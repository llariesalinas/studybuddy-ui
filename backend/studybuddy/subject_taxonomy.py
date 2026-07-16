"""The shared, user-facing subject taxonomy."""
import re


CATEGORIES = [
    'Mathematics & Data Sciences',
    'Natural Sciences',
    'Technology & Computer Science',
    'Business, Finance & Economics',
    'Humanities & Social Sciences',
    'Hobbies & Arts',
]

_OVERRIDES = {'C++': 'cpp', 'C#': 'csharp', 'C': 'c-language'}


def slugify_subject_code(name):
    """Return the stable wire-format code for a taxonomy subject."""
    name = str(name or '').strip()
    if name in _OVERRIDES:
        return _OVERRIDES[name]
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


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
