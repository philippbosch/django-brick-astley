# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**django-brick-astley** is a Django library for creating reusable template components called "bricks". It provides a clean, declarative way to define self-contained UI components with their own templates, similar to React components but for Django templates.

## Architecture

- `src/brickastley/` - Main library code
  - `brick.py` - Core `Brick` base class that components inherit from
  - `registry.py` - Global registry for brick classes
  - `autodiscover.py` - Auto-discovers `bricks.py` modules in Django apps
  - `templatetags/brickastley.py` - Template tags (`{% brick %}`, `{% brickslot %}`)
  - `apps.py` - Django app configuration
- `tests/` - pytest test suite
- `example/` - Demo Django project showing usage
- `docs/` - Sphinx documentation

## Common Commands

Make sure to call all commands within the context of the virtualenv.

```bash
# Run tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test file
pytest tests/test_brick.py

# Run the example project
cd example && python manage.py runserver

# Build documentation
cd docs && sphinx-build -b html . _build/html

# Type checking
mypy src/

# Linting
flake8 src/

# Formatting
black src/ tests/
```

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Testing

- Tests use pytest with pytest-django
- Django test settings are in `tests/settings.py`
- Test templates are in `tests/templates/`
- Run `pytest` from the project root

## Code Style

- Follow PEP 8
- Use Black for formatting (line length 160)
- Use type hints where practical
- Keep brick implementations simple and focused

## Key Concepts

1. **Brick**: A reusable component defined as a Python class that inherits from `Brick`. Each brick has an associated template.

2. **Registry**: Bricks are registered globally and can be rendered by name in templates.

3. **Slots**: Bricks can define slots for nested content, allowing composition.

4. **Context**: Bricks receive and can access the parent template's context.
