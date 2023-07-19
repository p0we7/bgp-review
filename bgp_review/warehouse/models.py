from django.db import models

# Create your models here.
class ASN(models.Model):
    prefix_url = models.CharField(max_length=255)
    ip_prefix = models.CharField(max_length=40)
    as_number = models.CharField(max_length=10, null=True, blank=True)
    company = models.CharField(max_length=255)
    crawled = models.BooleanField(default=False)
    update = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.ip_prefix
    


class Domain(models.Model):
    domain = models.CharField(max_length=255)
    ip = models.CharField(max_length=40)
    match_ip = models.BooleanField(default=False)
    record_type = models.CharField(max_length=5)
    ip_prefix = models.CharField(max_length=40)
    illegal = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    keyword = models.CharField(max_length=255, null=True)
    as_number = models.CharField(max_length=10)
    add_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ip_prefix']

    def illegal_icon(self):
        from django.utils.html import format_html
        from django.templatetags.static import static

        value = self.illegal
        icon_url = static('warehouse/img/icon-%s.svg' %
                        {True: 'illegal', False: 'regular', None: 'unknown'}[value])
        return format_html('<img src="{}" alt="{}">', icon_url, value)
        
    def __str__(self):
       return self.domain

    def __eq__(self, other):
        excluded_keys = '_state', 'add_date', 'last_update', 'checked', 'keyword', 'illegal', 'id'
        values = [(k,v) for k,v in self.__dict__.items() if k not in excluded_keys]
        
        others = [(k,v) for k,v in other.__dict__.items() if k not in excluded_keys]

        return values == others

    def to_dict(self):
        excluded_keys = '_state', 'add_date', 'last_update', 'checked', 'keyword', 'illegal', 'id'
        values = { k: v for k,v in self.__dict__.items() if k not in excluded_keys }
        return values




class Cookies(models.Model):
    cookies = models.TextField(max_length=255)
    update_time = models.DateTimeField(auto_now=True)