from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings

import boto3
import secrets
import time
import hashlib
import hmac

from .models import AWSConnection, GCPConnection
from . import aws
from . import gcp


ACTION_MAP = {
    ("ec2", "start"): lambda conn, rid: aws.start_ec2_instance(conn, rid),
    ("ec2", "stop"): lambda conn, rid: aws.stop_ec2_instance(conn, rid),
    ("ec2", "terminate"): lambda conn, rid: aws.terminate_ec2_instance(conn, rid),

    ("s3", "create"): lambda conn, rid: aws.create_s3_bucket(conn, rid),
    ("s3", "delete"): lambda conn, rid: aws.delete_s3_bucket(conn, rid),

    ("rds", "start"): lambda conn, rid: aws.start_rds_instance(conn, rid),
    ("rds", "stop"): lambda conn, rid: aws.stop_rds_instance(conn, rid),
    ("rds", "delete"): lambda conn, rid: aws.delete_rds_instance(conn, rid),

    ("lambda", "delete"): lambda conn, rid: aws.delete_lambda_function(conn, rid),

    ("vpc", "create"): lambda conn, rid: aws.create_vpc(conn, rid),
    ("vpc", "delete"): lambda conn, rid: aws.delete_vpc(conn, rid),

    ("iam", "create"): lambda conn, rid: aws.create_iam_user(conn, rid),
    ("iam", "delete"): lambda conn, rid: aws.delete_iam_user(conn, rid),

    ("cloudwatch", "delete"): lambda conn, rid: aws.delete_cloudwatch_alarm(
        conn, rid
    ),
}


ACTION_OTP_EXPIRY_SECONDS = 5 * 60
ACTION_OTP_MAX_ATTEMPTS = 5


def _otp_hash(otp):
    return hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256,
    ).hexdigest()


# =========================================================
# SIGN UP
# =========================================================

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username:
            messages.error(request, "Please enter a username.")
            return render(request, "signup.html")

        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, "signup.html")

        if not password:
            messages.error(request, "Please enter a password.")
            return render(request, "signup.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "signup.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(
                request,
                "An account with this email already exists.",
            )
            return render(request, "signup.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("dashboard")

    return render(request, "signup.html")


# =========================================================
# LOGIN
# =========================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(
                request,
                "Please enter your email and password.",
            )
            return render(request, "login.html")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html")

        authenticated_user = authenticate(
            request,
            username=user.username,
            password=password,
        )

        if authenticated_user is not None:
            login(request, authenticated_user)
            return redirect("dashboard")

        messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


# =========================================================
# LOGOUT
# =========================================================

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================================================
# AWS CONNECT
# =========================================================

@login_required
def aws_connect(request):
    if request.method == "POST":
        name = request.POST.get(
            "name",
            "My AWS Account",
        ).strip()

        access_key_id = request.POST.get(
            "access_key_id",
            "",
        ).strip()

        secret_access_key = request.POST.get(
            "secret_access_key",
            "",
        ).strip()

        region = request.POST.get(
            "region",
            "us-east-1",
        ).strip()

        if not access_key_id:
            messages.error(
                request,
                "AWS Access Key ID is required.",
            )
            return render(request, "aws_connect.html")

        if not secret_access_key:
            messages.error(
                request,
                "AWS Secret Access Key is required.",
            )
            return render(request, "aws_connect.html")

        try:
            session = boto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region,
            )

            sts = session.client("sts")
            identity = sts.get_caller_identity()
            account_id = identity.get("Account")

            existing = AWSConnection.objects.filter(
                user=request.user,
                account_id=account_id,
            ).first()

            if existing:
                existing.name = name or "My AWS Account"
                existing.access_key_id = access_key_id
                existing.secret_access_key = secret_access_key
                existing.region = region
                existing.is_connected = True
                existing.save()
            else:
                AWSConnection.objects.create(
                    user=request.user,
                    name=name or "My AWS Account",
                    access_key_id=access_key_id,
                    secret_access_key=secret_access_key,
                    region=region,
                    account_id=account_id,
                    is_connected=True,
                )

            messages.success(
                request,
                f"AWS connected successfully! Account: {account_id}",
            )
            return redirect("dashboard")

        except Exception as e:
            messages.error(
                request,
                f"AWS connection failed: {str(e)}",
            )
            return render(request, "aws_connect.html")

    return render(request, "aws_connect.html")


# =========================================================
# GCP CONNECT - SERVICE ACCOUNT JSON
# =========================================================

