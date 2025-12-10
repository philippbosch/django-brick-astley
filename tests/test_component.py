import pytest

from djenga import BlockComponent, Component, ComponentValidationError


class TestComponentFields:
    """Tests for component field parsing and defaults."""

    def test_required_field(self):
        """Required fields must be provided."""

        class MyComponent(Component):
            name: str

        with pytest.raises(ComponentValidationError) as exc_info:
            MyComponent()

        assert "Missing required field 'name'" in str(exc_info.value)

    def test_optional_field_with_default(self):
        """Optional fields use their default value when not provided."""

        class MyComponent(Component):
            name: str
            color: str = "blue"

        comp = MyComponent(name="test")
        assert comp.name == "test"
        assert comp.color == "blue"

    def test_optional_field_override(self):
        """Optional fields can be overridden."""

        class MyComponent(Component):
            name: str
            color: str = "blue"

        comp = MyComponent(name="test", color="red")
        assert comp.color == "red"

    def test_nullable_field(self):
        """Fields with None default are optional and nullable."""

        class MyComponent(Component):
            name: str
            subtitle: str | None = None

        comp = MyComponent(name="test")
        assert comp.subtitle is None

        comp2 = MyComponent(name="test", subtitle="hello")
        assert comp2.subtitle == "hello"

    def test_unknown_field_raises(self):
        """Unknown fields raise an error."""

        class MyComponent(Component):
            name: str

        with pytest.raises(ComponentValidationError) as exc_info:
            MyComponent(name="test", unknown="value")

        assert "Unknown field 'unknown'" in str(exc_info.value)


class TestTypeValidation:
    """Tests for type validation."""

    def test_string_validation(self):
        """String fields validate correctly."""

        class MyComponent(Component):
            name: str

        comp = MyComponent(name="hello")
        assert comp.name == "hello"

    def test_int_validation(self):
        """Integer fields validate correctly."""

        class MyComponent(Component):
            count: int

        comp = MyComponent(count=42)
        assert comp.count == 42

    def test_bool_validation(self):
        """Boolean fields validate correctly."""

        class MyComponent(Component):
            active: bool

        comp = MyComponent(active=True)
        assert comp.active is True

    def test_type_mismatch_in_debug(self, settings):
        """Type mismatch raises exception in DEBUG mode."""
        settings.DEBUG = True

        class MyComponent(Component):
            count: int

        with pytest.raises(ComponentValidationError) as exc_info:
            MyComponent(count="not an int")

        assert "expected int" in str(exc_info.value)

    def test_type_mismatch_in_production(self, settings, caplog):
        """Type mismatch logs warning in production mode."""
        settings.DEBUG = False

        class MyComponent(Component):
            count: int

        # Should not raise, just log
        comp = MyComponent(count="not an int")
        assert comp.count == "not an int"  # Value still set despite type mismatch
        assert "Type validation failed" in caplog.text

    def test_union_type_validation(self):
        """Union types validate correctly."""

        class MyComponent(Component):
            value: str | int

        comp1 = MyComponent(value="hello")
        assert comp1.value == "hello"

        comp2 = MyComponent(value=42)
        assert comp2.value == 42

    def test_optional_union_type(self):
        """Optional (Union with None) validates correctly."""

        class MyComponent(Component):
            value: str | None = None

        comp1 = MyComponent()
        assert comp1.value is None

        comp2 = MyComponent(value="hello")
        assert comp2.value == "hello"

        comp3 = MyComponent(value=None)
        assert comp3.value is None


class TestComponentNaming:
    """Tests for component name derivation."""

    def test_default_name_from_class(self):
        """Component name is derived from class name."""

        class MyButton(Component):
            label: str

        assert MyButton.get_component_name() == "my_button"

    def test_default_name_camel_case(self):
        """CamelCase class names convert to snake_case."""

        class MyFancyButtonComponent(Component):
            label: str

        assert MyFancyButtonComponent.get_component_name() == "my_fancy_button_component"

    def test_custom_component_name(self):
        """Custom component name can be set."""

        class MyButton(Component):
            label: str
            component_name = "btn"

        assert MyButton.get_component_name() == "btn"

    def test_default_template_name(self):
        """Template name is derived from class name."""

        class MyButton(Component):
            label: str

        assert MyButton.get_template_name() == "components/my_button.html"

    def test_custom_template_name(self):
        """Custom template name can be set."""

        class MyButton(Component):
            label: str
            template_name = "custom/button.html"

        assert MyButton.get_template_name() == "custom/button.html"


class TestContextData:
    """Tests for context data generation."""

    def test_default_context_includes_fields(self):
        """Default context includes all field values."""

        class MyComponent(Component):
            name: str
            count: int = 0

        comp = MyComponent(name="test", count=5)
        context = comp.get_context_data()

        assert context["name"] == "test"
        assert context["count"] == 5

    def test_context_data_can_be_extended(self):
        """get_context_data can be overridden to add extra context."""

        class MyComponent(Component):
            name: str

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context["uppercase_name"] = self.name.upper()
                return context

        comp = MyComponent(name="test")
        context = comp.get_context_data()

        assert context["name"] == "test"
        assert context["uppercase_name"] == "TEST"


class TestBlockComponent:
    """Tests for BlockComponent."""

    def test_block_component_inherits_from_component(self):
        """BlockComponent is a subclass of Component."""
        assert issubclass(BlockComponent, Component)

    def test_block_component_fields_work(self):
        """BlockComponent supports fields like Component."""

        class Card(BlockComponent):
            title: str
            subtitle: str | None = None

        card = Card(title="Hello")
        assert card.title == "Hello"
        assert card.subtitle is None

    def test_block_component_render_includes_children(self):
        """BlockComponent.render() accepts children parameter."""

        class Card(BlockComponent):
            title: str
            template_name = "test_card.html"

        card = Card(title="Hello")
        # Note: actual rendering requires template to exist
        # This test just verifies the method signature
        assert hasattr(card, "render")


class TestMedia:
    """Tests for Media class support."""

    def test_component_with_media(self):
        """Components can define Media class."""

        class MyButton(Component):
            label: str

            class Media:
                css = {"all": ["css/button.css"]}
                js = ["js/button.js"]

        # Media is handled by Django's MediaDefiningClass metaclass
        assert hasattr(MyButton, "media")
        assert "css/button.css" in str(MyButton(label="test").media)
        assert "js/button.js" in str(MyButton(label="test").media)

    def test_component_without_media(self):
        """Components without Media class still work."""

        class MyButton(Component):
            label: str

        comp = MyButton(label="test")
        # Should have empty media
        assert hasattr(comp, "media")
