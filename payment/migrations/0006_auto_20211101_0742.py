# Generated by Django 3.2.8 on 2021-11-01 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20211031_1018'),
        ('payment', '0005_alter_orderitem_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.productoption'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='payment.order'),
        ),
    ]