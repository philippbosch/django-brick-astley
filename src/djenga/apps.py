from django.apps import AppConfig


class DjengaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djenga"
    verbose_name = "Djenga"

    def ready(self) -> None:
        from .autodiscover import autodiscover
        from .templatetags.djenga import register_component_tags

        autodiscover()
        register_component_tags()
