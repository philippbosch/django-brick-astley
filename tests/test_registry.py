import pytest

from djenga import Component, register
from djenga.registry import clear_registry, get_component, get_registry


@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before and after each test."""
    clear_registry()
    yield
    clear_registry()


class TestRegisterDecorator:
    """Tests for the @register decorator."""

    def test_register_without_arguments(self):
        """@register without arguments uses class name for tag name."""

        @register
        class MyButton(Component):
            label: str

        registry = get_registry()
        assert "my_button" in registry
        assert registry["my_button"] is MyButton

    def test_register_with_custom_name(self):
        """@register(name="...") uses custom tag name."""

        @register(name="btn")
        class MyButton(Component):
            label: str

        registry = get_registry()
        assert "btn" in registry
        assert "my_button" not in registry
        assert registry["btn"] is MyButton

    def test_register_sets_component_name(self):
        """@register(name="...") also sets component_name on class."""

        @register(name="btn")
        class MyButton(Component):
            label: str

        assert MyButton.get_component_name() == "btn"

    def test_register_returns_class(self):
        """@register returns the original class unchanged."""

        @register
        class MyButton(Component):
            label: str

        assert MyButton.__name__ == "MyButton"
        assert issubclass(MyButton, Component)

    def test_duplicate_registration_same_class(self):
        """Registering the same class twice is allowed."""

        @register
        class MyButton(Component):
            label: str

        # Re-registering same class should not raise
        register(MyButton)

        registry = get_registry()
        assert registry["my_button"] is MyButton

    def test_duplicate_registration_different_class_raises(self):
        """Registering different class with same name raises."""

        @register
        class MyButton(Component):
            label: str

        with pytest.raises(ValueError) as exc_info:

            @register(name="my_button")
            class AnotherButton(Component):
                text: str

        assert "already registered" in str(exc_info.value)


class TestGetComponent:
    """Tests for get_component function."""

    def test_get_existing_component(self):
        """get_component returns registered component."""

        @register
        class MyButton(Component):
            label: str

        result = get_component("my_button")
        assert result is MyButton

    def test_get_nonexistent_component(self):
        """get_component returns None for unknown component."""
        result = get_component("nonexistent")
        assert result is None


class TestClearRegistry:
    """Tests for clear_registry function."""

    def test_clear_removes_all(self):
        """clear_registry removes all registered components."""

        @register
        class Button1(Component):
            label: str

        @register
        class Button2(Component):
            label: str

        assert len(get_registry()) == 2

        clear_registry()

        assert len(get_registry()) == 0
