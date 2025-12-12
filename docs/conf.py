# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import tomllib

# Add the src directory to the path so autodoc can find the modules
sys.path.insert(0, os.path.abspath("../src"))

# Read version from pyproject.toml
with open(os.path.join(os.path.dirname(__file__), "..", "pyproject.toml"), "rb") as f:
    pyproject = tomllib.load(f)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "django-brick-astley"
copyright = "2025, Philipp Bosch"
author = "Philipp Bosch"
release = pyproject["project"]["version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Support both reStructuredText and Markdown
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

# -- Options for autodoc -----------------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/stable/", "https://docs.djangoproject.com/en/stable/_objects/"),
}

# -- Options for MyST parser -------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
