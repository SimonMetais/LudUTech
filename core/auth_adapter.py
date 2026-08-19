# myapp/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages




class DomainRestrictedSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email", "")
        email_verified = sociallogin.account.extra_data.get("email_verified", False)
        domain: str = email.split("@")[-1].lower()
        d = settings.AUTH_ALLOWED_DOMAIN
        if not domain.endswith((f'.{d}', f'@{d}')) or not email_verified:
            messages.error(
                request,
                f"Seuls les comptes {d} sont autorisés."
            )
            raise ImmediateHttpResponse(redirect("account_login"))