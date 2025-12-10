django-brick-astley
===================

**django-brick-astley** (import as ``brickastley``) is a Django package for creating
reusable template components called "bricks". It provides a clean, declarative way to
define UI components with type-validated kwargs and automatic template tag generation.

.. code-block:: python

   from brickastley import Brick, register

   @register
   class Button(Brick):
       label: str
       variant: str = "primary"
       disabled: bool = False

Then use it in your templates:

.. code-block:: html+django

   {% button label="Click me" variant="primary" %}

Features
--------

- **Declarative Components**: Define bricks as Python classes with type-annotated kwargs
- **Automatic Template Tags**: Components are automatically registered as Django template tags
- **Type Validation**: Kwargs are validated against their type hints (strict in DEBUG, warnings in production)
- **Block Components**: Support for components that wrap content (like cards, modals, etc.)
- **Media Support**: Include CSS/JS assets with your components using Django's Media class
- **Autodiscovery**: Automatically discovers ``bricks.py`` modules in your Django apps

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   guide
   api

Quick Example
-------------

Create a ``bricks.py`` file in your Django app:

.. code-block:: python

   # myapp/bricks.py
   from brickastley import Brick, BlockBrick, register

   @register
   class Alert(Brick):
       message: str
       level: str = "info"  # info, success, warning, error

   @register
   class Card(BlockBrick):
       title: str
       subtitle: str | None = None

Create templates for your bricks:

.. code-block:: html+django

   {# myapp/templates/bricks/alert.html #}
   <div class="alert alert-{{ level }}">
       {{ message }}
   </div>

.. code-block:: html+django

   {# myapp/templates/bricks/card.html #}
   <div class="card">
       <h2>{{ title }}</h2>
       {% if subtitle %}<h3>{{ subtitle }}</h3>{% endif %}
       <div class="card-body">
           {{ children }}
       </div>
   </div>

Use them in your templates:

.. code-block:: html+django

   {% load brickastley %}

   {% alert message="Operation successful!" level="success" %}

   {% card title="Welcome" subtitle="Getting started" %}
       <p>This content goes inside the card.</p>
   {% endcard %}


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
