from django.db import migrations

def deactivate_cash_payment(apps, schema_editor):
    PaymentMethod = apps.get_model('studybuddy', 'PaymentMethod')
    PaymentMethod.objects.filter(code='CASH').update(is_active=False)

def reactivate_cash_payment(apps, schema_editor):
    PaymentMethod = apps.get_model('studybuddy', 'PaymentMethod')
    PaymentMethod.objects.filter(code='CASH').update(is_active=True)

class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0054_booking_dashboard_hidden_fields'),
    ]

    operations = [
        migrations.RunPython(deactivate_cash_payment, reactivate_cash_payment),
    ]
