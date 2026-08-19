from django.db import migrations

# Frozen copies of the constants as they stood when the weights became editable.
# Deliberately NOT imported from studybuddy.recommender.weights: a migration must
# describe a fixed point in history, and importing live code would mean a future
# edit to the defaults retroactively changed what this migration seeds on a fresh
# database. See docs/plans/2026-08-19-dynamic-algorithm-weights.md.
SEEDED_WEIGHTS = {
    'hybrid': {
        'cbf': 0.70,
        'cf': 0.30,
    },
    'cbf': {
        'specific': 0.40,
        'general': 0.20,
        'expertise': 0.15,
        'course': 0.10,
        'year': 0.10,
        'level': 0.05,
    },
}


def seed_weights(apps, schema_editor):
    """Seed the eight weights from the values that were hardcoded before this.

    Behaviour must be identical on deploy: these are the same numbers the module
    constants held, so the first request after migrating scores exactly as the
    last request before it.
    """
    AlgorithmWeight = apps.get_model('studybuddy', 'AlgorithmWeight')

    for group, defaults in SEEDED_WEIGHTS.items():
        for key, value in defaults.items():
            AlgorithmWeight.objects.update_or_create(
                group=group, key=key, defaults={'value': value}
            )


def unseed_weights(apps, schema_editor):
    AlgorithmWeight = apps.get_model('studybuddy', 'AlgorithmWeight')
    AlgorithmWeight.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0083_algorithmweight'),
    ]

    operations = [
        migrations.RunPython(seed_weights, unseed_weights),
    ]
