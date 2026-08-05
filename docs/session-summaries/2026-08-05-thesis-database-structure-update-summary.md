# Thesis Database Structure section update — session summary

**Date:** 2026-08-05
**Plan:** [2026-08-05-thesis-database-structure-update.md](../plans/2026-08-05-thesis-database-structure-update.md)
**Status:** Done

## What shipped

Two edits to the thesis manuscript `C:\Users\ryand\Downloads\Group7_Final Evaluation.docx`:

1. The **Database Structure** section rewritten from **14 table blocks to 35**, every field
   verified against the real Django models.
2. **Figure 5, the ERD**, regenerated to match — all 35 tables with every field, on its own
   landscape page.

Both are driven from a single data file, so the diagram and the table section cannot drift apart.

Output: `C:\Users\ryand\Downloads\Group7_Final Evaluation (updated DB tables).docx`. The original
was never opened for write.

No application code changed. This was a documentation-only session.

## Why it was needed

The documented schema had drifted badly from the built system:

- **19 tables were missing entirely** — the entire wallet/compensation module (`wallet`,
  `transaction`, `withdrawal_request`, `wallet_top_up`), verification
  (`tutor_application`, `tutee_application` and their renewal-review tables), communication
  (`chat_room`, `message`, `notification`, `support_ticket`), institutional multi-tenancy
  (`partner_institution`, `institution_request`), and system records (`platform_activity`,
  `email_send_log`, `email_otp_challenge`, `tutor_availability_override`, `session_check_in`).
- The 14 that existed had **wrong primary keys, missing foreign keys, and missing fields**. The
  `auth_users` block claimed `Primary Key: activity_id`. The `booking` block listed 8 fields; the
  model has 20, and omitted the `subject` foreign key entirely.
- Chapters 3 and 5 already made claims the schema section could not support — the double-booking
  constraint, the commission and wallet flow, chat rooms and support tickets. **The prose was
  ahead of the tables.** This work made the tables catch up; it did not introduce new claims.

## Decisions (settled by grilling before any edit)

| Decision | Resolution |
| --- | --- |
| Scope | Full rewrite: correct all 14, add 21 |
| Table naming | Conceptual snake_case (`user_profile`), matching the existing doc and the ERD figure |
| Ordering | Grouped into nine modules, renumbered 1-35 |
| Field depth | Every field, no omissions, including UI-state and idempotency columns |
| Constraints | New optional `Unique Constraint:` header line, only where one exists |
| Built-ins | `auth_users` + the two SimpleJWT blacklist tables; no django_q, sessions, permissions |
| Figure 5 (ERD) | Left untouched, mismatch reported |
| Output | New file; original untouched |
| Navigation | One intro paragraph, no new sub-headings |

## Deviations from the plan

One, minor: the `booking` description originally read "the unique constraint below", but the
`Unique Constraint:` line renders *above* the description. Caught while reviewing the rendered
output and corrected to "stated above" before finalizing.

## Checks run

All three passing:

| Check | Result |
| --- | --- |
| Document structure | 35 blocks, 301 field rows, all header rows intact |
| Untouched regions | 418 body elements before the heading and 80 from `Network Topology` on are identical to source; all 26 embedded media files unchanged |
| Django cross-check | Field names compared against `model._meta.get_fields()` via the live app registry — zero missing, zero extra across 34 mapped models; all 31 concrete `studybuddy` models documented |

The third check is the one that matters: it compares the document against Django's own
introspection rather than against the data file used to generate it, so it would catch a
transcription error rather than merely confirming the transcription was copied faithfully.

Scripts are preserved in [`docs/scripts/thesis-db-tables/`](../scripts/thesis-db-tables/) so the
section can be regenerated if the models change again.

### One incidental change, checked and cleared

Saving through `python-docx` re-serializes the whole package, so several XML parts differ at byte
level even though only `word/document.xml` was edited. All were canonicalized and compared:

