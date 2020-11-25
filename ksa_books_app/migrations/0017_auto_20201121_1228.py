# Generated by Django 3.1.2 on 2020-11-21 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ksa_books_app', '0016_auto_20201121_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentuser',
            name='notify_comment',
            field=models.BooleanField(default=True, verbose_name='댓글이 달림'),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='notify_new_offer',
            field=models.BooleanField(default=True, verbose_name='원하는 책이 올라옴'),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='notify_new_want',
            field=models.BooleanField(default=True, verbose_name='새 구매 신청'),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='notify_sold_to_other',
            field=models.BooleanField(default=True, verbose_name='다른 사람에게 책을 판매함'),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='notify_sold_to_user',
            field=models.BooleanField(default=True, verbose_name='자신에게 책을 판매함'),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='notify_books',
            field=models.ManyToManyField(to='ksa_books_app.Book', verbose_name='알림을 받을 책'),
        ),
    ]