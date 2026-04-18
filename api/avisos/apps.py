from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AvisosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "avisos"
    verbose_name = _("Avisos")
