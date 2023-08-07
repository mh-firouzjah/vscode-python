"""
The content of this module has been added to help vscode python extension in order to
visualize discovery and execution django tests like what it does for unittest or pytest
"""

import os
import re
import sys


def setup_django_env(manage_py_module='', root='.'):
    """Configures the Django environment to run Django tests.

    If Django is not installed or if manage.py can not be found, the function fails quietly.

    Args:
        manage_py_module (str): The path to manage.py module.

        root (str): The root directory of the Django project.

    Returns:
        None
    """

    # To avoid false positive ModuleNotFoundError from django.setup() due to missing current workspace in sys.path
    sys.path.insert(0, os.getcwd())

    try:
        import django
    except ImportError:
        return

    if not manage_py_module:
        manage_py_module = os.path.join(root, "manage.py")

    try:
        with open(manage_py_module, "r") as f:
            manage_py_module = f.readlines()
    except FileNotFoundError:
        return

    django_settings_module = None
    pattern = r"^os\.environ\.setdefault\((\'|\")DJANGO_SETTINGS_MODULE(\'|\"), (\'|\")(?P<settings_path>[\w.]+)(\'|\")\)$"
    for line in manage_py_module:
        matched = re.match(pattern, line.strip())
        if matched is not None:
            django_settings_module = matched.groupdict().get("settings_path", None)
            break

    if django_settings_module is None:
        return

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", django_settings_module)

    try:
        django.setup()
    except ModuleNotFoundError:
        return

    return