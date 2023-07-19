#!/usr/bin/env python
import os
import sys
from django.contrib.admin import utils
from warehouse.monkey_patching import display_for_field_mod

utils.display_for_field = display_for_field_mod

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bgp_review.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
