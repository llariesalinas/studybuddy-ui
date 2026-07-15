from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('studybuddy', '0072_convert_admin_to_superadmin'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AdminAccountRequest',
        ),
    ]
