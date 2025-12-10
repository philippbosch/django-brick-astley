from brickastley import BlockBrick, Brick, register


@register
class Button(Brick):
    """A simple button brick."""

    label: str
    variant: str = "primary"
    disabled: bool = False

    class Media:
        css = {"all": ["css/button.css"]}


@register
class Alert(Brick):
    """An alert/notification brick."""

    message: str
    level: str = "info"  # info, success, warning, error

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context["level"] not in ["info", "success", "warning", "error"]:
            raise Exception("Invalid level for Alert brick")
        return context


@register
class Card(BlockBrick):
    """A card brick that wraps content."""

    title: str
    subtitle: str | None = None

    class Media:
        css = {"all": ["css/card.css"]}
