---
title: Thesis Database Structure section update
date: 2026-08-05
status: Done
summary: Rewrote the Database Structure section of Group7_Final Evaluation.docx from 14 stale table blocks to 35 verified against models.py.
spec:
---

# Thesis Database Structure section update

## Status & Progress Summary

**Done** (2026-08-05). All 35 table blocks written to
`C:\Users\ryand\Downloads\Group7_Final Evaluation (updated DB tables).docx`. The original file was
never opened for write.

Verified by four independent checks, all passing:

- Document structure: 35 blocks, 301 field rows, every header row intact.
- Untouched regions: the 418 body elements up to and including the section heading, and the 80 from
  `Network Topology` onward, are text-and-kind identical to the source; all 32 image parts are
  byte-identical.
- Django cross-check: field names compared against `model._meta.get_fields()` via the live app
  registry. Zero missing, zero extra, across 34 mapped models. All 31 concrete models in the
  `studybuddy` app are documented.
- ERD swap: correct image bytes, 8.18 x 5.60in on a landscape section whose page size is the
  portrait size swapped, table section still 35/301. Confirmed by a Word PDF export.

**Scope extended the same day:** the user asked for the ERD as well, so Figure 5 was regenerated
too. It now shows all 35 tables with every field, on its own landscape page, rendered from the same
`tables_data.py` that drives the table section. Verified by converting the finished document to PDF
with Word and inspecting the rendered page: one landscape page, caption and figure together, image
8.18 x 5.60in.

Nothing is outstanding. Two things need a human:

- **Refresh the field-driven lists.** LIST OF FIGURES and LIST OF TABLES are Word `TOC` fields, so
  their page numbers are stale until someone opens the file and presses Ctrl+A then F9.
- **Eyeball the figures in Word.** The checks prove bytes and relationships are intact and the PDF
  export renders correctly, but a visual pass is cheap insurance.

## Goal

The thesis manuscript `C:\Users\ryand\Downloads\Group7_Final Evaluation.docx` documents 14 database
tables in its "Database Structure" section (Chapter 3, between "Tangible and Intangible Benefits"
and "Network Topology"). The built system has 31 concrete Django models. The section is both
incomplete and wrong in its details.

Bring the section into agreement with the actual schema, without touching anything else in the
document.

## Approach

Rewrite the section to 35 table blocks, each verified field-by-field against
`backend/studybuddy/models.py`, `backend/studybuddy/chat/models.py`, and
`backend/backend/settings.py`.

The 35 blocks:

- 29 concrete models in `studybuddy/models.py`
- 2 models in `studybuddy/chat/models.py` (ChatRoom, Message)
- `auth_users` (Django built-in, already documented)
- `preference_subjects` (auto-created M2M through table for `Preference.subjects`)
- 2 SimpleJWT blacklist tables (`token_blacklist` is in INSTALLED_APPS)

`ApplicationVerificationBase` and `DocumentRenewalReviewBase` are `abstract = True` and correctly
produce no tables. Their fields are inherited into the four concrete application/renewal models and
are listed there.

### Decisions (settled in a grilling session, 2026-08-05)

| Decision | Resolution |
| --- | --- |
| Scope | Full rewrite: correct all 14 existing blocks, add 21 new |
| Table naming | Conceptual snake_case (`user_profile`), not real Django names (`studybuddy_userprofile`) |
| Ordering | Grouped by module, renumbered 1-35 |
| Field depth | Every field, no omissions, including UI-state and idempotency columns |
| Constraints | New optional `Unique Constraint:` header line, only where one exists |
| Built-ins | `auth_users` + 2 JWT blacklist tables only; no django_q, sessions, permissions |
| Figure 5 (ERD) | Untouched. Mismatch reported to the user for manual redraw |
| Output | New file, original untouched |
| Navigation | One intro paragraph, no new sub-headings |

### Module grouping order

1. Identity and authentication: auth_users, token_blacklist_outstandingtoken,
   token_blacklist_blacklistedtoken, email_otp_challenge, partner_institution, institution_request,
   user_profile
2. Academic taxonomy: strand, course, subjects
3. Tutor profile: tutor, tutor_subjects, preference, preference_subjects
4. Scheduling: tutor_availability, tutor_availability_override
5. Bookings and sessions: booking, session_check_in, rating
6. Payments and wallet: payment_method, payment, wallet, transaction, withdrawal_request,
   wallet_top_up
