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


def create_ec2_key_pair(connection, key_name, key_type="rsa"):
    """Create an EC2 key pair and return the private key material once."""
    try:
        ec2 = _client("ec2", connection)
        key_name = str(key_name or "").strip()
        key_type = str(key_type or "rsa").strip().lower()

        if not key_name:
            return {
                "ok": False,
                "error": "Key pair name is required.",
            }

        if len(key_name) > 255:
            return {
                "ok": False,
                "error": "Key pair name must be 255 characters or fewer.",
            }

        if key_type not in {"rsa", "ed25519"}:
            return {
                "ok": False,
                "error": "Key type must be RSA or ED25519.",
            }

        response = ec2.create_key_pair(
            KeyName=key_name,
            KeyType=key_type,
            KeyFormat="pem",
        )

        return {
            "ok": True,
            "name": response.get("KeyName", key_name),
            "key_pair_id": response.get("KeyPairId", "-"),
            "fingerprint": response.get("KeyFingerprint", "-"),
            "key_material": response.get("KeyMaterial", ""),
        }

    except (ClientError, NoCredentialsError, BotoCoreError) as e:
        return {
            "ok": False,
            "error": str(e),
        }


def get_ec2_ami_options(connection):
    """Return a small Quick Start catalog of common AWS operating systems."""
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
            {
                "slug": "windows-server",
                "label": "Windows Server",
                "description": "Latest available Amazon Windows Server AMI for this Region.",
                "owner": "amazon",
                "filters": [
                    {"Name": "state", "Values": ["available"]},
                    {"Name": "platform", "Values": ["windows"]},
                    {"Name": "root-device-type", "Values": ["ebs"]},
                    {"Name": "architecture", "Values": ["x86_64"]},
                    {"Name": "virtualization-type", "Values": ["hvm"]},
                ],
            },
            {
                "slug": "macos",
                "label": "macOS",
                "description": "AWS macOS image. Mac EC2 instances require a Dedicated Host.",
                "owner": "amazon",
                "filters": [
                    {"Name": "state", "Values": ["available"]},
                    {"Name": "name", "Values": ["amzn-ec2-macos-15*"]},
                    {"Name": "root-device-type", "Values": ["ebs"]},
                    {"Name": "virtualization-type", "Values": ["hvm"]},
                ],
            },
        ]

        # macOS 15 is the preferred current macOS Quick Start target.
        # Fall back to macOS 14 if the Region has no Sequoia AMI.
        for catalog in catalogs:
            active_catalog = catalog
            if catalog["slug"] == "macos":
                image_sets = [
                    catalog["filters"],
                    [
                        {"Name": "state", "Values": ["available"]},
                        {"Name": "name", "Values": ["amzn-ec2-macos-14*"]},
                        {"Name": "root-device-type", "Values": ["ebs"]},
                        {"Name": "virtualization-type", "Values": ["hvm"]},
                    ],
                    [
                        {"Name": "state", "Values": ["available"]},
                        {"Name": "name", "Values": ["amzn-ec2-macos-13*"]},
                        {"Name": "root-device-type", "Values": ["ebs"]},
                        {"Name": "virtualization-type", "Values": ["hvm"]},
                    ],
                ]
            else:
                image_sets = [catalog["filters"]]

            image = None
            for filters in image_sets:
                response = ec2.describe_images(
                    Owners=[active_catalog["owner"]],
                    Filters=filters,
                )
                images = response.get("Images", [])
                images.sort(
                    key=lambda item: item.get("CreationDate", ""),
                    reverse=True,
                )
                if images:
                    image = images[0]
                    break

            if not image:
                continue

            options.append(
                {
                    "slug": active_catalog["slug"],
                    "label": active_catalog["label"],
                    "description": active_catalog["description"],
                    "image_id": image.get("ImageId", ""),
                    "name": image.get("Name", ""),
                    "creation_date": image.get("CreationDate", ""),
                    "architecture": image.get("Architecture", "x86_64"),
                    "platform": image.get("Platform", "") or "linux",
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
    root_device_name="/dev/xvda",
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

        root_device_name = str(root_device_name or "/dev/xvda").strip()
        if root_device_name not in {"/dev/xvda", "/dev/sda1"}:
            return {
                "ok": False,
                "error": "Unsupported root device name.",
            }

        kwargs["BlockDeviceMappings"] = [
            {
                "DeviceName": root_device_name,
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

# =========================================================
# S3 CREATE
# =========================================================

def create_s3_bucket(connection, bucket_name):
    try:
        bucket_name = str(bucket_name or "").strip().lower()

        if not bucket_name:
            return {"ok": False, "error": "Bucket name is required."}

        if len(bucket_name) < 3 or len(bucket_name) > 63:
            return {
                "ok": False,
                "error": "Bucket name must be between 3 and 63 characters.",
            }

        import re
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*[a-z0-9]", bucket_name):
            return {
                "ok": False,
                "error": "Bucket name can contain lowercase letters, numbers, dots and hyphens and must start and end with a letter or number.",
            }

        if ".." in bucket_name or ".-" in bucket_name or "-." in bucket_name:
            return {
                "ok": False,
                "error": "Bucket name cannot contain consecutive dots or dot-hyphen combinations.",
            }

        s3 = _client("s3", connection)

        if connection.region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": connection.region,
                },
            )

        return {"ok": True, "name": bucket_name}

    except (ClientError, NoCredentialsError, BotoCoreError) as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# RDS CREATE
# =========================================================

def create_rds_instance(
    connection,
    db_identifier,
    engine,
    instance_class,
    allocated_storage,
    master_username,
    master_password,
    db_name=None,
    publicly_accessible=False,
):
    try:
        rds = _client("rds", connection)

        db_identifier = str(db_identifier or "").strip().lower()
        engine = str(engine or "").strip().lower()
        instance_class = str(instance_class or "db.t3.micro").strip()
        master_username = str(master_username or "").strip()
        master_password = str(master_password or "")
        db_name = str(db_name or "").strip() or None

        if not db_identifier:
            return {"ok": False, "error": "DB instance identifier is required."}

        if engine not in {"mysql", "postgres"}:
            return {"ok": False, "error": "Supported engines are MySQL and PostgreSQL."}

        try:
            allocated_storage = int(allocated_storage)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Allocated storage must be a whole number."}

        if allocated_storage < 20 or allocated_storage > 65536:
            return {"ok": False, "error": "Allocated storage must be between 20 GiB and 65536 GiB."}

        if not master_username:
            return {"ok": False, "error": "Master username is required."}

        if len(master_password) < 8 or len(master_password) > 41:
            return {"ok": False, "error": "Master password must be between 8 and 41 characters."}

        params = {
            "DBInstanceIdentifier": db_identifier,
            "DBInstanceClass": instance_class,
            "Engine": engine,
            "AllocatedStorage": allocated_storage,
            "MasterUsername": master_username,
            "MasterUserPassword": master_password,
            "BackupRetentionPeriod": 0,
            "PubliclyAccessible": bool(publicly_accessible),
            "MultiAZ": False,
            "AutoMinorVersionUpgrade": True,
            "DeletionProtection": False,
        }

        if db_name:
            params["DBName"] = db_name

        response = rds.create_db_instance(**params)
        db = response.get("DBInstance", {})

        return {
            "ok": True,
            "id": db.get("DBInstanceIdentifier", db_identifier),
            "status": db.get("DBInstanceStatus", "creating"),
        }

    except (ClientError, NoCredentialsError, BotoCoreError) as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# LAMBDA CREATE
# =========================================================

def create_lambda_function(
    connection,
    function_name,
    runtime,
    handler,
    role_arn,
    source_code,
    memory_size=128,
    timeout=10,
):
    try:
        import io
        import zipfile

        lambda_client = _client("lambda", connection)

        function_name = str(function_name or "").strip()
        runtime = str(runtime or "python3.12").strip()
        handler = str(handler or "lambda_function.lambda_handler").strip()
        role_arn = str(role_arn or "").strip()
        source_code = str(source_code or "").strip()

        allowed_runtimes = {
            "python3.12",
            "python3.11",
            "python3.10",
            "nodejs22.x",
            "nodejs20.x",
        }

        if not function_name:
            return {"ok": False, "error": "Function name is required."}
        if runtime not in allowed_runtimes:
            return {"ok": False, "error": "Unsupported Lambda runtime selected."}
        if not role_arn:
            return {"ok": False, "error": "Lambda execution role ARN is required."}
        if not source_code:
            return {"ok": False, "error": "Function source code is required."}

        try:
            memory_size = int(memory_size)
            timeout = int(timeout)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Memory and timeout must be whole numbers."}

        if memory_size < 128 or memory_size > 10240:
            return {"ok": False, "error": "Memory must be between 128 MB and 10240 MB."}
        if timeout < 1 or timeout > 900:
            return {"ok": False, "error": "Timeout must be between 1 and 900 seconds."}

        filename = "lambda_function.py" if runtime.startswith("python") else "index.js"
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(filename, source_code)
        buffer.seek(0)

        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": buffer.read()},
            Description="Created from CloudDesk",
            Timeout=timeout,
            MemorySize=memory_size,
            Publish=True,
        )

        return {
            "ok": True,
            "name": response.get("FunctionName", function_name),
            "arn": response.get("FunctionArn", ""),
            "state": response.get("State", "Pending"),
        }

    except (ClientError, NoCredentialsError, BotoCoreError) as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# VPC CREATE
# =========================================================

def create_vpc(connection, cidr_block, name=None):
    try:
        ec2 = _client("ec2", connection)

        cidr_block = str(cidr_block or "").strip()
        name = str(name or "").strip()

        if not cidr_block:
            return {"ok": False, "error": "VPC CIDR block is required."}

        kwargs = {"CidrBlock": cidr_block}
        if name:
            kwargs["TagSpecifications"] = [
                {
                    "ResourceType": "vpc",
                    "Tags": [{"Key": "Name", "Value": name}],
                }
            ]

        response = ec2.create_vpc(**kwargs)
        vpc = response.get("Vpc", {})

        return {
            "ok": True,
            "vpc_id": vpc.get("VpcId"),
            "state": vpc.get("State", "pending"),
        }

    except (ClientError, NoCredentialsError, BotoCoreError) as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# IAM CREATE
# =========================================================

def create_iam_user(connection, username):
    try:
        iam = _client("iam", connection)
        username = str(username or "").strip()

        if not username:
            return {"ok": False, "error": "IAM username is required."}

        response = iam.create_user(UserName=username)
        user = response.get("User", {})

        return {
            "ok": True,
            "name": user.get("UserName", username),
            "arn": user.get("Arn", ""),
        }

    except (ClientError, NoCredentialsError, BotoCoreError) as e:
        return {"ok": False, "error": str(e)}


# =========================================================
# CLOUDWATCH CREATE
# =========================================================

def create_cloudwatch_alarm(
    connection,
    alarm_name,
    namespace,
    metric_name,
    threshold,
    comparison_operator,
    period=300,
    evaluation_periods=1,
    statistic="Average",
    instance_id=None,
    description=None,
):
    try:
        cloudwatch = _client("cloudwatch", connection)

        alarm_name = str(alarm_name or "").strip()
        namespace = str(namespace or "").strip()
        metric_name = str(metric_name or "").strip()
        comparison_operator = str(comparison_operator or "GreaterThanOrEqualToThreshold").strip()
        statistic = str(statistic or "Average").strip()

        if not alarm_name:
            return {"ok": False, "error": "Alarm name is required."}
        if not namespace:
            return {"ok": False, "error": "Metric namespace is required."}
        if not metric_name:
            return {"ok": False, "error": "Metric name is required."}

        try:
            threshold = float(threshold)
            period = int(period)
            evaluation_periods = int(evaluation_periods)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Threshold, period and evaluation periods must be valid numbers."}

        allowed_operators = {
            "GreaterThanOrEqualToThreshold",
            "GreaterThanThreshold",
            "LessThanThreshold",
            "LessThanOrEqualToThreshold",
        }
        allowed_statistics = {"Average", "Minimum", "Maximum", "Sum", "SampleCount"}

        if comparison_operator not in allowed_operators:
            return {"ok": False, "error": "Unsupported comparison operator."}
        if statistic not in allowed_statistics:
            return {"ok": False, "error": "Unsupported statistic."}
        if period not in {10, 30, 60, 300, 600, 900, 1800, 3600}:
            return {"ok": False, "error": "Unsupported CloudWatch period."}
        if evaluation_periods < 1 or evaluation_periods > 10:
            return {"ok": False, "error": "Evaluation periods must be between 1 and 10."}

        dimensions = []
        if instance_id:
            dimensions.append({"Name": "InstanceId", "Value": str(instance_id).strip()})

        params = {
            "AlarmName": alarm_name,
            "AlarmDescription": str(description or "Created from CloudDesk").strip(),
            "Namespace": namespace,
            "MetricName": metric_name,
            "Dimensions": dimensions,
            "Statistic": statistic,
            "Period": period,
            "EvaluationPeriods": evaluation_periods,
            "Threshold": threshold,
            "ComparisonOperator": comparison_operator,
            "TreatMissingData": "notBreaching",
        }

        cloudwatch.put_metric_alarm(**params)

        return {"ok": True, "name": alarm_name}

    except (ClientError, NoCredentialsError, BotoCoreError) as e:
        return {"ok": False, "error": str(e)}
