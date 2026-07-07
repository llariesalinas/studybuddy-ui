from django.db import migrations


def reactivate_cash_payment(apps, schema_editor):
    PaymentMethod = apps.get_model('studybuddy', 'PaymentMethod')
    PaymentMethod.objects.filter(code='CASH').update(is_active=True)


def deactivate_cash_payment(apps, schema_editor):
    PaymentMethod = apps.get_model('studybuddy', 'PaymentMethod')
    PaymentMethod.objects.filter(code='CASH').update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0069_alter_platformactivity_activity_type'),
    ]

    operations = [
        migrations.RunPython(reactivate_cash_payment, deactivate_cash_payment),
    ]
