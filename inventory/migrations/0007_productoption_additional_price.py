# Generated by Django 3.2.8 on 2021-11-02 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20211031_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='productoption',
            name='additional_price',
            field=models.IntegerField(default=0, verbose_name='옵션 가격'),
            preserve_default=False,
        ),
    ]
