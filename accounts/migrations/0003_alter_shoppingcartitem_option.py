# Generated by Django 3.2.8 on 2021-11-01 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20211031_1018'),
        ('accounts', '0002_shoppingcart_shoppingcartitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcartitem',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.productoption'),
        ),
    ]
