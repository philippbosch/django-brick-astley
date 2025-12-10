from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import template
from django.template.base import Parser, Token
from django.template.context import Context
from django.utils.safestring import mark_safe

from ..component import BlockComponent, Component
from ..registry import get_registry

if TYPE_CHECKING:
    from django.template.base import NodeList

register = template.Library()


def parse_tag_kwargs(parser: Parser, bits: list[str]) -> dict[str, Any]:
    """
    Parse keyword arguments from template tag bits.

    Handles:
        - kwarg="string value"
        - kwarg=variable
        - kwarg=42 (integers)
        - kwarg=3.14 (floats)
        - kwarg=True/False (booleans)
    """
    kwargs: dict[str, Any] = {}

    for bit in bits:
        if "=" not in bit:
            raise template.TemplateSyntaxError(
                f"Invalid argument '{bit}'. Arguments must be in kwarg=value format."
            )

        name, value = bit.split("=", 1)

        # Handle quoted strings
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            kwargs[name] = value[1:-1]
        # Handle booleans
        elif value == "True":
            kwargs[name] = True
        elif value == "False":
            kwargs[name] = False
        # Handle None
        elif value == "None":
            kwargs[name] = None
        # Handle integers
        elif value.lstrip("-").isdigit():
            kwargs[name] = int(value)
        # Handle floats
        elif _is_float(value):
            kwargs[name] = float(value)
        # Handle as template variable
        else:
            kwargs[name] = template.Variable(value)

    return kwargs


def _is_float(value: str) -> bool:
    """Check if a string represents a float."""
    try:
        float(value)
        return "." in value or "e" in value.lower()
    except ValueError:
        return False


def resolve_kwargs(kwargs: dict[str, Any], context: Context) -> dict[str, Any]:
    """Resolve any template variables in kwargs."""
    resolved = {}
    for key, value in kwargs.items():
        if isinstance(value, template.Variable):
            resolved[key] = value.resolve(context)
        else:
            resolved[key] = value
    return resolved


class ComponentNode(template.Node):
    """Template node for simple (self-closing) components."""

    def __init__(
        self, component_class: type[Component], kwargs: dict[str, Any]
    ) -> None:
        self.component_class = component_class
        self.kwargs = kwargs

    def render(self, context: Context) -> str:
        resolved_kwargs = resolve_kwargs(self.kwargs, context)
        component = self.component_class(**resolved_kwargs)
        return mark_safe(component.render())


class BlockComponentNode(template.Node):
    """Template node for block components that wrap children."""

    def __init__(
        self,
        component_class: type[BlockComponent],
        kwargs: dict[str, Any],
        nodelist: NodeList,
    ) -> None:
        self.component_class = component_class
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context: Context) -> str:
        resolved_kwargs = resolve_kwargs(self.kwargs, context)
        children = self.nodelist.render(context)
        component = self.component_class(**resolved_kwargs)
        return mark_safe(component.render(children=children))


def create_simple_tag(component_class: type[Component]):
    """Create a simple tag function for a component."""

    def tag_func(parser: Parser, token: Token) -> ComponentNode:
        bits = token.split_contents()[1:]  # Skip the tag name
        kwargs = parse_tag_kwargs(parser, bits)
        return ComponentNode(component_class, kwargs)

    return tag_func


def create_block_tag(component_class: type[BlockComponent]):
    """Create a block tag function for a component."""
    tag_name = component_class.get_component_name()
    end_tag = f"end{tag_name}"

    def tag_func(parser: Parser, token: Token) -> BlockComponentNode:
        bits = token.split_contents()[1:]  # Skip the tag name
        kwargs = parse_tag_kwargs(parser, bits)
        nodelist = parser.parse((end_tag,))
        parser.delete_first_token()  # Remove the end tag
        return BlockComponentNode(component_class, kwargs, nodelist)

    return tag_func


def register_component_tags() -> None:
    """Register all components as template tags."""
    registry = get_registry()

    for name, component_class in registry.items():
        # Skip if already registered
        if name in register.tags:
            continue

        if issubclass(component_class, BlockComponent):
            tag_func = create_block_tag(component_class)
        else:
            tag_func = create_simple_tag(component_class)

        # Register the tag with Django's template library
        register.tag(name, tag_func)


# Note: We don't call register_component_tags() here at import time
# because autodiscovery may not have run yet. Instead, we register
# tags in DjengaConfig.ready() after autodiscovery completes.
