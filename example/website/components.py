from djenga import BlockComponent, Component, register


@register
class Button(Component):
    """A simple button component."""

    label: str
    variant: str = "primary"
    disabled: bool = False

    class Media:
        css = {"all": ["css/button.css"]}


@register
class Alert(Component):
    """An alert/notification component."""

    message: str
    level: str = "info"  # info, success, warning, error

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context["level"] not in ["info", "success", "warning", "error"]:
            raise Exception("Invalid level for Alert component")
        return context


@register
class Card(BlockComponent):
    """A card component that wraps content."""

    title: str
    subtitle: str | None = None

    class Media:
        css = {"all": ["css/card.css"]}
