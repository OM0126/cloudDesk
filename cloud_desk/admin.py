from django.contrib import admin
from .models import AWSConnection, UserProfile
# Register your models here.


admin.site.register(UserProfile)
admin.site.register(AWSConnection)