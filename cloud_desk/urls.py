from django.urls import path
from . import views
from .aws_dashboard import (
    aws_account_page,
    ec2_launch_page,
    create_ec2,
    create_ec2_key_pair,
)


urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("complete-profile/", views.complete_profile, name="complete_profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cloud-accounts/", views.cloud_accounts, name="cloud_accounts"),
    path("logout/", views.logout_view, name="logout"),

    
    path("aws/account/", aws_account_page, name="aws_account"),
    path("aws/create/ec2/", ec2_launch_page, name="aws_ec2_launch"),
    path("aws/create/ec2/launch/", create_ec2, name="create_ec2"),
    path("aws/create/ec2/key-pair/", create_ec2_key_pair, name="create_ec2_key_pair"),
    path("aws/create/s3/", views.aws_create_s3, name="aws_s3_create"),
    path("aws/create/rds/", views.aws_create_rds, name="aws_rds_create"),
    path("aws/create/lambda/", views.aws_create_lambda, name="aws_lambda_create"),
    path("aws/create/vpc/", views.aws_create_vpc, name="aws_vpc_create"),
    path("aws/create/iam/", views.aws_create_iam_user, name="aws_iam_create"),
    path("aws/create/cloudwatch/", views.aws_create_cloudwatch_alarm, name="aws_cloudwatch_create"),
    path("aws/connect/", views.aws_connect, name="aws_connect"),
    path("aws/disconnect/", views.disconnect_aws, name="aws_disconnect"),
    path("aws/action/send-otp/", views.send_action_otp, name="send_action_otp"),
    path("aws/action/verify-otp/", views.verify_action_otp, name="verify_action_otp"),

]
