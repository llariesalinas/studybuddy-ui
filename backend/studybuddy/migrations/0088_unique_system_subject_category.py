from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('studybuddy', '0087_review_integrity')]

    # Keep the index in a separate transaction from 0087's subject FK updates:
    # PostgreSQL cannot create it while deferred FK trigger events remain pending.
    operations = [
        migrations.AddConstraint(
            model_name='subjectcategory',
            constraint=models.UniqueConstraint(
                fields=('is_system',), condition=models.Q(is_system=True),
                name='unique_system_subject_category',
            ),
        ),
    ]
