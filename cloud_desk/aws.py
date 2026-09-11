import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError


def _client(service, connection):
    return boto3.client(
        service,
        aws_access_key_id=connection.access_key_id,
        aws_secret_access_key=connection.secret_access_key,
        region_name=connection.region,
    )


# =========================================================
# AWS READ / DASHBOARD DATA
# =========================================================

def get_ec2_instances(connection):
    try:
        ec2 = _client("ec2", connection)
        response = ec2.describe_instances()

        raw_instances = []
        image_ids = set()

        for reservation in response.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                name = next(
                    (
                        tag["Value"]
                        for tag in inst.get("Tags", [])
                        if tag.get("Key") == "Name"
                    ),
                    inst["InstanceId"],
                )
                image_id = inst.get("ImageId") or "-"
                if image_id != "-":
                    image_ids.add(image_id)

                platform = "Windows" if inst.get("Platform") == "windows" else "Linux"

                raw_instances.append({
                    "id": inst["InstanceId"],
                    "name": name,
                    "type": inst.get("InstanceType", "-"),
                    "state": inst.get("State", {}).get("Name", "unknown"),
                    "az": inst.get("Placement", {}).get("AvailabilityZone", "-"),
                    "private_ip": inst.get("PrivateIpAddress") or "-",
                    "public_ip": inst.get("PublicIpAddress") or "-",
                    "private_dns": inst.get("PrivateDnsName") or "-",
                    "public_dns": inst.get("PublicDnsName") or "-",
                    "image_id": image_id,
                    "platform": platform,
                    "key_name": inst.get("KeyName") or "-",
                })

        image_info = {}
        if image_ids:
            try:
                images = ec2.describe_images(ImageIds=sorted(image_ids)).get("Images", [])
                image_info = {image.get("ImageId"): image for image in images}
            except (ClientError, BotoCoreError):
                image_info = {}

        instances = []
        for inst in raw_instances:
            image = image_info.get(inst["image_id"], {})
            image_name = image.get("Name") or ""
            lower_image_name = image_name.lower()

            if inst["platform"] == "Windows":
                os_user = "Administrator"
            elif "ubuntu" in lower_image_name:
                os_user = "ubuntu"
            elif "debian" in lower_image_name:
                os_user = "admin"
            else:
                os_user = "ec2-user"

            inst["image_name"] = image_name or inst["image_id"]
            inst["os_user"] = os_user
            instances.append(inst)

        return {"ok": True, "data": instances}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def get_s3_buckets(connection):
    try:
        s3 = _client("s3", connection)
        response = s3.list_buckets()

        buckets = [
            {
                "name": bucket["Name"],
                "created": bucket["CreationDate"].strftime("%Y-%m-%d"),
            }
            for bucket in response.get("Buckets", [])
        ]

        return {"ok": True, "data": buckets}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def get_rds_instances(connection):
    try:
        rds = _client("rds", connection)
        response = rds.describe_db_instances()

        instances = [
            {
                "id": db["DBInstanceIdentifier"],
                "engine": db.get("Engine", "-"),
                "status": db.get("DBInstanceStatus", "unknown"),
                "class": db.get("DBInstanceClass", "-"),
            }
            for db in response.get("DBInstances", [])
        ]

        return {"ok": True, "data": instances}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def get_lambda_functions(connection):
    try:
        lambda_client = _client("lambda", connection)
        response = lambda_client.list_functions()

        functions = [
            {
                "name": fn["FunctionName"],
                "runtime": fn.get("Runtime", "-"),
                "memory": fn.get("MemorySize", "-"),
            }
            for fn in response.get("Functions", [])
        ]

        return {"ok": True, "data": functions}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def get_vpcs(connection):
    try:
        ec2 = _client("ec2", connection)
        response = ec2.describe_vpcs()

        vpcs = [
            {
                "id": vpc["VpcId"],
                "cidr": vpc["CidrBlock"],
                "state": vpc["State"],
                "is_default": vpc.get("IsDefault", False),
            }
            for vpc in response.get("Vpcs", [])
        ]

        return {"ok": True, "data": vpcs}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def get_iam_users(connection):
    try:
        iam = _client("iam", connection)
        response = iam.list_users()

        users = [
            {
                "name": user["UserName"],
                "created": user["CreateDate"].strftime("%Y-%m-%d"),
            }
            for user in response.get("Users", [])
        ]

        return {"ok": True, "data": users}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def get_cloudwatch_alarms(connection):
    try:
        cloudwatch = _client("cloudwatch", connection)
        response = cloudwatch.describe_alarms()

        alarms = [
            {
                "name": alarm["AlarmName"],
                "state": alarm["StateValue"],
                "metric": alarm.get("MetricName", "-"),
            }
            for alarm in response.get("MetricAlarms", [])
        ]

        return {"ok": True, "data": alarms}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def get_dashboard_summary(connection):
    return {
        "ec2": get_ec2_instances(connection),
        "s3": get_s3_buckets(connection),
        "rds": get_rds_instances(connection),
        "lambda": get_lambda_functions(connection),
        "vpc": get_vpcs(connection),
        "iam": get_iam_users(connection),
        "cloudwatch": get_cloudwatch_alarms(connection),
    }


