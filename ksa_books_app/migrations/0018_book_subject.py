# Generated by Django 3.1.2 on 2020-11-21 08:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ksa_books_app', '0017_auto_20201121_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ksa_books_app.subject', verbose_name='과목'),
        ),
    ]
