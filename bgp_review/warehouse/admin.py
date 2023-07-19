from django.contrib import admin
from django.utils.html import format_html
from .models import ASN, Domain
# Register your models here.

admin.site.disable_action('delete_selected')

@admin.register(ASN)
class ASNAdmin(admin.ModelAdmin):
    empty_value_display = ''
    list_display = ['ip_prefix',
                    'as_number',
                    'company',
                    'update',
                    'crawled']

    search_fields = ['ip_prefix']
    list_filter = ['update']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):

    def make_checked(self, request, queryset):
        updated = queryset.update(checked=True)
        self.message_user(request, "%s domain checked" % updated)
    make_checked.short_description = 'Mark domain as checked'

    def make_illegal(self, request, queryset):
        updated = queryset.update(illegal=True)
        self.message_user(request, "%s domain illegal" % updated)
    make_illegal.short_description = 'Mark domain as illegal'

    # def actions_html(self, obj):
    #     return format_html('<button class="button" type="button" onclick="activate_and_send_email({pk})">Activate</button>', pk=obj.pk)

    # actions_html.allow_tags = True
    # actions_html.short_description = "Actions"

    def pass_value(self):
        print(1)
        return True

    list_per_page = 50
    list_display = ['ip_prefix',
                    'ip',
                    'domain',
                    'record_type',
                    'match_ip',
                    'checked',
                    'illegal',
                    'as_number',
                    'last_update',
                    'add_date'
                    # 'actions_html'
                    ]
                    
    list_filter = ['match_ip', 'checked', 'record_type', 'illegal', 'last_update', 'ip_prefix']
    search_fields = ['ip_prefix', 'ip', 'domain']
    fields = ['as_number',
              'ip_prefix',
              'ip',
              'domain',
              'record_type',
              'match_ip',
              'checked',
              'illegal',
              ]
    
    actions = ['make_checked', 'make_illegal']


