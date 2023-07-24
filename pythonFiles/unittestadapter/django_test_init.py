"""
This module sets up a Django environment to run Django tests.
"""

import os
import re
import sys


def setup_django_test_env(django_settings_module=None, root=None):
    """Configures the Django environment for running Django tests.

    If Django is not installed or if manage.py is not found, the function fails quietly.

    Args:
        django_settings_module (str): The value to be used to set `DJANGO_SETTINGS_MODULE` environment variable.
            If not provided, the function will look for `manage.py` in the specified `root` directory and extract
            the value of `DJANGO_SETTINGS_MODULE` from that.

        root (str): The root directory of the Django project.

    Returns:
        None
    """

    try:
        import django
    except ModuleNotFoundError:
        return

    sys.path.insert(0, os.getcwd())

    if django_settings_module is not None:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", django_settings_module)
        try:
            django.setup()
        except ModuleNotFoundError:
            # Here it means django_settings_module has no relative in items inside sys.path
            return
        return

    # The following block prevents the failure of test-plugin
    # In case if no django_settings_module is specified but there are some django tests
    try:
        with open(os.path.join(root, "manage.py"), "r") as manage_py:
            pattern = r"^os\.environ\.setdefault\((\'|\")DJANGO_SETTINGS_MODULE(\'|\"), (\'|\")(?P<settings_path>[\w.]+)(\'|\")\)$"
            for line in manage_py.readlines():
                pattern_matched = re.match(pattern, line.strip())
                if pattern_matched is not None:
                    django_settings_module = str(
                        pattern_matched.groupdict().get("settings_path", "")
                    )
                    os.environ.setdefault(
                        "DJANGO_SETTINGS_MODULE", django_settings_module
                    )
                    django.setup()
                    return

    except FileNotFoundError:
        return