7. Verification: tutor_application, tutor_document_renewal_review, tutee_application,
   tutee_document_renewal_review
8. Communication: chat_room, message, notification, support_ticket
9. System records: platform_activity, email_send_log

### Technique

`python-docx` surgery on the document body XML:

1. Locate the `Database Structure` Heading 2 paragraph and the `Network Topology` Heading 2
   paragraph.
2. Delete every body element strictly between them.
3. Insert the new paragraphs and tables in order, cloning paragraph styles from the originals and
   using the same `Table Grid` table style, so rendering is unchanged.
4. Save to a new file; the original is never opened for write.

## Steps

1. Extract and read the current section (done).
2. Read every model definition and record exact field names, types, defaults, choices, and
   constraints (done).
3. Write the plan (this file).
4. Build the block data structure: 35 blocks of {name, no, pk, fks, unique constraint, description,
   rows}.
5. Write the docx surgery script into the scratchpad.
6. Run it, producing `Group7_Final Evaluation (updated DB tables).docx` in Downloads.
7. Re-extract the output and diff the section against the source data to confirm all 35 blocks
   landed with correct field counts.
8. Confirm nothing outside the section changed: paragraph count before the heading, table count
   before the heading, image/relationship count, and the LIST OF TABLES entries.

## Risks

- **Style loss on inserted tables.** Mitigated by reusing the `Table Grid` style object already
  present in the document and cloning the header row formatting from an existing block.
- **Deleting too much.** The delete range is bounded by two Heading 2 paragraphs located by exact
  text. Verified by a paragraph/table census before and after.
- **Image corruption.** The 4.9MB document is mostly embedded images. python-docx preserves parts it
  does not touch; the original file is never written to, and the output is verified to still contain
  the same number of image relationships.
- **Figure 5 (ERD) will contradict the new section.** Accepted and flagged; out of scope by
  instruction.

## Checks to run

- Re-extract the output docx and print all 35 blocks; compare field counts against models.py.
- Assert body element count before the `Database Structure` heading is identical in source and
  output.
- Assert the number of image relationships is identical in source and output.
- Assert `Network Topology` and everything after it is byte-identical in text.

### Results (2026-08-05)

All passed. Scripts live in the session scratchpad:

| Script | Purpose | Result |
| --- | --- | --- |
| `rewrite_section.py` | Performs the surgery | 35 blocks, 301 field rows emitted |
| `verify.py` | Structure + untouched-region check | ALL CHECKS PASSED |
| `crosscheck.py` | Field names vs. live Django app registry | ALL CHECKS PASSED |

The cross-check is the meaningful one: it compares the documented field lists against
`model._meta.get_fields()` rather than against the data file used to write them, so it catches a
mistake in the transcription rather than just confirming the transcription was copied faithfully.

## Changelog

- **2026-08-05** — Plan created after a grilling session settled scope, naming, ordering, field
  depth, constraint handling, built-in coverage, ERD handling, output location and navigation.
  Implemented the same day: section rewritten from 14 to 35 blocks, all three verification scripts
  passing. Corrected a wording slip in the `booking` description ("constraint below" -> "constraint
  stated above") after reviewing the rendered output. Status moved Draft -> In Progress -> Done.
- **2026-08-05 (later)** — Scope extended on request to Figure 5, the ERD, which the original plan
  had deliberately excluded. Two decisions taken: show all 35 tables with every field (the user
  chose full detail over a keys-only diagram, having been told 301 rows would be dense), and give
  it a full landscape page. Wrote `build_erd.py` (Pillow, no Graphviz or downloads) and
  `insert_erd.py`, both fed by the same `tables_data.py`. Three defects found and fixed by
  inspecting real renders rather than assuming: key-marker glyphs rendered as tofu and were
  replaced with drawn shapes; a white halo intended to make edges traceable was erasing field text,
  so edges moved back underneath the boxes; and the figure kept landing on a page of its own,
  which turned out to be the manuscript's double spacing inflating the inline image's line box,
  fixed by single-spacing that one paragraph and capping the figure at 5.6in. Confirmed by
  converting the finished document to PDF with Word: one landscape page, caption and figure
  together. Plan stays Done.
