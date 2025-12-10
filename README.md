# djenga

Reusable components to be used in Django templates.

## Installation

```bash
pip install djenga
```

## Usage

Add `djenga` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'djenga',
    # ...
]
```

## Example Project

This repository includes a Django demo project in the `example/` directory. To run it:

```bash
cd example
python -m venv .venv
source .venv/bin/activate
pip install -e ..
pip install Django
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see the example in action.

## Development

Clone the repository:

```bash
git clone https://github.com/philippbosch/djenga.git
cd djenga
```

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

Install in development mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```


## License

MIT
