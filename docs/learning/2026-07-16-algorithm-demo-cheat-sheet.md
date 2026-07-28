# Algorithm demo cheat sheet — subjects taxonomy reseed

Private reference for the superadmin algorithm demo tool (Ranked List / Compare Pair tabs)
after `python manage.py reset_demo_data && python manage.py seed_data`. Every score below was
read directly from the seeded database on 2026-07-16 (not hand-calculated) — rerun the seed
with its fixed random seed (`20260716`) and these numbers reproduce exactly.

All accounts use the shared demo password `studybuddy123`. Every curated tutor's surname
starts with the next letter after the previous one (Aquino, Bautista, Cruz, Diaz, Elizalde /
Fernandez, Garcia, Herrera, Ignacio, Jimenez), so they're easy to pick out of the filler
population by eye.

## Curated tutors

| Key | Name | Login | Course/Year | Teaching level | Subjects (expertise) |
|---|---|---|---|---|---|
| T1 | Marisol Aquino | `t1.marisol.aquino@cpu.edu.ph` | BSCS, 4th yr | College | Python (5), Data Structures (4), Algorithms (4) |
| T2 | Benigno Bautista | `t2.benigno.bautista@cpu.edu.ph` | BSCS, 3rd yr | College | C++ (3), Web Development (3) |
| T3 | Corazon Cruz | `t3.corazon.cruz@cpu.edu.ph` | BSBA, 3rd yr | College | Financial Accounting (5), Microeconomics (4) |
| T4 | Domingo Diaz | `t4.domingo.diaz@cpu.edu.ph` | BSCS, 4th yr | College | Python (3) |
| T5 | Esperanza Elizalde | `t5.esperanza.elizalde@cpu.edu.ph` | SHS-STEM, grade 12 | High School | Python (5) |

## Curated tutees

| Key | Name | Login | Course/Year | Preferences |
|---|---|---|---|---|
| S1 | Felipe Fernandez | `s1.felipe.fernandez@cpu.edu.ph` | BSCS, 2nd yr | Python, SQL |
| S2 | Gloria Garcia | `s2.gloria.garcia@cpu.edu.ph` | BSCS, 2nd yr | Python, Algorithms |
| S3 | Hernan Herrera | `s3.hernan.herrera@cpu.edu.ph` | BSCS, 3rd yr | Python, Data Structures |
| S4 | Imelda Ignacio | `s4.imelda.ignacio@cpu.edu.ph` | BSCS, 1st yr | SQL, Web Development |
| S5 | Jacinto Jimenez | `s5.jacinto.jimenez@cpu.edu.ph` | BSBA, 2nd yr | Financial Accounting, Marketing |

## Demo script

Run these in the superadmin algorithm demo tool (Ranked List tab, tutee = S1 Felipe
Fernandez, requested subject = Python) unless noted otherwise.

### 1. Specific vs. General vs. unrelated, plus expertise and the level ceiling

S1 requests **Python**. Expected ranked order among the curated tutors, with the CBF score
each currently produces:

| Rank | Tutor | Score | Why |
|---|---|---|---|
| 1 | T1 Marisol Aquino | 0.9333 | Exact match on Python, expertise 5, same course (BSCS) as S1, adjacent year |
| 2 | T4 Domingo Diaz | 0.8733 | Exact match on Python, but expertise only 3 — the Expertise component (0.15 weight) is what separates T1 from T4 |
| 3 | T5 Esperanza Elizalde | 0.8333 | Exact match on Python at expertise 5 (as high as T1), but the **Level component drops to 0** — she teaches at High School level and S1 is a college student above her ceiling. Compare her breakdown to T1's: same Specific/Expertise scores, only Level and Course/Year differ |
| 4 | T2 Benigno Bautista | 0.49 | No Python — only C++ and Web Development, both in the same category (Technology & Computer Science) as Python. General match only, no Specific credit |
| 5 | T3 Corazon Cruz | 0.1 | No Technology & Computer Science subjects at all (Financial Accounting, Microeconomics — a different category and a different course/strand) — Specific and General both fail; only Course/Year/Level residue remains |

Use **Compare Pair** on T1 vs. T5 to show the level-ceiling mechanic directly: identical
Specific and Expertise sub-scores, but T5's Level cell reads 0 while T1's reads 1.

### 2. Course/strand affinity

Switch the tutee to **S5 Jacinto Jimenez**, request **Financial Accounting**. T3 Corazon Cruz
scores **0.95** — exact subject match, expertise 5, and same course (BSBA) as S5. This is the
counterpart to story 1: T3 was the worst match for a BSCS tutee, but the best match for a BSBA
tutee requesting her subject.

### 3. Same-course CF peer signal

S1's same-course (BSCS) peers — **S2 Gloria Garcia, S3 Hernan Herrera, S4 Imelda Ignacio** —
each rated T1 highly (5, 5, 4) and T2 modestly (3, 3, 2). None of them, and no filler tutee,
ever rated T1 or T2 — those eight ratings are the entire rating history for both tutors. In
**Compare Pair**, look at T1's and T2's neighbor lists: the same three BSCS names appear as
T1's top positive-similarity neighbors, reinforcing the same ranking the CBF side already
produced independently.

### 4. Everyone has a real rating history

Every seeded tutor (curated and filler, 155 total) has at least 3 ratings; every tutee except
S1 and S5 (who only appear as CF *raters*, not *ratees*, in this script — S1's own booking
history is deliberately the demo subject, not the demo evidence) has rated at least 2 tutors.
T1: 4.67 avg / 3 sessions. T2: 2.67 avg / 3 sessions — visibly lower, consistent with story 3.

## Where this comes from

- Formula and weights: `backend/studybuddy/recommender/cbf.py`
  (`W_SPECIFIC`/`W_GENERAL`/`W_EXPERTISE`/`W_COURSE`/`W_YEAR`/`W_LEVEL`,
  `TEACHING_LEVEL_MAX_YEAR`).
- Persona definitions and rating script: `backend/studybuddy/management/commands/seed_data.py`
  (`CURATED_TUTORS`, `CURATED_TUTEES`, `CURATED_RATINGS`, `FILLER_SUPPORT_RATINGS`).
- Regression test locking in story 1's ordering:
  `backend/studybuddy/tests.py::CuratedPersonaCbfOrderingTests`.
- Plan: `docs/plans/2026-07-16-subjects-taxonomy-reseed.md`.
