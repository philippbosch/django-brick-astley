from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeVar, overload

if TYPE_CHECKING:
    from .component import Component

C = TypeVar("C", bound="Component")

# Global registry mapping component names to component classes
_registry: dict[str, type[Component]] = {}


def get_registry() -> dict[str, type[Component]]:
    """Get the global component registry."""
    return _registry


def get_component(name: str) -> type[Component] | None:
    """Get a component class by its registered name."""
    return _registry.get(name)


def clear_registry() -> None:
    """Clear the component registry. Useful for testing."""
    _registry.clear()


@overload
def register(cls: type[C]) -> type[C]: ...


@overload
def register(
    cls: None = None, *, name: str | None = None
) -> Callable[[type[C]], type[C]]: ...


def register(
    cls: type[C] | None = None, *, name: str | None = None
) -> type[C] | Callable[[type[C]], type[C]]:
    """
    Register a component class.

    Can be used as a decorator with or without arguments:

        @register
        class MyComponent(Component):
            ...

        @register(name="custom_name")
        class MyComponent(Component):
            ...

    Args:
        cls: The component class to register (when used without parentheses)
        name: Optional custom name for the component's template tag
    """

    def decorator(component_cls: type[C]) -> type[C]:
        # Determine the component name
        if name:
            component_name = name
            # Also set it on the class so get_component_name() returns it
            component_cls.component_name = name  # type: ignore[attr-defined]
        else:
            component_name = component_cls.get_component_name()  # type: ignore[attr-defined]

        # Check for duplicate registration
        if component_name in _registry:
            existing = _registry[component_name]
            if existing is not component_cls:
                raise ValueError(
                    f"Component name '{component_name}' is already registered "
                    f"by {existing.__module__}.{existing.__name__}"
                )

        _registry[component_name] = component_cls
        return component_cls

    # Handle both @register and @register(...) syntax
    if cls is not None:
        return decorator(cls)
    return decorator
