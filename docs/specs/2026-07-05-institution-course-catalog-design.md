# Institution Course Catalog — Design Spec

## Goal

Let each Partner Institution curate its own subset of the course catalog — which Subjects it
recognizes under which Courses — instead of every institution implicitly sharing the entire
global `Subjects` table. Institution Admins can also add subjects that are private to their own
institution (never visible to other institutions).

## Background

Today `Subjects` is one global table (`subject_code` primary key, `subject_name`, `department`,
`category` — where `category` loosely stores a default course code). Every institution effectively
sees and can use the same ~90 rows. `CONTEXT.md` already carried draft glossary entries for
"Institution Course Catalog" and "Institution Catalog Entry" describing a curation-record concept;
this spec makes that concrete.

## Roles

- **Admin** (institution-scoped) manages their own institution's catalog — curate which global
  subjects they recognize, under which course, and create custom subjects private to their
  institution. This matches the existing pattern of every other Admin screen
  (`AdminTutorApplications.vue`, `AdminUsers.vue`, `AdminWithdrawals.vue`) being institution-scoped
  via `BaseAdminView.get_queryset_for_user`.
- **SuperAdmin** can view any institution's catalog (optional `institution_id` filter, matching the
  pattern already used by `AdminStatsView` and the Algorithm Demo Tool), but this pass does not add
  a SuperAdmin-specific catalog-editing UI — SuperAdmin uses the same screen with the institution
  filter, consistent with how other admin screens already behave for SuperAdmin.

## Data model

### `Subjects` (existing model, one new field)

```python
owning_institution = models.ForeignKey(
    PartnerInstitution, null=True, blank=True,
    on_delete=models.CASCADE, related_name='custom_subjects',
)
```

- `null` (the default for all ~90 seeded subjects today): a global/shared subject, visible to every
  institution.
- Set: a custom subject private to that institution. Only that institution's Admin can add it to
  their own catalog; no other institution can see or curate it.

### `InstitutionCourseCatalog` (new model)

```python
class InstitutionCourseCatalog(models.Model):
    institution = models.ForeignKey(PartnerInstitution, on_delete=models.CASCADE, related_name='catalog_entries')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='institution_catalog_entries')
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='institution_catalog_entries')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('institution', 'course', 'subject')
        ordering = ['course__course_code', 'subject__subject_code']

    def clean(self):
        if self.subject.owning_institution_id and self.subject.owning_institution_id != self.institution_id:
            raise ValidationError('A private subject can only be curated into its owning institution\'s catalog.')
```

One row = "this institution recognizes this Subject under this Course." `course` and `subject` are
independently chosen by the Admin (not forced to match `Subjects.category`) — this supports an
institution filing a subject under a differently-structured course than the platform default (e.g.
a merged program). The `clean()` guard prevents institution A from curating institution B's
private subject into its own catalog.

## API

All endpoints require `IsAuthenticated` + `IsAdminUser` (existing permission class in
`backend/studybuddy/permissions.py`, already allows `Admin` or `SuperAdmin`). Institution scoping
follows the existing `BaseAdminView.get_queryset_for_user` pattern.

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/api/admin/course-catalog/?course=<code>` | List the requester's institution's catalog entries, optional course filter. SuperAdmin may pass `institution_id`. |
| `POST` | `/api/admin/course-catalog/` | Create an entry `{course, subject}`, forced to the requester's own institution (SuperAdmin must pass `institution_id`). |
| `DELETE` | `/api/admin/course-catalog/<id>/` | Remove an entry; 403 if it doesn't belong to the requester's institution. |
| `POST` | `/api/admin/subjects/custom/` | Create a new `Subjects` row with `owning_institution` forced to the requester's own institution. Body: `{subject_code, subject_name, department}`. |

## Visibility fix (not scope creep — a correctness fix the new field requires)

`SubjectListView` (`backend/studybuddy/views.py:1857`, currently `Subjects.objects.all()`, backing
`catalog.js`'s `fetchSubjects()` used by Register.vue and other subject dropdowns platform-wide)
must filter to:

```python
Subjects.objects.filter(
    Q(owning_institution__isnull=True) | Q(owning_institution=request.user.userprofile.institution)
)
```

Without this, any institution's private custom subjects would appear in every other institution's
subject dropdowns immediately upon creation — a data leak directly caused by adding
`owning_institution`, not a matter of the deferred "full catalog enforcement" scope below.

## Frontend

- **New view**: `src/views/AdminCourseCatalog.vue` — Course dropdown (from `catalogStore.fetchCourses`),
  a checkbox list of subjects available to curate for the selected course (global subjects + this
  institution's own private subjects), and an "Add custom subject" form (code/name/department).
  Styled consistent with `AdminInstitutions.vue`'s table/card patterns.
- **Sidebar**: new item in the Admin role menu (`src/components/AppSidebar.vue:117-126`):
  `{ to: '/admin/course-catalog', label: 'Course Catalog', icon: 'bi-journal-bookmark' }`.
- **Router**: new route in `src/router/index.js` alongside the other `/admin/*` routes, same
  role guard as the existing Admin routes.
- **Store**: extend `src/stores/catalog.js` (or a new `institutionCatalog.js` store) with
  `fetchCourseCatalog`, `addCatalogEntry`, `removeCatalogEntry`, `addCustomSubject`.

## Reseed script alignment

`backend/studybuddy/management/commands/reset_demo_data.py` gets a new phase: after seeding the
global `Subjects` catalog, seed `InstitutionCourseCatalog` rows so **CPU and North University
curate visibly different subsets** — e.g. CPU recognizes its full course-appropriate subject set,
North University recognizes a deliberately smaller/different subset (and gets one seeded custom
subject unique to it) — so the curation feature is demonstrably exercised, not just built.

## Explicitly out of scope for this pass

- **No enforcement of the curated catalog anywhere else.** Register.vue's subject dropdown,
  `TutorSubjects` assignment, `Preference` selection, and the CBF recommender's subject matching
  continue reading from the global `Subjects` list (minus the visibility fix above, which is about
  private-subject leakage, not curation enforcement). Wiring "only show this institution's curated
  subjects" into every consumer is a separate follow-up plan.
- **No SuperAdmin-specific catalog-editing UI.** SuperAdmin uses the same Admin screen with the
  existing institution-filter pattern.
- **No editing of existing catalog entries** — only add/remove. An Admin who wants to change a
  course pairing removes and re-adds.

## Glossary updates

`CONTEXT.md`'s existing draft entries ("Institution Course Catalog", "Institution Catalog Entry")
get refined during implementation to reflect: `course`/`subject` are independently chosen (not
derived from `Subjects.category`), and a new **Custom Subject** term is added — a `Subjects` row
with `owning_institution` set, private to that institution, distinct from the ~90 global subjects.
