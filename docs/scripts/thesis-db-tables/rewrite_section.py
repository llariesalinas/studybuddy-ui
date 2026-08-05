# -*- coding: utf-8 -*-
"""Replace the Database Structure section of the thesis docx with 35 verified table blocks.

Reads the original, never writes to it. Clones the formatting of the existing paragraphs and
tables so the new content renders identically to the old.
"""
import sys
from copy import deepcopy

from docx import Document
from docx.oxml.ns import qn

from tables_data import BLOCKS, INTRO

SRC = r"C:\Users\ryand\Downloads\Group7_Final Evaluation.docx"
DST = r"C:\Users\ryand\Downloads\Group7_Final Evaluation (updated DB tables).docx"

START_HEADING = "Database Structure"
END_HEADING = "Network Topology"


def para_text(p_el):
    return "".join(t.text or "" for t in p_el.iter(qn("w:t")))


def set_run_text(r_el, text):
    """Replace the text of a run, keeping its formatting (w:rPr)."""
    for child in list(r_el):
        if child.tag != qn("w:rPr"):
            r_el.remove(child)
    t = r_el.makeelement(qn("w:t"), {})
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r_el.append(t)


def clone_para(template, text):
    """Clone a paragraph element, collapsing it to a single run carrying `text`."""
    new = deepcopy(template)
    runs = new.findall(qn("w:r"))
    if not runs:
        raise RuntimeError("template paragraph has no runs")
    for r in runs[1:]:
        new.remove(r)
    # Drop anything that is not the paragraph mark or the surviving run
    # (bookmarks, proofErr, hyperlinks) so no stale content leaks through.
    for child in list(new):
        if child.tag not in (qn("w:pPr"), qn("w:r")):
            new.remove(child)
    set_run_text(new.findall(qn("w:r"))[0], text)
    return new


def set_cell_text(tc_el, text):
    """Set a table cell's text, keeping the first paragraph's and run's formatting."""
    paras = tc_el.findall(qn("w:p"))
    for p in paras[1:]:
        tc_el.remove(p)
    p = paras[0]
    runs = p.findall(qn("w:r"))
    if runs:
        for r in runs[1:]:
            p.remove(r)
        set_run_text(runs[0], text)
    else:
        r = p.makeelement(qn("w:r"), {})
        set_run_text(r, text)
        p.append(r)


def clone_table(template, rows):
    """Clone a table element, keeping its header row verbatim and re-filling the body.

    `rows` holds body rows only; the template's own "Field Name | Type | Description"
    header row is preserved so its formatting is untouched.
    """
    new = deepcopy(template)
    trs = new.findall(qn("w:tr"))
    if len(trs) < 2:
        raise RuntimeError("template table needs a header row and at least one body row")
    body_tpl = deepcopy(trs[1])
    for tr in trs[1:]:
        new.remove(tr)
    for row in rows:
        tr = deepcopy(body_tpl)
        tcs = tr.findall(qn("w:tc"))
        if len(tcs) != len(row):
            raise RuntimeError("column count mismatch: %d cells vs %d values" % (len(tcs), len(row)))
        for tc, value in zip(tcs, row):
            set_cell_text(tc, value)
        new.append(tr)
    return new


def main():
    doc = Document(SRC)
    body = doc.element.body
    children = list(body.iterchildren())

    # --- locate the section boundaries -------------------------------------------------
    start_i = end_i = None
    for i, el in enumerate(children):
        if el.tag != qn("w:p"):
            continue
        text = para_text(el).strip()
        if text == START_HEADING and start_i is None:
            start_i = i
        elif text == END_HEADING and start_i is not None and end_i is None:
            end_i = i
    if start_i is None or end_i is None:
        sys.exit("could not locate section boundaries: start=%r end=%r" % (start_i, end_i))

    section = children[start_i + 1:end_i]
    print("section spans %d body elements (indices %d..%d)" % (len(section), start_i + 1, end_i - 1))

    # --- capture formatting templates before deleting anything -------------------------
    para_tpl = None
    for el in section:
        if el.tag == qn("w:p") and para_text(el).strip().startswith("Table Name:"):
            para_tpl = deepcopy(el)
            break
    table_tpl = None
    for el in section:
        if el.tag == qn("w:tbl"):
            table_tpl = deepcopy(el)
            break
    if para_tpl is None or table_tpl is None:
        sys.exit("could not capture templates")

    n_tables_before = sum(1 for el in section if el.tag == qn("w:tbl"))
    print("captured templates; old section had %d tables" % n_tables_before)

    # --- delete the old section --------------------------------------------------------
    for el in section:
        body.remove(el)

    # --- rebuild -----------------------------------------------------------------------
    anchor = children[end_i]  # the "Network Topology" heading; insert before it

    def emit_para(text):
        anchor.addprevious(clone_para(para_tpl, text))

    def emit_table(rows):
        anchor.addprevious(clone_table(table_tpl, rows))

    emit_para("Database Name: studybuddy_db")
    emit_para("")
    emit_para(INTRO)
    emit_para("")

    for n, block in enumerate(BLOCKS, start=1):
        emit_para("Table Name: %s" % block["name"])
        emit_para("Table No: %d" % n)
        emit_para("Primary Key: %s" % block["pk"])

        fks = block["fks"]
        if not fks:
            emit_para("Foreign Key: --")
        elif len(fks) == 1:
            emit_para("Foreign Key: %s" % fks[0])
        else:
            emit_para("Foreign Key:")
            for fk in fks:
                emit_para("    %s" % fk)

        if block["unique"]:
            emit_para("Unique Constraint: %s" % block["unique"])

        emit_para("Description:")
        emit_para(block["desc"])
        emit_table(block["rows"])
        emit_para("")

    doc.save(DST)
    print("wrote %s" % DST)
    print("emitted %d table blocks" % len(BLOCKS))
    print("total field rows: %d" % sum(len(b["rows"]) for b in BLOCKS))


if __name__ == "__main__":
    main()