# =========================================================
# EC2 INSTANCE LIFECYCLE
# =========================================================

def start_ec2_instance(connection, instance_id):
    try:
        ec2 = _client("ec2", connection)
        response = ec2.start_instances(
            InstanceIds=[instance_id],
        )

        state = (
            response.get("StartingInstances", [{}])[0]
            .get("CurrentState", {})
            .get("Name", "pending")
        )

        return {
            "ok": True,
            "state": state,
            "message": f"EC2 instance {instance_id} start requested.",
        }

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def stop_ec2_instance(connection, instance_id):
    try:
        ec2 = _client("ec2", connection)
        response = ec2.stop_instances(
            InstanceIds=[instance_id],
        )

        state = (
            response.get("StoppingInstances", [{}])[0]
            .get("CurrentState", {})
            .get("Name", "stopping")
        )

        return {
            "ok": True,
            "state": state,
            "message": f"EC2 instance {instance_id} stop requested.",
        }

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def reboot_ec2_instance(connection, instance_id):
    try:
        ec2 = _client("ec2", connection)

        ec2.reboot_instances(
            InstanceIds=[instance_id],
        )

        return {
            "ok": True,
            "message": f"EC2 instance {instance_id} reboot requested.",
        }

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def terminate_ec2_instance(connection, instance_id):
    try:
        ec2 = _client("ec2", connection)

        response = ec2.terminate_instances(
            InstanceIds=[instance_id],
        )

        state = (
            response.get("TerminatingInstances", [{}])[0]
            .get("CurrentState", {})
            .get("Name", "shutting-down")
        )

        return {
            "ok": True,
            "state": state,
            "message": (
                f"EC2 instance {instance_id} termination requested."
            ),
        }

    except ClientError as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# EC2 CREATE
# =========================================================

def get_ec2_regions(connection):
    try:
        ec2 = _client("ec2", connection)

        response = ec2.describe_regions(
            AllRegions=False,
        )

        regions = sorted(
            [
                item["RegionName"]
                for item in response.get("Regions", [])
                if item.get("RegionName")
            ]
        )

        return {
            "ok": True,
            "data": regions,
        }

    except (ClientError, NoCredentialsError) as e:
        return {
            "ok": False,
            "error": str(e),
            "data": [],
        }


def get_ec2_vpcs(connection):
    try:
        ec2 = _client("ec2", connection)
        response = ec2.describe_vpcs()

        data = [
            {
                "id": vpc["VpcId"],
                "cidr": vpc["CidrBlock"],
                "is_default": vpc.get("IsDefault", False),
            }
            for vpc in response.get("Vpcs", [])
        ]

        return {
            "ok": True,
            "data": data,
        }

    except (ClientError, NoCredentialsError) as e:
        return {
            "ok": False,
            "error": str(e),
            "data": [],
        }


def get_ec2_subnets(connection, vpc_id=None):
    try:
        ec2 = _client("ec2", connection)

        kwargs = {}

        if vpc_id:
            kwargs["Filters"] = [
                {
                    "Name": "vpc-id",
                    "Values": [vpc_id],
                }
            ]

        response = ec2.describe_subnets(**kwargs)

        data = [
            {
                "id": subnet["SubnetId"],
                "az": subnet.get("AvailabilityZone", "-"),
                "cidr": subnet.get("CidrBlock", "-"),
                "vpc_id": subnet.get("VpcId", "-"),
            }
            for subnet in response.get("Subnets", [])
        ]

        return {
            "ok": True,
            "data": data,
        }

    except (ClientError, NoCredentialsError) as e:
        return {
            "ok": False,
            "error": str(e),
            "data": [],
        }


def get_ec2_security_groups(connection, vpc_id=None):
    try:
        ec2 = _client("ec2", connection)

        kwargs = {}

        if vpc_id:
            kwargs["Filters"] = [
                {
                    "Name": "vpc-id",
                    "Values": [vpc_id],
                }
            ]

        response = ec2.describe_security_groups(**kwargs)

        data = [
            {
                "id": group["GroupId"],
                "name": group.get("GroupName", "-"),
                "description": group.get("Description", "-"),
                "vpc_id": group.get("VpcId", "-"),
            }
            for group in response.get("SecurityGroups", [])
        ]

        return {
            "ok": True,
            "data": data,
        }

    except (ClientError, NoCredentialsError) as e:
        return {
            "ok": False,
            "error": str(e),
            "data": [],
        }


