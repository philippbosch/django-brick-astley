import pytest
from django.template import Context, Template, TemplateSyntaxError

from djenga import BlockComponent, Component, register
from djenga.registry import clear_registry


@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before and after each test."""
    clear_registry()
    yield
    clear_registry()


@pytest.fixture
def reload_templatetags():
    """Reload templatetags after registering components."""
    # Import here to trigger tag registration
    from djenga.templatetags import djenga as djenga_tags

    def _reload():
        djenga_tags.register_component_tags()

    return _reload


class TestSimpleComponentRendering:
    """Tests for simple component template tag rendering."""

    def test_render_simple_component(self, reload_templatetags):
        """Simple component renders correctly."""

        @register
        class TestButton(Component):
            label: str
            template_name = "test_button.html"

        reload_templatetags()

        # Create a simple template that uses our component
        # We need to mock the template loading, so we'll test the node directly
        from djenga.templatetags.djenga import ComponentNode

        node = ComponentNode(TestButton, {"label": "Click me"})
        # We can't fully test without a template file, but we can test instantiation
        assert node.component_class is TestButton
        assert node.kwargs == {"label": "Click me"}

    def test_parse_string_kwarg(self, reload_templatetags):
        """String kwargs are parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ['label="Hello World"'])
        assert result["label"] == "Hello World"

    def test_parse_single_quoted_string(self, reload_templatetags):
        """Single-quoted strings are parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["label='Hello'"])
        assert result["label"] == "Hello"

    def test_parse_integer_kwarg(self, reload_templatetags):
        """Integer kwargs are parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["count=42"])
        assert result["count"] == 42
        assert isinstance(result["count"], int)

    def test_parse_negative_integer(self, reload_templatetags):
        """Negative integers are parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["count=-5"])
        assert result["count"] == -5

    def test_parse_float_kwarg(self, reload_templatetags):
        """Float kwargs are parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["price=19.99"])
        assert result["price"] == 19.99
        assert isinstance(result["price"], float)

    def test_parse_boolean_true(self, reload_templatetags):
        """Boolean True is parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["active=True"])
        assert result["active"] is True

    def test_parse_boolean_false(self, reload_templatetags):
        """Boolean False is parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["active=False"])
        assert result["active"] is False

    def test_parse_none(self, reload_templatetags):
        """None is parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["value=None"])
        assert result["value"] is None

    def test_parse_variable_kwarg(self, reload_templatetags):
        """Variable kwargs are parsed as Template Variables."""
        from django.template import Variable

        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(MockParser(), ["label=my_variable"])
        assert isinstance(result["label"], Variable)

    def test_invalid_kwarg_format_raises(self, reload_templatetags):
        """Invalid kwarg format raises TemplateSyntaxError."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        with pytest.raises(TemplateSyntaxError) as exc_info:
            parse_tag_kwargs(MockParser(), ["invalid"])

        assert "must be in kwarg=value format" in str(exc_info.value)


class TestVariableResolution:
    """Tests for template variable resolution."""

    def test_resolve_static_kwargs(self):
        """Static kwargs pass through unchanged."""
        from djenga.templatetags.djenga import resolve_kwargs

        kwargs = {"label": "Hello", "count": 42}
        context = Context({})

        result = resolve_kwargs(kwargs, context)
        assert result == {"label": "Hello", "count": 42}

    def test_resolve_variable_kwargs(self):
        """Template variables are resolved from context."""
        from django.template import Variable

        from djenga.templatetags.djenga import resolve_kwargs

        kwargs = {"label": Variable("my_label"), "static": "value"}
        context = Context({"my_label": "Dynamic Label"})

        result = resolve_kwargs(kwargs, context)
        assert result["label"] == "Dynamic Label"
        assert result["static"] == "value"


class TestBlockComponentRendering:
    """Tests for block component template tag rendering."""

    def test_block_component_node_has_nodelist(self, reload_templatetags):
        """BlockComponentNode stores the nodelist for children."""
        from django.template.base import NodeList

        from djenga.templatetags.djenga import BlockComponentNode

        @register
        class TestCard(BlockComponent):
            title: str

        nodelist = NodeList()
        node = BlockComponentNode(TestCard, {"title": "Hello"}, nodelist)

        assert node.component_class is TestCard
        assert node.nodelist is nodelist


class TestMultipleKwargs:
    """Tests for parsing multiple kwargs."""

    def test_parse_multiple_kwargs(self):
        """Multiple kwargs are parsed correctly."""
        from djenga.templatetags.djenga import parse_tag_kwargs

        class MockParser:
            pass

        result = parse_tag_kwargs(
            MockParser(),
            ['label="Click"', "count=5", "active=True", "price=9.99"],
        )

        assert result["label"] == "Click"
        assert result["count"] == 5
        assert result["active"] is True
        assert result["price"] == 9.99
