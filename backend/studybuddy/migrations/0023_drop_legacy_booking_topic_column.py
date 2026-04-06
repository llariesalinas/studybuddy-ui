from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0022_partnerinstitution_userprofile_institution_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE studybuddy_booking DROP COLUMN IF EXISTS topic;',
            reverse_sql='ALTER TABLE studybuddy_booking ADD COLUMN topic varchar(255);',
        ),
    ]