def get_ec2_key_pairs(connection):
    try:
        ec2 = _client("ec2", connection)

        response = ec2.describe_key_pairs()

        data = [
            {
                "name": key.get("KeyName", "-"),
                "key_pair_id": key.get("KeyPairId", "-"),
            }
            for key in response.get("KeyPairs", [])
        ]

        return {
            "ok": True,
            "data": data,
        }

    except (ClientError, NoCredentialsError) as e:
        return {
            "ok": False,
            "error": str(e),
            "data": [],
        }


def get_ec2_ami_options(connection):
    """Return a small Quick Start catalog similar to the AWS EC2 launch wizard."""
    try:
        ec2 = _client("ec2", connection)

        options = []

        catalogs = [
            {
                "slug": "amazon-linux-2023",
                "label": "Amazon Linux 2023",
                "description": "AWS Linux image for general-purpose workloads.",
                "owner": "amazon",
                "filters": [
                    {"Name": "state", "Values": ["available"]},
                    {"Name": "name", "Values": ["al2023-ami-*-x86_64"]},
                    {"Name": "architecture", "Values": ["x86_64"]},
                    {"Name": "root-device-type", "Values": ["ebs"]},
                    {"Name": "virtualization-type", "Values": ["hvm"]},
                ],
            },
            {
                "slug": "ubuntu-24-04",
                "label": "Ubuntu 24.04 LTS",
                "description": "Canonical Ubuntu Server 24.04 LTS image.",
                "owner": "099720109477",
                "filters": [
                    {"Name": "state", "Values": ["available"]},
                    {"Name": "name", "Values": ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]},
                    {"Name": "architecture", "Values": ["x86_64"]},
                    {"Name": "root-device-type", "Values": ["ebs"]},
                    {"Name": "virtualization-type", "Values": ["hvm"]},
                ],
            },
        ]

        for catalog in catalogs:
            response = ec2.describe_images(
                Owners=[catalog["owner"]],
                Filters=catalog["filters"],
            )

            images = response.get("Images", [])
            images.sort(
                key=lambda image: image.get("CreationDate", ""),
                reverse=True,
            )

            if not images:
                continue

            image = images[0]
            options.append(
                {
                    "slug": catalog["slug"],
                    "label": catalog["label"],
                    "description": catalog["description"],
                    "image_id": image.get("ImageId", ""),
                    "name": image.get("Name", ""),
                    "creation_date": image.get("CreationDate", ""),
                    "architecture": image.get("Architecture", "x86_64"),
                }
            )

        return {"ok": True, "data": options}

    except (ClientError, NoCredentialsError) as e:
        return {"ok": False, "error": str(e), "data": []}


