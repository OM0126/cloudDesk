import json

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def get_credentials(connection):
    if not connection.credentials_json:
        raise ValueError(
            "GCP credentials are not stored. Please reconnect the GCP project."
        )

    credentials_data = json.loads(connection.credentials_json)

    credentials = service_account.Credentials.from_service_account_info(
        credentials_data,
        scopes=SCOPES,
    )

    return credentials


def get_service(api_name, api_version, credentials):
    return build(
        api_name,
        api_version,
        credentials=credentials,
        cache_discovery=False,
    )


def get_compute_instances(project_id, credentials):
    try:
        service = get_service(
            "compute",
            "v1",
            credentials,
        )

        result = service.instances().aggregatedList(
            project=project_id
        ).execute()

        data = []

        for zone_data in result.get("items", {}).values():
            for instance in zone_data.get("instances", []):
                data.append(
                    {
                        "name": instance.get("name", "-"),
                        "zone": instance.get("zone", "").split("/")[-1],
                        "status": instance.get("status", "UNKNOWN"),
                    }
                )

        return {
            "ok": True,
            "data": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "data": [],
            "error": str(e),
        }


def get_storage_buckets(project_id, credentials):
    try:
        service = get_service(
            "storage",
            "v1",
            credentials,
        )

        result = service.buckets().list(
            project=project_id
        ).execute()

        data = []

        for bucket in result.get("items", []):
            data.append(
                {
                    "name": bucket.get("name", "-"),
                    "location": bucket.get("location", "-"),
                }
            )

        return {
            "ok": True,
            "data": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "data": [],
            "error": str(e),
        }


def get_cloud_sql(project_id, credentials):
    try:
        service = get_service(
            "sqladmin",
            "v1",
            credentials,
        )

        result = service.instances().list(
            project=project_id
        ).execute()

        data = []

        for instance in result.get("items", []):
            data.append(
                {
                    "name": instance.get("name", "-"),
                    "state": instance.get("state", "UNKNOWN"),
                }
            )

        return {
            "ok": True,
            "data": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "data": [],
            "error": str(e),
        }


def get_cloud_functions(project_id, credentials):
    try:
        service = get_service(
            "cloudfunctions",
            "v2",
            credentials,
        )

        result = service.projects().locations().functions().list(
            parent=f"projects/{project_id}/locations/-"
        ).execute()

        data = []

        for function in result.get("functions", []):
            name = function.get("name", "").split("/")[-1]

            state = function.get(
                "state",
                function.get("buildConfig", {}).get(
                    "runtime",
                    "UNKNOWN",
                ),
            )

            data.append(
                {
                    "name": name,
                    "state": state,
                }
            )

        return {
            "ok": True,
            "data": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "data": [],
            "error": str(e),
        }


def get_vpc_networks(project_id, credentials):
    try:
        service = get_service(
            "compute",
            "v1",
            credentials,
        )

        result = service.networks().list(
            project=project_id
        ).execute()

        data = []

        for network in result.get("items", []):
            data.append(
                {
                    "name": network.get("name", "-"),
                    "cidr": network.get(
                        "IPv4Range",
                        network.get(
                            "autoCreateSubnetworks",
                            "-"
                        ),
                    ),
                }
            )

        return {
            "ok": True,
            "data": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "data": [],
            "error": str(e),
        }


def get_iam_service_accounts(project_id, credentials):
    try:
        service = get_service(
            "iam",
            "v1",
            credentials,
        )

        result = service.projects().serviceAccounts().list(
            name=f"projects/{project_id}"
        ).execute()

        data = []

        for account in result.get("accounts", []):
            data.append(
                {
                    "name": account.get("displayName")
                    or account.get("name", "").split("/")[-1],
                    "email": account.get("email", "-"),
                }
            )

        return {
            "ok": True,
            "data": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "data": [],
            "error": str(e),
        }


def get_monitoring_alerts(project_id, credentials):
    try:
        service = get_service(
            "monitoring",
            "v3",
            credentials,
        )

        result = service.projects().alertPolicies().list(
            name=f"projects/{project_id}"
        ).execute()

        data = []

        for policy in result.get("alertPolicies", []):
            data.append(
                {
                    "name": policy.get("displayName", "-"),
                    "state": policy.get(
                        "enabled",
                        True,
                    )
                    and "enabled"
                    or "disabled",
                }
            )

        return {
            "ok": True,
            "data": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "data": [],
            "error": str(e),
        }


def get_dashboard_summary(connection):
    credentials = get_credentials(connection)
    project_id = connection.project_id

    return {
        "compute": get_compute_instances(
            project_id,
            credentials,
        ),

        "storage": get_storage_buckets(
            project_id,
            credentials,
        ),

        "sql": get_cloud_sql(
            project_id,
            credentials,
        ),

        "functions": get_cloud_functions(
            project_id,
            credentials,
        ),

        "vpc": get_vpc_networks(
            project_id,
            credentials,
        ),

        "iam": get_iam_service_accounts(
            project_id,
            credentials,
        ),

        "monitoring": get_monitoring_alerts(
            project_id,
            credentials,
        ),
    }