- `footer1`, `header1`, `numbering`, `settings`, `styles`, `comments`, `[Content_Types]`, the `.rels`
  files and `docProps/core` are **identical after canonicalization** — whitespace and attribute
  ordering only.
- **All 32 image parts are byte-identical**, and none are missing. (The package stores 26 under
  `word/media/` and 6 under a root-level `media/`.)
- The one real change: six image relationships used an absolute target (`/media/image21.png` …
  `image26.png`) and were rewritten to the equivalent relative form (`../media/image21.png`). From
  the base of `word/document.xml` both resolve to the same existing part, so this is equivalent, not
  a break. Every one of the six is referenced by `document.xml` in both files.

The output file is also 0.24MB smaller than the source purely from this re-serialization stripping
XML indentation whitespace; no content was dropped.

**Still worth doing before submission:** open the new file in Word and page through the figures.
The checks above prove the bytes and relationships are intact, but they do not prove Word renders
them, and that is cheap to confirm by eye.

## Scope extension: the ERD

The plan deliberately excluded Figure 5. The user then asked for it, so it was regenerated in the
same session.

The old ERD was worth looking at before replacing: 799x441px (~143 DPI at its display size), 13
entities, and it showed `TUTOR_WALLET`, `PAYMENTS`, `PAYOUT` and `PAYMENT_WEBHOOK_LOGS` — **none of
which were among the 14 documented tables**. The ERD and the table section had already disagreed
with each other, and neither matched the code.

Two decisions, both the user's:

- **All 35 tables with every field**, not a keys-only diagram. Chosen with the density trade-off
  stated up front.
- **Full-page landscape**, one page, so nothing else in the document renumbers.

Rendered with Pillow (`build_erd.py`) — no Graphviz or Mermaid, nothing downloaded. Boxes are
packed into six balanced columns by a linear-partition DP, grouped and colour-coded by the same
nine modules as the table section, with 58 foreign-key edges in crow's-foot notation.

### Three defects found by looking at real renders

None of these would have surfaced without inspecting the actual output:

1. **Key markers rendered as tofu.** Arial has no glyph for U+25C6/U+25C7 in this pipeline. Replaced
   with drawn polygons.
2. **A white halo was erasing field text.** Added to make edges traceable where they cross boxes,
   it visibly struck through `is_active` and `last_updated`. Edges moved back underneath the boxes,
   which is the right trade: text is never damaged, at the cost of long-distance edges being hidden
   behind intervening columns.
3. **The figure kept landing on a page of its own**, stranding the caption. Three wrong hypotheses
   (page height, margins, image size) were each tested and disproved by measurement before the real
   cause turned up: the manuscript is **double-spaced**, and Word multiplies an inline drawing's
   entire line box by the line-spacing factor, so a 6in image demands 12in. Fixed by single-spacing
   that one paragraph and capping the figure at 5.6in.

### ERD verification

`verify_erd.py` asserts the image bytes are the generated file, the display size is right, the
figure sits in a landscape section whose page size is the portrait size swapped, and the 35-table
section is undamaged. Beyond that, the finished document was **converted to PDF with Word** and the
rendered page inspected: one landscape page, caption and figure together, image 8.18 x 5.60in,
document 100 pages.

## Follow-up needed

1. **Refresh the lists.** LIST OF FIGURES and LIST OF TABLES are real Word `TOC` fields. Their
   cached page numbers are stale after adding ~20 pages of tables and a landscape page. Open the
   file, Ctrl+A, F9. Word does this; the scripts cannot.
2. **Page through the figures in Word.** The checks prove the bytes and relationships are intact
   and the PDF export renders correctly, but a visual pass costs a minute.
3. **Known limitation of the ERD.** Edges that cross an intervening column are hidden behind it, so
   long-distance relationships are not always traceable by eye. Every foreign key is still listed
   explicitly in the table section. If a panel wants fully traceable lines, the options are a
   two-page figure or a keys-only diagram.
