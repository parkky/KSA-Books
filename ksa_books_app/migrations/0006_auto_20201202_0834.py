# Generated by Django 3.1.3 on 2020-12-01 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ksa_books_app', '0005_auto_20201201_1229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='note_degree',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='note_explain',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='other',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='worn_degree',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='worn_explain',
        ),
        migrations.AddField(
            model_name='offer',
            name='explain',
            field=models.TextField(blank=True, null=True, verbose_name='내용'),
        ),
        migrations.AddField(
            model_name='offer',
            name='quality',
            field=models.CharField(choices=[('a', '상'), ('b', '중'), ('c', '하')], max_length=1, null=True, verbose_name='보관 상태'),
        ),
    ]