def create_ec2_instance(
    connection,
    image_id,
    instance_type="t3.micro",
    name="CloudDesk-EC2",
    subnet_id=None,
    security_group_ids=None,
    key_name=None,
    min_count=1,
    max_count=1,
    root_volume_size=8,
    root_volume_type="gp3",
    associate_public_ip=False,
):
    """
    Launch EC2 instances in the user's connected AWS account.

    Required:
        image_id

    Optional:
        instance_type
        name
        subnet_id
        security_group_ids
        key_name
    """

    try:
        image_id = str(image_id or "").strip()

        if not image_id:
            return {
                "ok": False,
                "error": "AMI Image ID is required.",
            }

        try:
            min_count = int(min_count)
            max_count = int(max_count)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "Instance count must be a valid number.",
            }

        if min_count < 1 or max_count < 1 or min_count > max_count:
            return {
                "ok": False,
                "error": "Invalid minimum/maximum instance count.",
            }

        ec2 = _client("ec2", connection)

        kwargs = {
            "ImageId": image_id,
            "InstanceType": instance_type,
            "MinCount": min_count,
            "MaxCount": max_count,
        }

        if subnet_id:
            kwargs["SubnetId"] = subnet_id

        if security_group_ids:
            kwargs["SecurityGroupIds"] = security_group_ids

        if key_name:
            kwargs["KeyName"] = key_name

        # Keep the launch experience close to the AWS console: create the
        # root EBS volume from the selected size/type and optionally request
        # a public IPv4 address.
        try:
            root_volume_size = int(root_volume_size)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "Root volume size must be a valid number.",
            }

        if root_volume_size < 8 or root_volume_size > 16384:
            return {
                "ok": False,
                "error": "Root volume size must be between 8 GiB and 16384 GiB.",
            }

        root_volume_type = str(root_volume_type or "gp3").strip()
        if root_volume_type not in {"gp3", "gp2", "io1", "io2", "st1", "sc1"}:
            return {
                "ok": False,
                "error": "Unsupported root volume type.",
            }

        kwargs["BlockDeviceMappings"] = [
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "VolumeSize": root_volume_size,
                    "VolumeType": root_volume_type,
                    "DeleteOnTermination": True,
                },
            }
        ]

        if associate_public_ip and subnet_id:
            kwargs["NetworkInterfaces"] = [
                {
                    "DeviceIndex": 0,
                    "SubnetId": subnet_id,
                    "AssociatePublicIpAddress": True,
                    **({"Groups": security_group_ids} if security_group_ids else {}),
                }
            ]
            # NetworkInterfaces already carries the subnet and security
            # groups, so those top-level parameters must not be duplicated.
            kwargs.pop("SubnetId", None)
            kwargs.pop("SecurityGroupIds", None)

        response = ec2.run_instances(**kwargs)

        instance_ids = [
            instance["InstanceId"]
            for instance in response.get("Instances", [])
        ]

        # Add a Name tag to each launched instance. If more than one
        # instance was requested, suffix the base name for easier
        # identification in CloudDesk/AWS.
        if name and instance_ids:
            for index, instance_id in enumerate(instance_ids, start=1):
                tag_value = name if len(instance_ids) == 1 else f"{name}-{index}"
                ec2.create_tags(
                    Resources=[instance_id],
                    Tags=[
                        {
                            "Key": "Name",
                            "Value": tag_value,
                        }
                    ],
                )

        return {
            "ok": True,
            "instance_ids": instance_ids,
            "message": (
                f"{len(instance_ids)} EC2 instance(s) launch requested."
            ),
        }

    except ClientError as e:
        return {
            "ok": False,
            "error": str(e),
        }


# =========================================================
# S3
# =========================================================

def create_s3_bucket(connection, bucket_name):
    try:
        bucket_name = str(bucket_name or "").strip()

        if not bucket_name:
            return {
                "ok": False,
                "error": "Bucket name is required.",
            }

        s3 = _client("s3", connection)

        if connection.region == "us-east-1":
            s3.create_bucket(
                Bucket=bucket_name,
            )
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": connection.region,
                },
            )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def delete_s3_bucket(connection, bucket_name):
    try:
        s3 = _client("s3", connection)

        # Current implementation deletes listed objects before deleting
        # the bucket. Additional pagination handling can be added later.
        objects = s3.list_objects_v2(
            Bucket=bucket_name,
        )

        contents = objects.get("Contents", [])

        if contents:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    "Objects": [
                        {"Key": obj["Key"]}
                        for obj in contents
                    ],
                },
            )

        s3.delete_bucket(
            Bucket=bucket_name,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# RDS
# =========================================================

def start_rds_instance(connection, db_id):
    try:
        rds = _client("rds", connection)

        rds.start_db_instance(
            DBInstanceIdentifier=db_id,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def stop_rds_instance(connection, db_id):
    try:
        rds = _client("rds", connection)

        rds.stop_db_instance(
            DBInstanceIdentifier=db_id,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def delete_rds_instance(connection, db_id):
    try:
        rds = _client("rds", connection)

        rds.delete_db_instance(
            DBInstanceIdentifier=db_id,
            SkipFinalSnapshot=True,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# LAMBDA
# =========================================================

def delete_lambda_function(connection, function_name):
    try:
        lambda_client = _client("lambda", connection)

        lambda_client.delete_function(
            FunctionName=function_name,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# VPC
# =========================================================

def create_vpc(connection, cidr_block):
    try:
        ec2 = _client("ec2", connection)

        response = ec2.create_vpc(
            CidrBlock=cidr_block,
        )

        return {
            "ok": True,
            "vpc_id": response.get("Vpc", {}).get("VpcId"),
        }

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def delete_vpc(connection, vpc_id):
    try:
        ec2 = _client("ec2", connection)

        ec2.delete_vpc(
            VpcId=vpc_id,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# IAM
# =========================================================

def create_iam_user(connection, username):
    try:
        iam = _client("iam", connection)

        iam.create_user(
            UserName=username,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


def delete_iam_user(connection, username):
    try:
        iam = _client("iam", connection)

        iam.delete_user(
            UserName=username,
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# CLOUDWATCH
# =========================================================

def delete_cloudwatch_alarm(connection, alarm_name):
    try:
        cloudwatch = _client("cloudwatch", connection)

        cloudwatch.delete_alarms(
            AlarmNames=[alarm_name],
        )

        return {"ok": True}

    except ClientError as e:
        return {"ok": False, "error": str(e)}
