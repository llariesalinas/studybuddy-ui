"""Give subject categories their own table and repoint Subjects.category at it.

Categories used to exist only as free-text strings on Subjects rows, so a category with no
subjects could not be represented at all. This creates the table, seeds it from the taxonomy
fixture, backfills a row for every category string already in use (including ones admins added
that are not in the fixture), folds case variants together, maps legacy NULL/'' categories onto
Uncategorized, and finally makes the foreign key non-nullable.
"""
from django.db import migrations, models
import django.db.models.deletion
from django.db.models.functions import Lower

from studybuddy.models import get_uncategorized, get_uncategorized_id
from studybuddy.subject_taxonomy import (
    CATEGORIES,
    CATEGORY_ORDER_STEP,
    UNCATEGORIZED_CATEGORY,
    seed_display_order,
)


def seed_categories(apps, schema_editor):
    SubjectCategory = apps.get_model('studybuddy', 'SubjectCategory')
    for name in CATEGORIES:
        SubjectCategory.objects.get_or_create(
            name=name,
            defaults={
                'display_order': seed_display_order(name),
                'is_system': name == UNCATEGORIZED_CATEGORY,
            },
        )


def backfill_categories(apps, schema_editor):
    SubjectCategory = apps.get_model('studybuddy', 'SubjectCategory')
    Subjects = apps.get_model('studybuddy', 'Subjects')

    by_lowered_name = {c.name.lower(): c for c in SubjectCategory.objects.all()}
    uncategorized = by_lowered_name[UNCATEGORIZED_CATEGORY.lower()]

    # Admin-added categories sort after the seeded ones but ahead of the Uncategorized fallback.
    next_order = (len(CATEGORIES) + 1) * CATEGORY_ORDER_STEP

    for subject in Subjects.objects.all().iterator():
        name = (subject.category or '').strip()
        if not name:
            subject.category_fk = uncategorized
            subject.save(update_fields=['category_fk'])
            continue

        # First spelling encountered wins, so 'Sports' and 'sports' fold into one row rather than
        # tripping the case-insensitive unique constraint.
        category = by_lowered_name.get(name.lower())
        if category is None:
            category = SubjectCategory.objects.create(name=name, display_order=next_order)
            by_lowered_name[name.lower()] = category
            next_order += CATEGORY_ORDER_STEP

        subject.category_fk = category
        subject.save(update_fields=['category_fk'])


def restore_category_strings(apps, schema_editor):
    Subjects = apps.get_model('studybuddy', 'Subjects')
    for subject in Subjects.objects.all().iterator():
        subject.category = subject.category_fk.name if subject.category_fk else ''
        subject.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0084_seed_algorithm_weights'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False,
                                           verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_system', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'subject categories',
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.AddConstraint(
            model_name='subjectcategory',
            constraint=models.UniqueConstraint(Lower('name'),
                                               name='unique_subject_category_name_ci'),
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
        migrations.AddField(
            model_name='subjects',
            name='category_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='subjects', to='studybuddy.subjectcategory'),
        ),
        migrations.RunPython(backfill_categories, restore_category_strings),
        migrations.RemoveField(model_name='subjects', name='category'),
        migrations.RenameField(model_name='subjects', old_name='category_fk',
                               new_name='category'),
        migrations.AlterField(
            model_name='subjects',
            name='category',
            field=models.ForeignKey(default=get_uncategorized_id,
                                    on_delete=models.SET(get_uncategorized),
                                    related_name='subjects', to='studybuddy.subjectcategory'),
        ),
    ]
