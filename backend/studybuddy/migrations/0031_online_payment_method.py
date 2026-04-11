from django.db import migrations, models


def add_online_payment_method(apps, schema_editor):
    PaymentMethod = apps.get_model('studybuddy', 'PaymentMethod')

    PaymentMethod.objects.update_or_create(
        code='online',
        defaults={
            'method_name': 'Online Payment',
            'is_active': True,
        },
    )

    PaymentMethod.objects.filter(code__in=['GCASH', 'BANK']).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0030_allow_rebooking_after_rejection'),
        ('studybuddy', '0023_merge_20260406_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='code',
            field=models.CharField(
                choices=[
                    ('CASH', 'Cash'),
                    ('GCASH', 'GCash'),
                    ('BANK', 'Bank Transfer'),
                    ('online', 'Online Payment'),
                ],
                max_length=20,
                unique=True,
            ),
        ),
        migrations.RunPython(add_online_payment_method, migrations.RunPython.noop),
    ]
