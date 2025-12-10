API Reference
=============

This page documents the public API of django-brick-astley.

Core Classes
------------

Brick
~~~~~

.. py:class:: brickastley.Brick

   Base class for simple (self-closing) bricks.

   Bricks are reusable template components defined as Python classes with
   type-annotated kwargs. They are automatically registered as Django template
   tags when decorated with ``@register``.

   **Class Attributes:**

   .. py:attribute:: template_name
      :type: str | None

      Custom template path. If not set, defaults to ``bricks/<brick_name>.html``.

   .. py:attribute:: brick_name
      :type: str | None

      Custom template tag name. If not set, derived from class name using snake_case.

   **Instance Methods:**

   .. py:method:: get_brick_name() -> str
      :classmethod:

      Get the template tag name for this brick.

      :returns: The snake_case name derived from the class name, or the custom
                ``brick_name`` if set.

   .. py:method:: get_template_name() -> str
      :classmethod:

      Get the template path for this brick.

      :returns: The custom ``template_name`` if set, otherwise ``bricks/<brick_name>.html``.

   .. py:method:: get_context_data(**kwargs) -> dict[str, Any]

      Get the template context for rendering.

      Override this method to add computed values or transform kwargs before
      they're passed to the template.

      :param kwargs: Additional context variables to include.
      :returns: Dictionary of context variables for the template.

   .. py:method:: render() -> str

      Render the brick to an HTML string.

      :returns: The rendered HTML.

   **Example:**

   .. code-block:: python

      from brickastley import Brick, register

      @register
      class Alert(Brick):
          message: str
          level: str = "info"

          def get_context_data(self, **kwargs):
              context = super().get_context_data(**kwargs)
              context["icon"] = {
                  "info": "ℹ️",
                  "success": "✅",
                  "warning": "⚠️",
                  "error": "❌",
              }.get(self.level, "")
              return context


BlockBrick
~~~~~~~~~~

.. py:class:: brickastley.BlockBrick

   Base class for block bricks that can wrap content.

   Inherits from :py:class:`Brick`. Block bricks are used for components that
   wrap other content, like cards, modals, or accordions.

   **Instance Methods:**

   .. py:method:: render(children: str = "") -> str

      Render the brick with children content.

      :param children: The rendered content between the opening and closing tags.
      :returns: The rendered HTML with children inserted.

   **Example:**

   .. code-block:: python

      from brickastley import BlockBrick, register

      @register
      class Modal(BlockBrick):
          title: str
          size: str = "medium"

   **Template (bricks/modal.html):**

   .. code-block:: html+django

      <div class="modal modal--{{ size }}">
          <div class="modal-header">
              <h2>{{ title }}</h2>
          </div>
          <div class="modal-body">
              {{ children }}
          </div>
      </div>

   **Usage:**

   .. code-block:: html+django

      {% modal title="Confirm Action" size="small" %}
          <p>Are you sure you want to proceed?</p>
          {% button label="Cancel" %}
          {% button label="Confirm" variant="primary" %}
      {% endmodal %}


BrickValidationError
~~~~~~~~~~~~~~~~~~~~

.. py:exception:: brickastley.BrickValidationError

   Raised when brick kwargs fail validation.

   This exception is raised when:

   - A required kwarg is missing
   - An unknown kwarg is provided
   - A kwarg has the wrong type (only in DEBUG mode)

   **Example:**

   .. code-block:: python

      from brickastley import Brick, BrickValidationError

      class Button(Brick):
          label: str

      try:
          Button()  # Missing required 'label'
      except BrickValidationError as e:
          print(e)  # "Missing required kwarg 'label' for brick 'Button'"


Decorator
---------

register
~~~~~~~~

.. py:decorator:: brickastley.register(cls=None, *, name=None)

   Register a brick class as a template tag.

   Can be used with or without arguments:

   .. code-block:: python

      # Without arguments - uses class name for tag
      @register
      class Button(Brick):
          label: str

      # With custom name
      @register(name="btn")
      class Button(Brick):
          label: str

   :param cls: The brick class (when used without parentheses).
   :param name: Optional custom name for the template tag.
   :returns: The original class, unchanged.
   :raises ValueError: If a different class is already registered with the same name.


Registry Functions
------------------

.. py:function:: brickastley.registry.get_registry() -> dict[str, type[Brick]]

   Get the global brick registry.

   :returns: Dictionary mapping brick names to brick classes.

   **Example:**

   .. code-block:: python

      from brickastley.registry import get_registry

      for name, cls in get_registry().items():
          print(f"{name}: {cls.__name__}")


.. py:function:: brickastley.registry.get_brick(name: str) -> type[Brick] | None

   Get a brick class by its registered name.

   :param name: The registered name of the brick.
   :returns: The brick class, or None if not found.

   **Example:**

   .. code-block:: python

      from brickastley.registry import get_brick

      ButtonClass = get_brick("button")
      if ButtonClass:
          button = ButtonClass(label="Click")


.. py:function:: brickastley.registry.clear_registry() -> None

   Clear the brick registry.

   Primarily useful for testing to ensure a clean state between tests.

   **Example:**

   .. code-block:: python

      import pytest
      from brickastley.registry import clear_registry

      @pytest.fixture(autouse=True)
      def clean_registry():
          clear_registry()
          yield
          clear_registry()


Autodiscovery
-------------

.. py:function:: brickastley.autodiscover.autodiscover() -> None

   Auto-discover ``bricks.py`` modules in all installed Django apps.

   This function is called automatically when the brickastley app is ready.
   You typically don't need to call it manually unless you're writing tests
   or have a custom setup.

   The function:

   1. Iterates through all installed Django apps
   2. Checks if each app has a ``bricks.py`` submodule
   3. Imports the module to trigger ``@register`` decorators

   :raises ImportError: If a ``bricks.py`` module exists but fails to import.


Template Tags
-------------

After loading the template library with ``{% load brickastley %}``, all registered
bricks become available as template tags.

Simple Brick Tags
~~~~~~~~~~~~~~~~~

Simple bricks are self-closing tags:

.. code-block:: html+django

   {% brick_name kwarg1="value" kwarg2=variable %}

**Kwarg Value Types:**

- Strings: ``kwarg="value"`` or ``kwarg='value'``
- Integers: ``kwarg=42`` or ``kwarg=-5``
- Floats: ``kwarg=3.14``
- Booleans: ``kwarg=True`` or ``kwarg=False``
- None: ``kwarg=None``
- Variables: ``kwarg=my_var`` or ``kwarg=object.attribute``

Block Brick Tags
~~~~~~~~~~~~~~~~

Block bricks wrap content and require an end tag:

.. code-block:: html+django

   {% brick_name kwarg="value" %}
       Content goes here...
   {% endbrick_name %}

The content between the tags is rendered and passed to the template as
the ``{{ children }}`` variable.
