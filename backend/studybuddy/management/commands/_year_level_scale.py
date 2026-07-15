import random


YEAR_RANGE_BY_COURSE = {
    'ELEMENTARY': (1, 6),
    'JUNIOR_HIGH': (7, 10),
    'SHS-STEM': (11, 12),
    'SHS-ABM': (11, 12),
    'SHS-HUMSS': (11, 12),
    'SHS-GAS': (11, 12),
    'BSCS': (13, 16),
    'BSIT': (13, 16),
    'BSBA': (13, 16),
}

# College year_level values are offset onto the unified scale (1st Year = 13, ...) so they
# never collide with the elementary/JHS/SHS ranges above. Derived from BSCS's lower bound so it
# stays in lockstep if that range ever changes, instead of a bare magic number elsewhere.
COLLEGE_YEAR_OFFSET = YEAR_RANGE_BY_COURSE['BSCS'][0] - 1


def random_year_level(course_code):
    return random.randint(*YEAR_RANGE_BY_COURSE[course_code])
