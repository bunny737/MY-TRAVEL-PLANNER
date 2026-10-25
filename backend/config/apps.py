from django.contrib.admin.apps import AdminConfig


class MfaAdminConfig(AdminConfig):
    """django.contrib.admin, but the default site requires a second factor (see config/admin_site.py)."""

    default_site = 'config.admin_site.MfaAdminSite'
