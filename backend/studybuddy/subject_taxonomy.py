"""The shared, user-facing subject taxonomy."""
import re


# The category a subject falls back to when its own category is deleted, and the value the
# migration backfills over legacy NULL/'' categories. It is seeded with is_system=True so it can
# never be deleted -- the fallback target has to outlive everything that points at it.
UNCATEGORIZED_CATEGORY = 'Uncategorized'

# Categories are seeded 10, 20, 30... rather than 1, 2, 3 so a new one can be wedged between two
# existing ones without renumbering the rest.
CATEGORY_ORDER_STEP = 10

# Sorts the fallback last, behind any category an admin adds later.
UNCATEGORIZED_DISPLAY_ORDER = 999

# Seed fixture for the SubjectCategory table, not the runtime source of truth -- once seeded, the
# table owns the list and admins can add to it. Order here is the authored picker order, so append
# rather than prepend: seed_data uses CATEGORIES[:1] as its default course affinity.
CATEGORIES = [
    'Mathematics & Data Sciences',
    'Natural Sciences',
    'Technology & Computer Science',
    'Business, Finance & Economics',
    'Humanities & Social Sciences',
    'Hobbies & Arts',
    'Sports',
    UNCATEGORIZED_CATEGORY,
]


def seed_display_order(name):
    """Return the seeded display_order for a taxonomy category."""
    if name == UNCATEGORIZED_CATEGORY:
        return UNCATEGORIZED_DISPLAY_ORDER
    return (CATEGORIES.index(name) + 1) * CATEGORY_ORDER_STEP

# Subjects.subject_code is a CharField(max_length=20); names whose plain slug would exceed
# that get an explicit short form here so the code stays readable rather than a raw truncation.
_OVERRIDES = {
    'C++': 'cpp',
    'C#': 'csharp',
    'C': 'c-language',
    'Differential Equations': 'diff-equations',
    'Human Anatomy & Physiology': 'human-anatomy',
    'Environmental Science': 'env-science',
    'Artificial Intelligence': 'artificial-intel',
    'Managerial Accounting': 'mgmt-accounting',
    'Human Resource Management': 'hr-management',
    'Operations Management': 'ops-management',
    'International Relations': 'intl-relations',
}

SUBJECT_CODE_MAX_LENGTH = 20


def slugify_subject_code(name):
    """Return the stable wire-format code for a taxonomy subject.

    Always <= SUBJECT_CODE_MAX_LENGTH (the Subjects.subject_code column width).
    """
    name = str(name or '').strip()
    if name in _OVERRIDES:
        return _OVERRIDES[name]
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug[:SUBJECT_CODE_MAX_LENGTH].rstrip('-')


_GROUPS = {
    'Mathematics & Data Sciences': {
        'Core Math': 'Pre-Algebra, Algebra, Geometry, Trigonometry, Pre-Calculus',
        'Advanced & Pure Math': 'Calculus, Linear Algebra, Abstract Algebra, Differential Equations, Discrete Mathematics, Number Theory',
        'Applied Math & Statistics': 'Statistics, Biostatistics, Probability, Data Analysis, Regression Analysis, Actuarial Science',
        'Grade Levels': 'Elementary Math, High School Math, College Mathematics',
    },
    'Natural Sciences': {
        'Physics': 'Classical Mechanics, Thermodynamics, Electromagnetism, Quantum Mechanics, Astrophysics, Relativity, Optics',
        'Chemistry': 'General Chemistry, Organic Chemistry, Inorganic Chemistry, Physical Chemistry, Biochemistry, Analytical Chemistry',
        'Biology': 'Molecular Biology, Genetics, Cell Biology, Human Anatomy & Physiology, Microbiology, Zoology, Botany, Marine Biology',
        'Earth & Environmental Sciences': 'Ecology, Geology, Meteorology, Environmental Science, Paleontology',
    },
    'Technology & Computer Science': {
        'Programming Languages': 'Python, Java, JavaScript, C, C++, C#, Ruby, PHP, SQL, HTML & CSS',
        'Computer Science Theories': 'Algorithms, Data Structures, Machine Learning, Artificial Intelligence, Cybersecurity, Database Management, Software Engineering, Web Development',
    },
    'Business, Finance & Economics': {
        'Economics': 'Microeconomics, Macroeconomics, Econometrics, Behavioral Economics, International Trade',
        'Accounting & Finance': 'Financial Accounting, Managerial Accounting, Corporate Finance, Personal Finance, Investment Banking, Auditing',
        'Business & Management': 'Marketing, Human Resource Management, Operations Management, Entrepreneurship, Project Management, Strategic Management',
    },
    'Humanities & Social Sciences': {
        'History': 'World History, European History, American History, Ancient History, Art History, Military History',
        'Social Sciences': 'Psychology, Sociology, Anthropology, Political Science, International Relations',
        'Law': 'Constitutional Law, Corporate Law, International Law, Criminal Law, Legal Writing',
        'Literature & Writing': 'Literary Analysis, Creative Writing, Academic Writing, Essay Editing, Rhetoric, Journalism',
        'Philosophy': 'Ethics, Logic, Epistemology, Metaphysics, Political Philosophy',
    },
    'Hobbies & Arts': {
        'Music Theory & Instruments': 'Music Theory, Solfege, Ear Training, Piano, Guitar, Violin, Drums, Music Production',
        'Visual Arts': 'Digital Art, Fine Art, Painting, Graphic Design, Photography',
    },
}

SUBJECTS = [
    (name, category, subgroup)
    for category, subgroups in _GROUPS.items()
    for subgroup, names in subgroups.items()
    for name in names.split(', ')
]
