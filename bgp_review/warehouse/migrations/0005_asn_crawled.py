# Generated by Django 2.1.4 on 2018-12-19 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0004_cookies'),
    ]

    operations = [
        migrations.AddField(
            model_name='asn',
            name='crawled',
            field=models.BooleanField(default=False),
        ),
    ]
