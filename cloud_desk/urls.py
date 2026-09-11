from django.urls import path
from . import views
from .aws_dashboard import aws_account_page, ec2_launch_page, create_ec2


urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("complete-profile/", views.complete_profile, name="complete_profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),

    # AWS
    path("aws/account/", aws_account_page, name="aws_account"),
    path("aws/create/ec2/", ec2_launch_page, name="aws_ec2_launch"),
    path("aws/create/ec2/launch/", create_ec2, name="create_ec2"),
    path("aws/connect/", views.aws_connect, name="aws_connect"),
    path("aws/disconnect/", views.disconnect_aws, name="aws_disconnect"),
    path("aws/action/send-otp/", views.send_action_otp, name="send_action_otp"),
    path("aws/action/verify-otp/", views.verify_action_otp, name="verify_action_otp"),

    # GCP
    path("gcp/connect/", views.gcp_connect, name="gcp_connect"),
    path("gcp/disconnect/", views.disconnect_gcp, name="gcp_disconnect"),
]
