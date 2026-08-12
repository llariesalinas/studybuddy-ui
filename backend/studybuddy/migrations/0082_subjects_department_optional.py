# Generated for 2026-08-13 admin review panel Sub-Group work

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0081_strike_window_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjects',
            name='department',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
    ]
