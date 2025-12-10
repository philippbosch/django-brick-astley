from __future__ import annotations

from importlib import import_module

from django.apps import apps
from django.utils.module_loading import module_has_submodule


def autodiscover() -> None:
    """
    Auto-discover bricks.py modules in all installed Django apps.

    This function iterates through all installed apps and imports their
    bricks.py module if it exists. The import triggers the @register
    decorators, which populate the brick registry.

    This is similar to Django's admin.autodiscover() pattern.
    """
    for app_config in apps.get_app_configs():
        # Skip if the app doesn't have a bricks module
        if not module_has_submodule(app_config.module, "bricks"):
            continue

        # Import the bricks module to trigger registration
        module_name = f"{app_config.name}.bricks"
        try:
            import_module(module_name)
        except Exception as e:
            # Re-raise with more context
            raise ImportError(
                f"Error importing bricks from {module_name}: {e}"
            ) from e
