# Generated by Django 3.2.8 on 2021-11-13 07:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_shoppingcartitem_option'),
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
