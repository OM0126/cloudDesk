from django import forms
from allauth.socialaccount.forms import SignupForm as SocialSignupForm


class CloudDeskSocialSignupForm(SocialSignupForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full Name",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your full name",
            "autofocus": True,
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Email comes pre-verified from Google — lock it
        if "email" in self.fields:
            self.fields["email"].widget.attrs["readonly"] = True

        # Show Full Name first, then Email, then Username
        self.order_fields(["full_name", "email", "username"])

    def save(self, request):
        user = super().save(request)

        full_name = self.cleaned_data.get("full_name", "").strip()
        if full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""
            user.save()

        return user