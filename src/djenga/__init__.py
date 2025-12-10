"""
djenga - Reusable components for Django templates
"""

__version__ = "0.1.0"

default_app_config = "djenga.apps.DjengaConfig"

from .component import BlockComponent, Component, ComponentValidationError
from .registry import register

__all__ = [
    "Component",
    "BlockComponent",
    "ComponentValidationError",
    "register",
]
