# Generated by Django 3.1.2 on 2020-11-21 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ksa_books_app', '0015_auto_20201121_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('0', 'Comment'), ('1', 'New offer'), ('2', 'Sold to user'), ('3', 'Sold to other'), ('4', 'New want')], max_length=1, null=True),
        ),
    ]