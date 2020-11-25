# Generated by Django 3.1.2 on 2020-11-15 01:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ksa_books_app', '0007_auto_20201112_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='buyer_done',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='seller_done',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='want_users',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]