@login_required
def gcp_connect(request):
    """Connect a user's GCP project using a service-account JSON key."""

    if request.method == "GET":
        return render(request, "gcp_connect.html")

    if request.method != "POST":
        return render(request, "gcp_connect.html")

    name = request.POST.get(
        "name",
        "My GCP Account",
    ).strip() or "My GCP Account"

    project_id = request.POST.get(
        "project_id",
        "",
    ).strip()

    credentials_file = request.FILES.get("credentials_file")

    if not project_id:
        messages.error(request, "GCP Project ID is required.")
        return render(request, "gcp_connect.html")

    if not credentials_file:
        messages.error(request, "Please upload the service-account JSON file.")
        return render(request, "gcp_connect.html")

    if not credentials_file.name.lower().endswith(".json"):
        messages.error(request, "Please upload a .json service-account key file.")
        return render(request, "gcp_connect.html")

    try:
        import json
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        raw = credentials_file.read()

        if len(raw) > 100 * 1024:
            raise ValueError("Credential file is too large.")

        try:
            key_info = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("The uploaded file is not valid JSON.") from exc

        # Google recommends validating externally sourced credential configs.
        if key_info.get("type") != "service_account":
            raise ValueError(
                "The JSON file is not a Google Cloud service-account key."
            )

        json_project_id = str(key_info.get("project_id", "")).strip()
        service_account_email = str(key_info.get("client_email", "")).strip()

        if not json_project_id:
            raise ValueError(
                "The service-account JSON does not contain a project_id."
            )

        if not service_account_email:
            raise ValueError(
                "The service-account JSON does not contain client_email."
            )

        # The project in the uploaded key should match the project
        # the user says they want CloudDesk to manage.
        if json_project_id != project_id:
            raise ValueError(
                "Project ID does not match the project_id in the JSON credential."
            )

        credentials = service_account.Credentials.from_service_account_info(
            key_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Test actual access to the requested project.
        resource_manager = build(
            "cloudresourcemanager",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

        project = (
            resource_manager
            .projects()
            .get(projectId=project_id)
            .execute()
        )

        verified_project_id = project.get("projectId")
        verified_project_name = project.get("name")

        if verified_project_id != project_id:
            raise ValueError(
                "Google Cloud returned a different project ID."
            )

        # Upsert the user's GCP connection.
        existing = GCPConnection.objects.filter(
            user=request.user,
            project_id=project_id,
        ).first()

        json_text = json.dumps(key_info)

        if existing:
            existing.name = name
            existing.project_name = verified_project_name or project_id
            existing.service_account_email = service_account_email
            existing.credentials_json = json_text
            existing.is_connected = True
            existing.save()
        else:
            existing = GCPConnection.objects.create(
                user=request.user,
                name=name,
                project_id=project_id,
                project_name=verified_project_name or project_id,
                service_account_email=service_account_email,
                credentials_json=json_text,
                is_connected=True,
            )

        messages.success(
            request,
            f"GCP connected successfully! Project: {project_id}",
        )
        return redirect("dashboard")

    except Exception as e:
        messages.error(
            request,
            f"GCP connection failed: {str(e)}",
        )
        return render(request, "gcp_connect.html")


# =========================================================
# DISCONNECT AWS / GCP
# =========================================================

@login_required
@require_POST
def disconnect_aws(request):
    connection_id = request.POST.get("connection_id", "").strip()

    if not connection_id:
        messages.error(request, "AWS connection ID is required.")
        return redirect("dashboard")

    connection = AWSConnection.objects.filter(
        id=connection_id,
        user=request.user,
        is_connected=True,
    ).first()

    if not connection:
        messages.error(request, "AWS connection was not found.")
        return redirect("dashboard")

    account_id = connection.account_id or "your AWS account"
    connection.delete()

    messages.success(
        request,
        f"AWS disconnected successfully from CloudDesk: {account_id}.",
    )
    return redirect("dashboard")


@login_required
@require_POST
def disconnect_gcp(request):
    connection_id = request.POST.get("connection_id", "").strip()

    if not connection_id:
        messages.error(request, "GCP connection ID is required.")
        return redirect("dashboard")

    connection = GCPConnection.objects.filter(
        id=connection_id,
        user=request.user,
        is_connected=True,
    ).first()

    if not connection:
        messages.error(request, "GCP connection was not found.")
        return redirect("dashboard")

    project_id = connection.project_id or "your GCP project"
    connection.delete()

    messages.success(
        request,
        f"GCP disconnected successfully from CloudDesk: {project_id}.",
    )
    return redirect("dashboard")


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):
    # =====================================================
    # AWS CONNECTION
    # =====================================================

    aws_connection = AWSConnection.objects.filter(
        user=request.user,
        is_connected=True,
    ).order_by("-created_at").first()

    aws_count = AWSConnection.objects.filter(
        user=request.user,
        is_connected=True,
    ).count()

    # =====================================================
    # GCP CONNECTION
    # =====================================================

    gcp_connection = GCPConnection.objects.filter(
        user=request.user,
        is_connected=True,
    ).order_by("-created_at").first()

    gcp_count = GCPConnection.objects.filter(
        user=request.user,
        is_connected=True,
    ).count()

    # =====================================================
    # PROFILE
    # =====================================================

    profile = {
        "name": (
            request.user.get_full_name()
            or request.user.username
        ),
        "username": request.user.username,
        "email": request.user.email,
    }

    # =====================================================
    # CLOUD ACCOUNT COUNTS
    # =====================================================

    cloud_accounts = {
        "aws": aws_count,
        "gcp": gcp_count,
    }

    total_cloud_accounts = aws_count + gcp_count

    # =====================================================
    # ALERTS
    # =====================================================

    alerts = []

    if not aws_connection:
        alerts.append({
            "type": "warning",
            "title": "AWS not connected",
            "message": (
                "Connect an AWS account to start managing your cloud."
            ),
        })

    if not gcp_connection:
        alerts.append({
            "type": "warning",
            "title": "GCP not connected",
            "message": (
                "Connect a GCP project to start managing your GCP resources."
            ),
        })

    # =====================================================
    # AWS SUMMARY
    # =====================================================

    aws_summary = None

    if aws_connection:
        try:
            aws_summary = aws.get_dashboard_summary(
                aws_connection
            )
        except Exception as e:
            aws_summary = {
                "error": str(e),
            }

    # =====================================================
    # GCP SUMMARY
    # =====================================================

    gcp_summary = None

    if gcp_connection:
        try:
            gcp_summary = gcp.get_dashboard_summary(
                gcp_connection
            )
        except Exception as e:
            error = str(e)
            gcp_summary = {
                "compute": {
                    "ok": False,
                    "data": [],
                    "error": error,
                },
                "storage": {
                    "ok": False,
                    "data": [],
                    "error": error,
                },
                "sql": {
                    "ok": False,
                    "data": [],
                    "error": error,
                },
                "functions": {
                    "ok": False,
                    "data": [],
                    "error": error,
                },
                "vpc": {
                    "ok": False,
                    "data": [],
                    "error": error,
                },
                "iam": {
                    "ok": False,
                    "data": [],
                    "error": error,
                },
                "monitoring": {
                    "ok": False,
                    "data": [],
                    "error": error,
                },
            }

    # =====================================================
    # RENDER DASHBOARD
    # =====================================================

    return render(
        request,
        "dashboard.html",
        {
            "aws_connection": aws_connection,
            "gcp_connection": gcp_connection,
            "aws_summary": aws_summary,
            "gcp_summary": gcp_summary,
            "profile": profile,
            "cloud_accounts": cloud_accounts,
            "total_cloud_accounts": total_cloud_accounts,
            "alerts": alerts,
        },
    )


# =========================================================
# COMPLETE GOOGLE PROFILE
# =========================================================

@login_required
def complete_profile(request):
    user = request.user

    if not request.session.get(
        "google_new_user",
        False,
    ):
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get(
            "username",
            "",
        ).strip()

        if not username:
            messages.error(
                request,
                "Please choose a username.",
            )
            return render(
                request,
                "account/complete_profile.html",
                {
                    "email": user.email,
                    "name": user.get_full_name(),
                },
            )

        if len(username) < 3:
            messages.error(
                request,
                "Username must be at least 3 characters.",
            )
            return render(
                request,
                "account/complete_profile.html",
                {
                    "email": user.email,
                    "name": user.get_full_name(),
                },
            )

        if User.objects.filter(
            username__iexact=username,
        ).exclude(
            pk=user.pk,
        ).exists():
            messages.error(
                request,
                "That username is already taken.",
            )
            return render(
                request,
                "account/complete_profile.html",
                {
                    "email": user.email,
                    "name": user.get_full_name(),
                },
            )

        user.username = username
        user.save(update_fields=["username"])

        request.session.pop("google_new_user", None)
        request.session.modified = True

        messages.success(
            request,
            "Your CloudDesk account has been created successfully!",
        )

        return redirect("dashboard")

    return render(
        request,
        "account/complete_profile.html",
        {
            "email": user.email,
            "name": user.get_full_name(),
        },
    )


# =========================================================
# SEND ACTION OTP
# =========================================================

@login_required
@require_POST
def send_action_otp(request):
    service = request.POST.get(
        "service",
        "",
    ).strip().lower()

    action = request.POST.get(
        "action",
        "",
    ).strip().lower()

    resource_id = request.POST.get(
        "resource_id",
        "",
    ).strip()

    if not request.user.email:
        return JsonResponse(
            {
                "ok": False,
                "error": "Your account does not have an email address.",
            },
            status=400,
        )

    if not resource_id:
        return JsonResponse(
            {
                "ok": False,
                "error": "Resource identifier required.",
            },
            status=400,
        )

    if (service, action) not in ACTION_MAP:
        return JsonResponse(
            {
                "ok": False,
                "error": "Unsupported action.",
            },
            status=400,
        )

    connection = AWSConnection.objects.filter(
        user=request.user,
        is_connected=True,
    ).first()

    if not connection:
        return JsonResponse(
            {
                "ok": False,
                "error": "No AWS account connected.",
            },
            status=400,
        )

    otp = f"{secrets.randbelow(1_000_000):06d}"

    request.session["aws_action_otp"] = {
        "otp_hash": _otp_hash(otp),
        "expires_at": time.time() + ACTION_OTP_EXPIRY_SECONDS,
        "attempts": 0,
        "service": service,
        "action": action,
        "resource_id": resource_id,
    }
    request.session.modified = True

    try:
        send_mail(
            subject="CloudDesk AWS Action Verification Code",
            message=(
                f"Your CloudDesk verification code is: {otp}\n\n"
                f"Action: {action.upper()}\n"
                f"Service: {service.upper()}\n\n"
                "This code expires in 5 minutes.\n"
                "If you did not request this action, "
                "you can safely ignore this email."
            ),
            from_email=getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                None,
            ),
            recipient_list=[request.user.email],
            fail_silently=False,
        )
    except Exception:
        request.session.pop("aws_action_otp", None)
        request.session.modified = True

        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "We could not send the verification email. "
                    "Please check your email settings."
                ),
            },
            status=500,
        )

    return JsonResponse(
        {
            "ok": True,
            "message": (
                f"OTP sent to {request.user.email}. "
                "Enter the 6-digit code to continue."
            ),
        }
    )


