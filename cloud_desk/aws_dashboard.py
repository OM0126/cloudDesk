from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import AWSConnection
from . import aws
from . import views


views.ACTION_MAP.setdefault(
    ("ec2", "reboot"),
    lambda conn, rid: aws.reboot_ec2_instance(conn, rid),
)


def _get_connection(request):
    return (
        AWSConnection.objects.filter(
            user=request.user,
            is_connected=True,
        )
        .order_by("-created_at")
        .first()
    )


@login_required
def aws_account_page(request):
    aws_connection = _get_connection(request)

    if not aws_connection:
        return redirect("dashboard")

    try:
        aws_summary = aws.get_dashboard_summary(aws_connection)
    except Exception as exc:
        aws_summary = {
            "error": str(exc),
            "ec2": {"ok": False, "data": [], "error": str(exc)},
            "s3": {"ok": False, "data": [], "error": str(exc)},
            "rds": {"ok": False, "data": [], "error": str(exc)},
            "lambda": {"ok": False, "data": [], "error": str(exc)},
            "vpc": {"ok": False, "data": [], "error": str(exc)},
            "iam": {"ok": False, "data": [], "error": str(exc)},
            "cloudwatch": {"ok": False, "data": [], "error": str(exc)},
        }

    return render(
        request,
        "aws_account.html",
        {
            "aws_connection": aws_connection,
            "aws_summary": aws_summary,
            "profile": {
                "name": request.user.get_full_name() or request.user.username,
                "username": request.user.username,
                "email": request.user.email,
            },
        },
    )


@login_required
def ec2_launch_page(request):
    aws_connection = _get_connection(request)

    if not aws_connection:
        messages.error(request, "No connected AWS account found.")
        return redirect("dashboard")

    ami_result = aws.get_ec2_ami_options(aws_connection)
    vpcs_result = aws.get_ec2_vpcs(aws_connection)
    subnets_result = aws.get_ec2_subnets(aws_connection)
    security_groups_result = aws.get_ec2_security_groups(aws_connection)
    key_pairs_result = aws.get_ec2_key_pairs(aws_connection)

    return render(
        request,
        "aws_ec2_launch.html",
        {
            "aws_connection": aws_connection,
            "ami_options": ami_result.get("data", []),
            "ec2_vpcs": vpcs_result.get("data", []),
            "ec2_subnets": subnets_result.get("data", []),
            "ec2_security_groups": security_groups_result.get("data", []),
            "ec2_key_pairs": key_pairs_result.get("data", []),
            "ami_error": ami_result.get("error"),
            "discovery_errors": [
                item.get("error")
                for item in (
                    vpcs_result,
                    subnets_result,
                    security_groups_result,
                    key_pairs_result,
                )
                if not item.get("ok") and item.get("error")
            ],
        },
    )


@login_required
@require_POST
def create_ec2(request):
    aws_connection = _get_connection(request)

    if not aws_connection:
        messages.error(request, "No connected AWS account found.")
        return redirect("dashboard")

    image_id = request.POST.get("image_id", "").strip()
    instance_type = request.POST.get("instance_type", "t3.micro").strip()
    name = request.POST.get("name", "CloudDesk-EC2").strip()
    subnet_id = request.POST.get("subnet_id", "").strip() or None
    key_name = request.POST.get("key_name", "").strip() or None
    volume_size_raw = request.POST.get("volume_size", "8").strip()
    volume_type = request.POST.get("volume_type", "gp3").strip()
    associate_public_ip = request.POST.get("associate_public_ip") == "on"
    instance_count_raw = request.POST.get("instance_count", "1").strip()

    security_group_ids = [
        value.strip()
        for value in request.POST.getlist("security_group_ids")
        if value.strip()
    ]

    if not image_id:
        messages.error(request, "Please select an operating system image.")
        return redirect("aws_ec2_launch")

    try:
        volume_size = int(volume_size_raw)
    except ValueError:
        messages.error(request, "Storage size must be a valid number.")
        return redirect("aws_ec2_launch")

    try:
        instance_count = int(instance_count_raw)
    except ValueError:
        messages.error(request, "Number of instances must be a valid whole number.")
        return redirect("aws_ec2_launch")

    if instance_count < 1 or instance_count > 20:
        messages.error(request, "Number of instances must be between 1 and 20.")
        return redirect("aws_ec2_launch")

    if volume_size < 8 or volume_size > 16384:
        messages.error(request, "Storage size must be between 8 GiB and 16384 GiB.")
        return redirect("aws_ec2_launch")

    result = aws.create_ec2_instance(
        aws_connection,
        image_id=image_id,
        instance_type=instance_type or "t3.micro",
        name=name or "CloudDesk-EC2",
        subnet_id=subnet_id,
        security_group_ids=security_group_ids or None,
        key_name=key_name,
        min_count=instance_count,
        max_count=instance_count,
        root_volume_size=volume_size,
        root_volume_type=volume_type,
        associate_public_ip=associate_public_ip,
    )

    if result.get("ok"):
        ids = ", ".join(result.get("instance_ids", []))
        messages.success(
            request,
            f"EC2 instance launch requested successfully. Instance: {ids}",
        )
        return redirect("aws_account")

    messages.error(
        request,
        result.get("error", "Could not launch the EC2 instance."),
    )
    return redirect("aws_ec2_launch")
