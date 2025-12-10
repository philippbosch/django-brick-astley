# brickastley-demo

Demo Django project for testing the `django-brick-astley` package.

## Setup

From the `example/` directory, create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

Install the local brickastley package in editable mode:

```bash
# Install brickastley from the parent directory
pip install -e ..

# Install Django
pip install Django
```

Run migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

## Using uv (faster alternative)

If you have [uv](https://github.com/astral-sh/uv) installed:

```bash
# Create virtual environment
uv venv

# Activate
source .venv/bin/activate

# Install brickastley in editable mode
uv pip install -e ..

# Install Django
uv pip install Django
```
