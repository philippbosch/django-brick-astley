from __future__ import annotations

import logging
import re
from typing import Any, ClassVar, get_type_hints

from django.conf import settings
from django.forms.widgets import Media, MediaDefiningClass
from django.template import loader

logger = logging.getLogger(__name__)


class ComponentValidationError(Exception):
    """Raised when component kwargs fail type validation."""

    pass


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _validate_type(value: Any, expected_type: type, field_name: str) -> None:
    """Validate that a value matches the expected type."""
    # Handle None for optional types
    if value is None:
        # Check if None is allowed (Union with None or Optional)
        origin = getattr(expected_type, "__origin__", None)
        if origin is type(None):
            return
        # For Union types (including Optional), check if NoneType is in args
        if hasattr(expected_type, "__args__") and type(None) in expected_type.__args__:
            return
        raise ComponentValidationError(
            f"Field '{field_name}' received None but is not optional"
        )

    # Get the origin type for generic types (e.g., list[int] -> list)
    origin = getattr(expected_type, "__origin__", None)

    if origin is not None:
        # Handle Union types (including Optional)
        if hasattr(expected_type, "__args__"):
            # For Union, check if value matches any of the types
            import typing

            if origin is typing.Union:
                for arg in expected_type.__args__:
                    if arg is type(None):
                        continue
                    try:
                        _validate_type(value, arg, field_name)
                        return  # Valid for at least one type
                    except ComponentValidationError:
                        continue
                raise ComponentValidationError(
                    f"Field '{field_name}' expected {expected_type}, got {type(value).__name__}"
                )

        # For other generic types, just check the origin
        if not isinstance(value, origin):
            raise ComponentValidationError(
                f"Field '{field_name}' expected {expected_type}, got {type(value).__name__}"
            )
    else:
        # Simple type check
        if not isinstance(value, expected_type):
            raise ComponentValidationError(
                f"Field '{field_name}' expected {expected_type.__name__}, got {type(value).__name__}"
            )


class ComponentMeta(MediaDefiningClass):
    """
    Metaclass for Component that processes field definitions.

    Inherits from MediaDefiningClass to support the Media inner class
    pattern used by Django forms and widgets.
    """

    def __new__(
        mcs, name: str, bases: tuple, namespace: dict, **kwargs: Any
    ) -> ComponentMeta:
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip processing for base classes
        if name in ("Component", "BlockComponent"):
            return cls

        # Gather fields from type hints
        hints = {}
        defaults = {}

        # Collect from parent classes first
        for base in reversed(cls.__mro__):
            if hasattr(base, "__annotations__"):
                for field_name, field_type in base.__annotations__.items():
                    # Skip class variables and private attributes
                    if field_name.startswith("_"):
                        continue
                    if hasattr(base, "__class_fields__"):
                        continue
                    hints[field_name] = field_type
                    # Check for default value
                    if hasattr(base, field_name):
                        defaults[field_name] = getattr(base, field_name)

        # Filter out ClassVar fields and known class attributes
        class_attrs = {"template_name", "component_name"}
        cls.__component_fields__ = {
            k: v for k, v in hints.items() if k not in class_attrs
        }
        cls.__component_defaults__ = {
            k: v for k, v in defaults.items() if k not in class_attrs
        }

        return cls


class Component(metaclass=ComponentMeta):
    """
    Base class for simple (self-closing) components.

    Usage:
        @register
        class MyButton(Component):
            label: str
            variant: str = "primary"

            class Media:
                css = {"all": ["css/button.css"]}
                js = ["js/button.js"]

    Template tag: {% my_button label="Click me" %}
    Template: components/my_button.html

    The Media class works exactly like Django forms/widgets Media.
    """

    # Can be overridden by subclasses
    template_name: ClassVar[str | None] = None
    component_name: ClassVar[str | None] = None

    # Set by metaclass
    __component_fields__: ClassVar[dict[str, type]]
    __component_defaults__: ClassVar[dict[str, Any]]

    def __init__(self, **kwargs: Any) -> None:
        self._validate_and_set_kwargs(kwargs)

    def _validate_and_set_kwargs(self, kwargs: dict[str, Any]) -> None:
        """Validate kwargs against field definitions and set as attributes."""
        fields = self.__component_fields__
        defaults = self.__component_defaults__

        # Check for required fields
        for field_name in fields:
            if field_name not in kwargs and field_name not in defaults:
                raise ComponentValidationError(
                    f"Missing required field '{field_name}' for component "
                    f"'{self.__class__.__name__}'"
                )

        # Validate and set each kwarg
        for field_name, value in kwargs.items():
            if field_name not in fields:
                raise ComponentValidationError(
                    f"Unknown field '{field_name}' for component "
                    f"'{self.__class__.__name__}'"
                )

            expected_type = fields[field_name]
            try:
                _validate_type(value, expected_type, field_name)
            except ComponentValidationError:
                if getattr(settings, "DEBUG", False):
                    raise
                else:
                    logger.warning(
                        f"Type validation failed for field '{field_name}' in "
                        f"component '{self.__class__.__name__}': expected "
                        f"{expected_type}, got {type(value).__name__}"
                    )

            setattr(self, field_name, value)

        # Set defaults for missing optional fields
        for field_name, default in defaults.items():
            if field_name not in kwargs:
                setattr(self, field_name, default)

    @classmethod
    def get_component_name(cls) -> str:
        """Get the template tag name for this component."""
        if cls.component_name:
            return cls.component_name
        return _camel_to_snake(cls.__name__)

    @classmethod
    def get_template_name(cls) -> str:
        """Get the template path for this component."""
        if cls.template_name:
            return cls.template_name
        return f"components/{_camel_to_snake(cls.__name__)}.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Get the template context for rendering.

        Override this method to customize the context passed to the template.
        By default, returns all component fields as context variables.
        """
        context = {}
        for field_name in self.__component_fields__:
            if hasattr(self, field_name):
                context[field_name] = getattr(self, field_name)
        context.update(kwargs)
        return context

    def render(self) -> str:
        """Render the component to a string."""
        template = loader.get_template(self.get_template_name())
        context = self.get_context_data()
        return template.render(context)


class BlockComponent(Component):
    """
    Base class for block components that can wrap children.

    Usage:
        @register
        class Card(BlockComponent):
            title: str

    Template tag:
        {% card title="Hello" %}
            <p>Card content here</p>
        {% endcard %}

    Template (components/card.html):
        <div class="card">
            <h2>{{ title }}</h2>
            <div class="card-body">
                {{ children }}
            </div>
        </div>
    """

    def render(self, children: str = "") -> str:
        """Render the component with children content."""
        template = loader.get_template(self.get_template_name())
        context = self.get_context_data(children=children)
        return template.render(context)
