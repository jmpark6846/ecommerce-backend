# Generated by Django 3.2.8 on 2021-10-31 10:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_productoption_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingcartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='shoppingcartitem',
            name='option',
        ),
        migrations.DeleteModel(
            name='ShoppingCart',
        ),
        migrations.DeleteModel(
            name='ShoppingCartItem',
        ),
    ]
