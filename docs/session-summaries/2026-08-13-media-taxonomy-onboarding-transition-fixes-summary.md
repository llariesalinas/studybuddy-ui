# Media persistence, tutor-propose taxonomy, onboarding transition — session summary

Three unrelated bugs diagnosed and fixed in one debugging session (no feature plan — ad hoc fixes).

## 1. Deployed images 404 despite a correctly-mounted persistent disk

**Symptom:** uploaded images (school IDs, receipts, avatars) 404'd on the Render deployment even
after a persistent disk was attached and `MEDIA_ROOT` pointed at its mount path.

**Root cause:** `django.conf.urls.static.static()` has a built-in `settings.DEBUG` gate — it
returns an *empty* URL pattern list whenever `DEBUG` is `False`, regardless of how its result is
appended to `urlpatterns`. `DEBUG=False` on the production/demo deployment (intentional, for
production-style security) meant `/media/...` had zero routes registered, independent of the disk
or `MEDIA_ROOT` being correct — confirmed on the Render shell: the uploaded file was sitting
exactly where expected on `/var/data/media`, but no route served it.

**Fix (`backend/backend/urls.py`):** replaced `static(settings.MEDIA_URL, document_root=...)` with
a direct `re_path` wired to `django.views.static.serve`, which isn't gated by `DEBUG`.

**Verified:** `python manage.py check`; `resolve('/media/...')` with `DEBUG=False` explicitly set
resolves to `django.views.static.serve` (previously would have raised `Resolver404`).

**Not yet done:** deploy and re-test on Render; images uploaded before this fix are lost (they
landed on ephemeral storage due to an earlier `MEDIA_ROOT` misconfiguration in the same
investigation) and will need re-uploading.

## 2. Tutor "propose a subject" rejected admin-approved categories

**Symptom:** a tutor proposing a subject under "Spoken Languages" — a category an admin had
already approved via the review panel — got "Select a category from the taxonomy," even though
the category existed in the catalog.

**Root cause:** `propose_tutor_subject` (`backend/studybuddy/views.py`) still hardcoded
`if category not in TAXONOMY_CATEGORIES` — a third instance of the same hardcoded allowlist that
`docs/plans/2026-08-12-admin-review-panel-category-keywords-backdrop.md` had already found and
removed in two other places (`AdminTutorProposedSubjectDetailView.patch`,
`SubjectSerializer.validate_category`), per that plan's "derive categories dynamically, no fixed
allowlist" decision.

**Fix:** removed the check and the now-unused `TAXONOMY_CATEGORIES` import. Replaced
`test_proposal_rejects_unknown_category` with `test_proposal_accepts_a_category_outside_the_curated_taxonomy`;
added `test_proposal_rejects_empty_category` to keep the still-required non-empty check covered.
Documented as a third follow-up entry in the same plan file's changelog.

**Verified:** targeted test class (25 tests) and full backend suite (459 tests) both pass.

## 3. Tutor onboarding white-screens moving Preferences → Subjects (and would on any transition)

**Symptom:** clicking "Continue to Subjects" (and reproducibly "Continue to Verification") left
the page blank — only the app's background wash visible, no navbar, no card — until a hard
refresh. No console error, no failed network request.

**Root cause, found via live repro (registered a throwaway tutor account against the local dev
stack and drove the flow through `claude-in-chrome`):** `App.vue`'s route-level
`<Transition name="page" mode="out-in">` requires its child to render exactly one root element.
`TutorPreferenceSetup.vue`'s template had **two** root nodes (the `<TutorOnboardingShell>` and a
sibling course/year-picker modal `<div v-if="isCourseYearModalOpen">`) — introduced by the
"collect course and year level during tutor onboarding" commit. Vue warned `Component inside
<Transition> renders non-element root node that cannot be animated`, and — confirmed by disabling
the Transition entirely, which fixed the blank page — `mode="out-in"`'s strict
leave-then-enter sequencing got stuck on that multi-root leave, dropping the incoming component
without ever mounting it (no `onMounted`, no network calls, no error).

**Fix:**
- `TutorPreferenceSetup.vue` — wrapped the whole template in a single root `<div>` so the
  component satisfies `<Transition>`'s single-root-element requirement (this alone silenced the
  Vue warning but was not sufficient on its own to fix the hang).
- `App.vue` — dropped `mode="out-in"` from the route transition (kept `<Transition name="page">`,
  same CSS classes/timing, just without the strict sequential leave-then-enter that was getting
  stuck). Confirmed by isolation testing: removing `<Transition>` entirely fixed it; removing only
  `mode="out-in"` also fixed it and preserves the fade/slide animation for every other public
  route (login, register, etc.).

**Verified:** live repro of both Preferences→Subjects and Subjects→Verify transitions, clean
(no warnings) after the fix; `npm run lint` (4 pre-existing, unrelated errors in
`make_algo_pptx.cjs`/`.js`); `npm run build` — passed.

**Not done / flagged:** removing `mode="out-in"` app-wide means entering and leaking pages now
transition simultaneously (a brief cross-fade) instead of sequentially everywhere, not just on the
onboarding routes. Not spot-checked across every public route (home, login, register, forgot/reset
password) for visual regressions — worth a quick pass if the app-wide feel matters.
