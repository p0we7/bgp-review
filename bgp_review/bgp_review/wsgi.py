"""
WSGI config for bgp_review project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

### monkey patching
from django.contrib.admin import utils
from warehouse.monkey_patching import display_for_field_mod

utils.display_for_field = display_for_field_mod
### monkey patching

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bgp_review.settings')

application = get_wsgi_application()
