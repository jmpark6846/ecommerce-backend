# Generated by Django 3.2.8 on 2021-11-02 07:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0009_auto_20211102_0725'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalPayment',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='결제금액')),
                ('status', models.SmallIntegerField(choices=[(0, 'Created'), (1, 'Paid'), (2, 'Payment Failed')], default=0)),
                ('payment_method', models.CharField(choices=[('transfer', 'Transfer'), ('kakaopay', 'Kakaopay'), ('naverpay', 'Naverpay')], max_length=20)),
                ('paid_at', models.DateTimeField(blank=True, editable=False)),
                ('error_message', models.CharField(max_length=140)),
                ('transfer_amount', models.IntegerField(blank=True, null=True, verbose_name='무통장입금 금액')),
                ('transfer_name', models.IntegerField(blank=True, null=True, verbose_name='무통장입금 입금자명')),
                ('transfer_bank', models.IntegerField(blank=True, null=True, verbose_name='무통장입금 은행')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payment.order')),
            ],
            options={
                'verbose_name': 'historical payment',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]