# =========================================================
# VERIFY ACTION OTP + EXECUTE AWS ACTION
# =========================================================

@login_required
@require_POST
def verify_action_otp(request):
    otp = request.POST.get(
        "otp",
        "",
    ).strip()

    if not otp:
        return JsonResponse(
            {
                "ok": False,
                "error": "OTP is required.",
            },
            status=400,
        )

    if not otp.isdigit() or len(otp) != 6:
        return JsonResponse(
            {
                "ok": False,
                "error": "Enter the 6-digit OTP.",
            },
            status=400,
        )

    otp_data = request.session.get(
        "aws_action_otp"
    )

    if not otp_data:
        return JsonResponse(
            {
                "ok": False,
                "error": "No active OTP. Please request a new OTP.",
            },
            status=400,
        )

    if time.time() > otp_data.get(
        "expires_at",
        0,
    ):
        request.session.pop(
            "aws_action_otp",
            None,
        )
        request.session.modified = True

        return JsonResponse(
            {
                "ok": False,
                "error": "OTP has expired. Please request a new OTP.",
            },
            status=400,
        )

    attempts = otp_data.get(
        "attempts",
        0,
    )

    if attempts >= ACTION_OTP_MAX_ATTEMPTS:
        request.session.pop(
            "aws_action_otp",
            None,
        )
        request.session.modified = True

        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Too many incorrect attempts. "
                    "Please request a new OTP."
                ),
            },
            status=403,
        )

    if not hmac.compare_digest(
        otp_data.get("otp_hash", ""),
        _otp_hash(otp),
    ):
        otp_data["attempts"] = attempts + 1
        request.session["aws_action_otp"] = otp_data
        request.session.modified = True

        remaining = ACTION_OTP_MAX_ATTEMPTS - attempts - 1

        return JsonResponse(
            {
                "ok": False,
                "error": (
                    f"Incorrect OTP. "
                    f"{remaining} attempt(s) remaining."
                ),
            },
            status=403,
        )

    service = otp_data["service"]
    action = otp_data["action"]
    resource_id = otp_data["resource_id"]

    connection = AWSConnection.objects.filter(
        user=request.user,
        is_connected=True,
    ).first()

    if not connection:
        request.session.pop(
            "aws_action_otp",
            None,
        )
        request.session.modified = True

        return JsonResponse(
            {
                "ok": False,
                "error": "No AWS account connected.",
            },
            status=400,
        )

    handler = ACTION_MAP.get(
        (service, action)
    )

    if not handler:
        request.session.pop(
            "aws_action_otp",
            None,
        )
        request.session.modified = True

        return JsonResponse(
            {
                "ok": False,
                "error": "Unsupported action.",
            },
            status=400,
        )

    try:
        result = handler(
            connection,
            resource_id,
        )
    except Exception as e:
        result = {
            "ok": False,
            "error": str(e),
        }

    # OTP is single-use.
    request.session.pop(
        "aws_action_otp",
        None,
    )
    request.session.modified = True

    if result.get("ok"):
        return JsonResponse(
            {
                "ok": True,
                "message": (
                    f"{action.capitalize()} succeeded."
                ),
            }
        )

    return JsonResponse(
        {
            "ok": False,
            "error": result.get(
                "error",
                "Action failed.",
            ),
        },
        status=500,
    )
