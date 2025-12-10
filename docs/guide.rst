Advanced Usage Guide
====================

This guide covers advanced features and patterns for using django-brick-astley.

Type Validation
---------------

Brick kwargs are validated against their type hints. The behavior depends on your
``DEBUG`` setting:

- **DEBUG=True**: Type mismatches raise ``BrickValidationError``
- **DEBUG=False**: Type mismatches log a warning but allow rendering to continue

Supported Types
~~~~~~~~~~~~~~~

.. code-block:: python

   from brickastley import Brick, register

   @register
   class MyBrick(Brick):
       # Basic types
       name: str
       count: int
       price: float
       active: bool

       # Optional types (can be None)
       subtitle: str | None = None

       # Union types
       value: str | int = 0

       # With defaults
       variant: str = "default"

Template Tag Values
~~~~~~~~~~~~~~~~~~~

In templates, values are parsed as follows:

.. code-block:: html+django

   {# Strings - use quotes #}
   {% mybrick name="Hello World" %}
   {% mybrick name='Single quotes work too' %}

   {# Integers #}
   {% mybrick count=42 %}
   {% mybrick count=-5 %}

   {# Floats #}
   {% mybrick price=19.99 %}

   {# Booleans #}
   {% mybrick active=True %}
   {% mybrick active=False %}

   {# None #}
   {% mybrick subtitle=None %}

   {# Template variables #}
   {% mybrick name=user.username %}
   {% mybrick count=items|length %}

Custom Context Data
-------------------

Override ``get_context_data()`` to add computed values or transform kwargs:

.. code-block:: python

   @register
   class PriceTag(Brick):
       amount: float
       currency: str = "USD"

       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           # Add computed values
           context["formatted_price"] = f"{self.currency} {self.amount:.2f}"
           context["is_free"] = self.amount == 0
           return context

Use in template:

.. code-block:: html+django

   {# bricks/price_tag.html #}
   <span class="price{% if is_free %} price--free{% endif %}">
       {% if is_free %}
           Free
       {% else %}
           {{ formatted_price }}
       {% endif %}
   </span>

Media (CSS and JavaScript)
--------------------------

Bricks support Django's Media class for declaring CSS and JavaScript dependencies:

.. code-block:: python

   @register
   class FancyButton(Brick):
       label: str

       class Media:
           css = {
               "all": ["css/fancy-button.css"],
           }
           js = ["js/fancy-button.js"]

You can access the media on brick instances:

.. code-block:: python

   button = FancyButton(label="Click")
   print(button.media)  # Outputs CSS and JS tags

.. note::

   Currently, media assets must be included manually in your base template.
   Automatic collection of brick media is planned for a future release.

Custom Brick Names
------------------

Use the ``name`` parameter to customize the template tag name:

.. code-block:: python

   @register(name="btn")
   class Button(Brick):
       label: str

   @register(name="cta")
   class CallToAction(Brick):
       text: str
       url: str

Use in templates:

.. code-block:: html+django

   {% btn label="Click me" %}
   {% cta text="Sign up now" url="/signup/" %}

Custom Template Paths
---------------------

Set ``template_name`` to use a custom template location:

.. code-block:: python

   @register
   class Button(Brick):
       label: str
       template_name = "components/buttons/primary.html"

   @register
   class Card(BlockBrick):
       title: str
       template_name = "ui/cards/basic.html"

Brick Inheritance
-----------------

Bricks can inherit from other bricks:

.. code-block:: python

   class BaseButton(Brick):
       label: str
       disabled: bool = False

   @register
   class PrimaryButton(BaseButton):
       # Inherits label and disabled
       pass

   @register
   class DangerButton(BaseButton):
       # Inherits label and disabled, adds confirm
       confirm: bool = False

.. note::

   Only bricks decorated with ``@register`` become template tags.
   Base classes without the decorator are not registered.

Accessing the Registry
----------------------

You can programmatically access registered bricks:

.. code-block:: python

   from brickastley.registry import get_registry, get_brick

   # Get all registered bricks
   registry = get_registry()
   for name, brick_class in registry.items():
       print(f"{name}: {brick_class}")

   # Get a specific brick by name
   ButtonClass = get_brick("button")
   if ButtonClass:
       button = ButtonClass(label="Hello")

Nesting Bricks
--------------

Bricks can be nested inside block bricks:

.. code-block:: html+django

   {% card title="User Actions" %}
       <div class="button-group">
           {% button label="Edit" variant="primary" %}
           {% button label="Delete" variant="danger" %}
       </div>
   {% endcard %}

Template Tag Loading
--------------------

By default, you need to load the brickastley template tags:

.. code-block:: html+django

   {% load brickastley %}

To make bricks available in all templates without loading, add to your settings:

.. code-block:: python

   TEMPLATES = [
       {
           "BACKEND": "django.template.backends.django.DjangoTemplates",
           "OPTIONS": {
               "builtins": [
                   "brickastley.templatetags.brickastley",
               ],
           },
       },
   ]

Autodiscovery
-------------

Brickastley automatically discovers ``bricks.py`` modules in all installed Django apps
when the app is ready. This happens in the ``AppConfig.ready()`` method.

The autodiscovery process:

1. Iterates through all installed apps
2. Checks if each app has a ``bricks.py`` module
3. Imports the module, triggering ``@register`` decorators
4. Registers all discovered bricks as template tags

If you need to manually trigger discovery (e.g., in tests):

.. code-block:: python

   from brickastley.autodiscover import autodiscover
   from brickastley.templatetags.brickastley import register_brick_tags

   autodiscover()
   register_brick_tags()

Testing Bricks
--------------

Test brick instantiation and context:

.. code-block:: python

   from myapp.bricks import Button

   def test_button_defaults():
       button = Button(label="Click")
       assert button.label == "Click"
       assert button.variant == "primary"
       assert button.disabled is False

   def test_button_context():
       button = Button(label="Click", variant="danger")
       context = button.get_context_data()
       assert context["label"] == "Click"
       assert context["variant"] == "danger"

Test validation:

.. code-block:: python

   import pytest
   from brickastley import BrickValidationError
   from myapp.bricks import Button

   def test_missing_required_kwarg():
       with pytest.raises(BrickValidationError):
           Button()  # Missing required 'label'

   def test_unknown_kwarg():
       with pytest.raises(BrickValidationError):
           Button(label="Click", unknown="value")
