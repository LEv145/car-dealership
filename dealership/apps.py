from __future__ import annotations

from django.apps import AppConfig


class DealershipConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dealership"
    verbose_name = "Автосалон"
