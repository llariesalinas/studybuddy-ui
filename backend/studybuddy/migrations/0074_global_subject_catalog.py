from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('studybuddy', '0073_delete_admin_account_request'),
    ]

    operations = [
        migrations.DeleteModel(
            name='InstitutionCourseCatalog',
        ),
        migrations.RemoveField(
            model_name='subjects',
            name='owning_institution',
        ),
    ]
