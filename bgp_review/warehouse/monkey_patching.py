
from django.utils.html import format_html
from django.templatetags.static import static
from django.utils import formats, timezone
from django.db import models
from django.contrib.admin.utils import display_for_value

def _boolean_icon_illegal(field_val):
    icon_url = static('admin/img/icon-%s.svg' %
                      {True: 'illegal', False: 'regular', None: 'unknown'}[field_val])
    return format_html('<img src="{}" alt="{}">', icon_url, field_val)


def display_for_field_mod(value, field, empty_value_display):
    from django.contrib.admin.templatetags.admin_list import _boolean_icon

    if getattr(field, 'flatchoices', None):
        return dict(field.flatchoices).get(value, empty_value_display)
    # BooleanField needs special-case null-handling, so it comes before the
    # general null test.
    elif isinstance(field, models.BooleanField):
        if field.name is 'illegal':
            return _boolean_icon_illegal(value)
        else:
            return _boolean_icon(value)
    elif value is None:
        return empty_value_display
    elif isinstance(field, models.DateTimeField):
        return formats.localize(timezone.template_localtime(value))
    elif isinstance(field, (models.DateField, models.TimeField)):
        return formats.localize(value)
    elif isinstance(field, models.DecimalField):
        return formats.number_format(value, field.decimal_places)
    elif isinstance(field, (models.IntegerField, models.FloatField)):
        return formats.number_format(value)
    elif isinstance(field, models.FileField) and value:
        return format_html('<a href="{}">{}</a>', value.url, value)
    else:
        return display_for_value(value, empty_value_display)

