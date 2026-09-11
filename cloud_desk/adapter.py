from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CloudDeskSocialAccountAdapter(DefaultSocialAccountAdapter):


    def pre_social_login(self, request, sociallogin):

        if sociallogin.is_existing:
            request.session.pop("google_new_user", None)
            request.session.modified = True
            return

        request.session["google_new_user"] = True
        request.session.modified = True


class CloudDeskAccountAdapter(DefaultAccountAdapter):

    def add_message(self, request, level, message_template, message_context=None, extra_tags=""):

        suppressed = (
            "account/messages/logged_in.txt",
            "account/messages/logged_out.txt",
            "account/messages/password_set.txt",
        )
        if message_template in suppressed:
            return
        super().add_message(request, level, message_template, message_context, extra_tags)