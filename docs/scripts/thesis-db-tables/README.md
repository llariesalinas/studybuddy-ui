# thesis-db-tables

Regenerates the **Database Structure** section of the thesis manuscript
(`Group7_Final Evaluation.docx`) from the live Django models.

See [the plan](../../plans/2026-08-05-thesis-database-structure-update.md) and
[the session summary](../../session-summaries/2026-08-05-thesis-database-structure-update-summary.md).

## What it does

Two edits to the manuscript, both driven from one data file:

1. **The table section.** Replaces every body element between the `Database Structure` and
   `Network Topology` Heading 2 paragraphs with 35 table blocks, cloning the formatting of the
   paragraphs and tables already in the document so the result renders identically.
2. **Figure 5, the ERD.** Regenerates the diagram from the same data and swaps it in, on its own
   landscape page.

The source document is opened read-only; output goes to a separate file.

## Public interface

Run in this order, from this directory:

```bash
python rewrite_section.py   # rebuild the table section  -> writes the output docx
python verify.py            # structure + untouched-regions check   (MUST run before insert_erd)
python crosscheck.py        # field names vs. live Django models
python build_erd.py         # render erd_studybuddy.png
python insert_erd.py        # swap the ERD in, on a landscape page  (edits the output in place)
python verify_erd.py        # image, size, section, table section intact
```

| Script | Run it to | Output |
| --- | --- | --- |
| `rewrite_section.py` | Rebuild the table section | Writes `Group7_Final Evaluation (updated DB tables).docx` |
| `verify.py` | Check structure and that untouched regions are untouched | `ALL CHECKS PASSED` or a problem list |
| `crosscheck.py` | Check field data against Django's model introspection | `ALL CHECKS PASSED` or a problem list |
| `build_erd.py` | Render the ERD | `erd_studybuddy.png`, 2850x1950 at 300 DPI |
| `insert_erd.py` | Swap the ERD into Figure 5 on a landscape page | Edits the output docx in place |
| `verify_erd.py` | Check the swap landed correctly | `ALL CHECKS PASSED` or a problem list |

`tables_data.py` is the data, not a script. It holds `BLOCKS` (the 35 table definitions) and
`INTRO`, and feeds both the table section and the ERD. **This is the file to edit when the schema
changes.**

**Order matters.** `verify.py` compares the output against the pristine source, so it must run
before `insert_erd.py` adds the section-break paragraphs. `insert_erd.py` edits the output in
place, so re-running `rewrite_section.py` discards the ERD and you must redo the last three steps.

## Layout constraints worth knowing

Both were established empirically from a Word PDF export of this specific manuscript, and are
recorded in comments at the point they are used:

- On the landscape page the usable body band is **y 0.91in to 7.59in**; the header and footer take
  the rest. The two-line caption occupies 0.92-1.44in.
- The figure paragraph inherits the manuscript's **double spacing**, and Word multiplies an inline
  drawing's whole line box by that factor. `insert_erd.py` single-spaces that one paragraph;
  without it a 6in image demands 12in and can never share a page with its caption.
- Figure height is capped at **5.6in** so caption and figure stay together. Raising it strands the
  caption on its own page.

## What it does NOT handle

- **Refreshing the figure and table lists.** LIST OF FIGURES and LIST OF TABLES are real Word `TOC`
  fields, so their page numbers are stale until someone opens the file and presses Ctrl+A then F9.
  The scripts cannot do this; Word must.
- **Anything outside the two edits above.** Chapter prose, other figures and references are never
  modified; `verify.py` asserts this.
- **Automatic discovery of new models.** Adding a model to `models.py` does not add a block.
  `crosscheck.py` fails with `UNDOCUMENTED MODELS`, telling you to add it to `tables_data.py`
  yourself. This is deliberate: the descriptions are written prose, not generated text.
- **Graph layout for the ERD.** Boxes are packed into balanced columns by module, and edges are
  routed through the gutters and drawn *underneath* the boxes so no line ever cuts through field
  text. The trade-off is that an edge crossing an intervening column is hidden behind it, so
  long-distance relationships are not always traceable by eye. Short-range ones are.
- **Editing the original manuscript.** By design there is no in-place mode for the source.

## Dependencies

- `python-docx`, `pillow` (`pip install python-docx pillow`)
- Django and the project's backend requirements, importable from
  `backend/` — `crosscheck.py` only loads the app registry and never connects to a database, so
  dummy values for the `DB_*` environment variables are enough.

## Paths

`SRC` and `DST` are hardcoded at the top of `rewrite_section.py` (and mirrored in the two check
scripts). They point at the manuscript in the user's Downloads folder, which is outside this repo.
Edit them if the manuscript moves.
