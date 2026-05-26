import decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0044_merge_chat_and_partnerinstitution_branches'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('session_credit', 'Session Credit'),
                    ('withdrawal', 'Withdrawal'),
                    ('withdrawal_reversal', 'Withdrawal Reversal'),
                    ('cashout_fee', 'Cash-Out Provider Fee'),
                    ('cashout_fee_reversal', 'Cash-Out Provider Fee Reversal'),
                    ('commission_deduction', 'Commission Deduction'),
                ],
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name='TutorPayoutAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination_type', models.CharField(choices=[('gcash', 'GCash'), ('bank', 'Bank Transfer')], max_length=10)),
                ('receiving_institution_id', models.CharField(max_length=100)),
                ('receiving_institution_name', models.CharField(max_length=150)),
                ('receiving_institution_code', models.CharField(blank=True, max_length=50)),
                ('provider', models.CharField(blank=True, default='', max_length=20)),
                ('account_number', models.CharField(max_length=50)),
                ('account_name', models.CharField(max_length=100)),
                ('bank_name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payout_accounts', to='studybuddy.tutor')),
            ],
            options={
                'ordering': ['-is_active', '-updated_at'],
            },
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='callback_received_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='net_amount',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='payout_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cash_outs', to='studybuddy.tutorpayoutaccount'),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='provider',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='provider_error_code',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='provider_error_message',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='provider_fee',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='provider_reference_number',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='provider_status',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='provider_wallet_transaction_id',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='rail',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
