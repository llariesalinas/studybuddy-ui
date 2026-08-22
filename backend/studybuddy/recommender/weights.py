"""Admin-tunable recommender weights.

The recommender has two groups of weights, each of whose members are normalised
together so the group sums to 1.0:

- ``hybrid`` - how much of the final score is content-based vs collaborative.
- ``cbf``    - what the content-based score itself is made of.

Summing to 1.0 is not cosmetic. Every CBF sub-score and the normalised CF score
lands in 0-1, so the group summing to 1.0 is the only reason a hybrid score is
itself 0-1 and therefore comparable between tutors. Weights totalling 1.2 would
silently rescale every score in the system without raising an error anywhere.

Rather than validate that, this module normalises: stored values are relative,
and dividing by the group total makes an invalid set non-existent rather than
merely rejected. See docs/plans/2026-08-19-dynamic-algorithm-weights.md.

Callers that loop over many tutors must call load_weights() ONCE per request and
pass the result down, never per tutor - the same contract target_categories has
in cbf.resolve_target_categories.
"""

import logging

logger = logging.getLogger(__name__)

GROUP_HYBRID = 'hybrid'
GROUP_CBF = 'cbf'

# The shipped values, and the fallback whenever a row is missing or a group is
# unusable. Insertion order is the display order the API and UI present.
DEFAULT_WEIGHTS = {
    GROUP_HYBRID: {
        'cbf': 0.70,
        'cf': 0.30,
    },
    GROUP_CBF: {
        'specific': 0.40,
        'general': 0.20,
        'expertise': 0.15,
        'course': 0.10,
        'year': 0.10,
        'level': 0.05,
    },
}


def normalize_group(values, group):
    """Scale one group's weights so they sum to 1.0.

    A group summing to 0 (every weight zeroed, or negatives cancelling out)
    cannot be scaled and would divide by zero, so it falls back to the defaults
    rather than returning all-zero weights - which would silently flatten every
    score in that group to 0 and rank every tutor identically.
    """
    total = sum(values.values())

    if total <= 0:
        logger.warning(
            "Algorithm weight group %r sums to %s; falling back to defaults.", group, total
        )
        values = DEFAULT_WEIGHTS[group]
        total = sum(values.values())

    return {key: value / total for key, value in values.items()}


def load_weights():
    """Return ``{group: {key: normalised_weight}}`` for every group.

    Missing rows fall back to their default, so the recommender keeps working
    before the seed migration runs and if a key is ever removed by hand. Unknown
    keys in the database are ignored - the code defines which components exist,
    the database only supplies their values.
    """
    from ..models import AlgorithmWeight

    stored = {}
    for weight in AlgorithmWeight.objects.all():
        stored.setdefault(weight.group, {})[weight.key] = weight.value

    return {
        group: normalize_group(
            {key: stored.get(group, {}).get(key, default) for key, default in defaults.items()},
            group,
        )
        for group, defaults in DEFAULT_WEIGHTS.items()
    }


def default_weights():
    """Normalised defaults, without touching the database.

    Used as the fallback when a scoring function is called without weights, so
    the recommender stays importable and testable with no database at all.
    """
    return {
        group: normalize_group(dict(defaults), group)
        for group, defaults in DEFAULT_WEIGHTS.items()
    }


# Display metadata, served by the API so the settings screen renders whatever the
# backend defines rather than keeping its own copy of the labels. Adding a
# component later is a default above plus an entry here.
GROUP_LABELS = {
    GROUP_HYBRID: {
        'label': 'Hybrid blend',
        'description': (
            'How much of the final score comes from content-based matching versus '
            'collaborative filtering.'
        ),
    },
    GROUP_CBF: {
        'label': 'Content-based match components',
        'description': 'What the content-based score itself is made of.',
    },
}

WEIGHT_LABELS = {
    GROUP_HYBRID: {
        'cbf': ('Content-based', 'subject, course and expertise match'),
        'cf': ('Collaborative', 'ratings from similar tutees'),
    },
    GROUP_CBF: {
        'specific': ('Specific', 'exact subject match'),
        'general': ('General', 'same-field match'),
        'expertise': ('Expertise', 'declared expertise level'),
        'course': ('Course', 'same course or strand'),
        'year': ('Year', 'year-level proximity'),
        'level': ('Level', 'teaching-level fit'),
    },
}
