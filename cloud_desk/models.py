from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Optional profile model for CloudDesk users."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cloud_desk_profile",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class AWSConnection(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="aws_connections",
    )

    name = models.CharField(
        max_length=100,
        default="My AWS Account",
    )

    access_key_id = models.CharField(
        max_length=255,
    )

    secret_access_key = models.CharField(
        max_length=255,
    )

    region = models.CharField(
        max_length=100,
        default="us-east-1",
    )

    account_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    is_connected = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class GCPConnection(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="gcp_connections",
    )

    name = models.CharField(
        max_length=100,
        default="My GCP Account",
    )

    project_id = models.CharField(
        max_length=200,
    )

    project_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    service_account_email = models.EmailField(
        blank=True,
        null=True,
    )

    credentials_json = models.TextField(
        blank=True,
        null=True,
    )

    is_connected = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name} - {self.user.username}"