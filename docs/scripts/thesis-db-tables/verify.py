# -*- coding: utf-8 -*-
"""Verify the rewritten docx: section correct, everything else untouched."""
import zipfile
from docx import Document
from docx.oxml.ns import qn

from tables_data import BLOCKS

SRC = r"C:\Users\ryand\Downloads\Group7_Final Evaluation.docx"
DST = r"C:\Users\ryand\Downloads\Group7_Final Evaluation (updated DB tables).docx"
START, END = "Database Structure", "Network Topology"


def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def split(path):
    doc = Document(path)
    kids = list(doc.element.body.iterchildren())
    s = e = None
    for i, el in enumerate(kids):
        if el.tag != qn("w:p"):
            continue
        t = ptext(el).strip()
        if t == START and s is None:
            s = i
        elif t == END and s is not None and e is None:
            e = i
    return doc, kids, s, e


def signature(els):
    """Text + element-kind signature, used to prove untouched regions really are untouched."""
    out = []
    for el in els:
        if el.tag == qn("w:p"):
            out.append(("p", ptext(el)))
        elif el.tag == qn("w:tbl"):
            rows = el.findall(qn("w:tr"))
            out.append(("tbl", len(rows), tuple(ptext(r) for r in rows)))
        else:
            out.append((el.tag,))
    return out


src_doc, src_kids, s0, e0 = split(SRC)
dst_doc, dst_kids, s1, e1 = split(DST)

print("=" * 70)
print("REGIONS OUTSIDE THE SECTION")
print("=" * 70)
before_ok = signature(src_kids[:s0 + 1]) == signature(dst_kids[:s1 + 1])
after_ok = signature(src_kids[e0:]) == signature(dst_kids[e1:])
print("elements before+including heading: src=%d dst=%d  identical=%s"
      % (s0 + 1, s1 + 1, before_ok))
print("elements from 'Network Topology' on: src=%d dst=%d  identical=%s"
      % (len(src_kids) - e0, len(dst_kids) - e1, after_ok))

with zipfile.ZipFile(SRC) as z:
    src_media = sorted(n for n in z.namelist() if n.startswith("word/media/"))
with zipfile.ZipFile(DST) as z:
    dst_media = sorted(n for n in z.namelist() if n.startswith("word/media/"))
print("embedded media files: src=%d dst=%d  identical=%s"
      % (len(src_media), len(dst_media), src_media == dst_media))

print()
print("=" * 70)
print("NEW SECTION")
print("=" * 70)
sect = dst_kids[s1 + 1:e1]
tables = [el for el in sect if el.tag == qn("w:tbl")]
names = [ptext(el).strip() for el in sect
         if el.tag == qn("w:p") and ptext(el).strip().startswith("Table Name:")]
print("body elements: %d | tables: %d | 'Table Name:' lines: %d"
      % (len(sect), len(tables), len(names)))

# Walk the section pairing each block header with the table that follows it.
problems = []
idx = 0
cur = None
seen = []
for el in sect:
    if el.tag == qn("w:p"):
        t = ptext(el).strip()
        if t.startswith("Table Name:"):
            cur = t[len("Table Name:"):].strip()
    elif el.tag == qn("w:tbl"):
        rows = el.findall(qn("w:tr"))
        header = tuple(ptext(c).strip() for c in rows[0].findall(qn("w:tc")))
        body = len(rows) - 1
        seen.append((cur, body, header))

print()
print("%-3s %-48s %6s %6s  %s" % ("No", "Table Name", "doc", "expect", "header row"))
print("-" * 100)
for i, ((name, body, header), block) in enumerate(zip(seen, BLOCKS), start=1):
    expect = len(block["rows"])
    ok = (name == block["name"]) and (body == expect)
    if not ok:
        problems.append((i, name, block["name"], body, expect))
    if header != ("Field Name", "Type", "Description"):
        problems.append((i, "BAD HEADER", header, "", ""))
    print("%-3d %-48s %6d %6d  %s%s"
          % (i, name[:48], body, expect, header, "" if ok else "   <-- MISMATCH"))

print()
if len(seen) != len(BLOCKS):
    problems.append(("count", len(seen), len(BLOCKS), "", ""))
    print("COUNT MISMATCH: %d tables in doc, %d expected" % (len(seen), len(BLOCKS)))

total = sum(len(b["rows"]) for b in BLOCKS)
doc_total = sum(b for _, b, _ in seen)
print("total field rows: doc=%d expected=%d" % (doc_total, total))
print()
print("RESULT:", "ALL CHECKS PASSED" if (not problems and before_ok and after_ok
                                        and src_media == dst_media) else "PROBLEMS: %s" % problems)
