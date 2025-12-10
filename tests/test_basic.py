import pytest
from django.test import TestCase


class BasicTestCase(TestCase):
    """Basic tests for the djenga package."""

    def test_app_config(self):
        """Test that the app is properly configured."""
        from django.apps import apps

        app_config = apps.get_app_config("djenga")
        assert app_config.name == "djenga"
        assert app_config.verbose_name == "Djenga"
