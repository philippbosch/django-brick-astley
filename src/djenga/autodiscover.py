from __future__ import annotations

from importlib import import_module

from django.apps import apps
from django.utils.module_loading import module_has_submodule


def autodiscover() -> None:
    """
    Auto-discover components.py modules in all installed Django apps.

    This function iterates through all installed apps and imports their
    components.py module if it exists. The import triggers the @register
    decorators, which populate the component registry.

    This is similar to Django's admin.autodiscover() pattern.
    """
    for app_config in apps.get_app_configs():
        # Skip if the app doesn't have a components module
        if not module_has_submodule(app_config.module, "components"):
            continue

        # Import the components module to trigger registration
        module_name = f"{app_config.name}.components"
        try:
            import_module(module_name)
        except Exception as e:
            # Re-raise with more context
            raise ImportError(
                f"Error importing components from {module_name}: {e}"
            ) from e
