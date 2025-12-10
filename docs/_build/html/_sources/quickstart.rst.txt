Quickstart
==========

This guide will get you up and running with django-brick-astley in minutes.

Installation
------------

Install the package using pip:

.. code-block:: bash

   pip install django-brick-astley

Configuration
-------------

Add ``brickastley`` to your ``INSTALLED_APPS`` in your Django settings:

.. code-block:: python

   INSTALLED_APPS = [
       # ... other apps
       "brickastley",
       # ... your apps
   ]

That's it! The package will automatically discover ``bricks.py`` modules in all your
installed apps and register them as template tags.

Creating Your First Brick
-------------------------

1. Create a ``bricks.py`` file in one of your Django apps:

.. code-block:: python

   # myapp/bricks.py
   from brickastley import Brick, register

   @register
   class Button(Brick):
       """A simple button component."""
       label: str
       variant: str = "primary"
       disabled: bool = False

2. Create a template for your brick at ``myapp/templates/bricks/button.html``:

.. code-block:: html+django

   <button class="btn btn-{{ variant }}"{% if disabled %} disabled{% endif %}>
       {{ label }}
   </button>

3. Use the brick in your templates:

.. code-block:: html+django

   {% load brickastley %}

   {% button label="Click me" %}
   {% button label="Secondary" variant="secondary" %}
   {% button label="Disabled" disabled=True %}

Understanding Brick Names
-------------------------

By default, brick names are derived from the class name using snake_case conversion:

- ``Button`` → ``{% button %}``
- ``MyFancyButton`` → ``{% my_fancy_button %}``
- ``AlertBox`` → ``{% alert_box %}``

You can customize the name using the ``name`` parameter:

.. code-block:: python

   @register(name="btn")
   class Button(Brick):
       label: str

Now use it as ``{% btn label="Click" %}``.

Template Paths
--------------

By default, brick templates are located at ``bricks/<brick_name>.html``. For example:

- ``Button`` → ``bricks/button.html``
- ``AlertBox`` → ``bricks/alert_box.html``

You can customize the template path:

.. code-block:: python

   @register
   class Button(Brick):
       label: str
       template_name = "components/ui/button.html"

Required vs Optional Kwargs
---------------------------

Kwargs without default values are required:

.. code-block:: python

   @register
   class Button(Brick):
       label: str        # Required - must be provided
       variant: str = "primary"  # Optional - defaults to "primary"
       size: str | None = None   # Optional - defaults to None

Using required kwargs without providing them raises an error:

.. code-block:: html+django

   {# This will raise BrickValidationError #}
   {% button variant="secondary" %}

   {# This works #}
   {% button label="Click me" variant="secondary" %}

Block Bricks
------------

Block bricks can wrap content. Use ``BlockBrick`` as your base class:

.. code-block:: python

   from brickastley import BlockBrick, register

   @register
   class Card(BlockBrick):
       title: str
       subtitle: str | None = None

Create the template with a ``{{ children }}`` variable:

.. code-block:: html+django

   {# bricks/card.html #}
   <div class="card">
       <div class="card-header">
           <h2>{{ title }}</h2>
           {% if subtitle %}<h3>{{ subtitle }}</h3>{% endif %}
       </div>
       <div class="card-body">
           {{ children }}
       </div>
   </div>

Use it with an end tag:

.. code-block:: html+django

   {% card title="Welcome" subtitle="Getting started" %}
       <p>This is the card content.</p>
       <p>You can include any HTML here.</p>
       {% button label="Learn more" %}
   {% endcard %}

Next Steps
----------

- Learn about :doc:`advanced features <guide>` like Media classes and custom context
- Check out the :doc:`API reference <api>` for complete documentation
