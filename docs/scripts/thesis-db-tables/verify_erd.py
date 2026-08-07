# -*- coding: utf-8 -*-
"""Verify the ERD swap: right image, right size, landscape section, table section intact."""
import hashlib
import zipfile

from docx import Document
from docx.oxml.ns import qn

DOCX = r"C:\Users\ryand\Downloads\Group7_Final Evaluation (updated DB tables).docx"
NEW_IMAGE = "erd_studybuddy.png"
IMAGE_PART = "word/media/image5.png"
CAPTION = "Entity-Relationship Diagram (ERD) of StudyBuddy"
EMU = 914400

problems = []

# --- the image bytes are the ones we generated -----------------------------------------
want = hashlib.sha256(open(NEW_IMAGE, "rb").read()).hexdigest()
with zipfile.ZipFile(DOCX) as z:
    got = hashlib.sha256(z.read(IMAGE_PART)).hexdigest()
    n_media = len([n for n in z.namelist() if "/media/" in n or n.startswith("media/")])
print("Figure 5 image is the generated ERD: %s" % (want == got))
if want != got:
    problems.append("image bytes do not match erd_studybuddy.png")
print("image parts in package: %d (expected 32)" % n_media)
if n_media != 32:
    problems.append("image part count changed: %d" % n_media)

doc = Document(DOCX)
kids = list(doc.element.body.iterchildren())


def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


# --- the drawing is sized for a landscape page -----------------------------------------
cap_i = None
for i, el in enumerate(kids):
    if el.tag == qn("w:p") and CAPTION in ptext(el) and el.findall(qn("w:r")):
        if "PAGEREF" not in "".join(t.text or "" for t in el.iter(qn("w:instrText"))):
            cap_i = i
img_i = next(j for j in range(cap_i + 1, cap_i + 4)
             if kids[j].find(".//" + qn("w:drawing")) is not None)

for e in kids[img_i].iter():
    if e.tag.endswith("}extent"):
        w, h = int(e.get("cx")) / EMU, int(e.get("cy")) / EMU
        print("figure display size: %.2f x %.2f in" % (w, h))
        if not (8.0 < w < 9.6 and 5.4 < h < 6.6):
            problems.append("unexpected figure size %.2f x %.2f" % (w, h))

# --- the figure sits in a landscape section --------------------------------------------
before = kids[cap_i - 1].find(qn("w:pPr"))
after = kids[img_i + 1].find(qn("w:pPr"))


def orient(pPr):
    if pPr is None:
        return None
    sect = pPr.find(qn("w:sectPr"))
    if sect is None:
        return None
    pgSz = sect.find(qn("w:pgSz"))
    return pgSz.get(qn("w:orient")) or "portrait", \
        int(pgSz.get(qn("w:w"))), int(pgSz.get(qn("w:h")))


ob, oa = orient(before), orient(after)
print("section break before caption: %s" % (ob,))
print("section break after image:    %s" % (oa,))
if not ob or ob[0] != "portrait":
    problems.append("paragraph before the caption is not a portrait section break")
if not oa or oa[0] != "landscape":
    problems.append("paragraph after the image is not a landscape section break")
if ob and oa and not (ob[1] == oa[2] and ob[2] == oa[1]):
    problems.append("landscape page size is not the portrait size swapped")

# --- the 35-table section survived the edit --------------------------------------------
s = next(i for i, e in enumerate(kids)
         if e.tag == qn("w:p") and ptext(e).strip() == "Database Structure")
e_ = next(i for i, e in enumerate(kids)
          if i > s and e.tag == qn("w:p") and ptext(e).strip() == "Network Topology")
sect = kids[s + 1:e_]
n_tbl = sum(1 for el in sect if el.tag == qn("w:tbl"))
n_rows = sum(len(el.findall(qn("w:tr"))) - 1 for el in sect if el.tag == qn("w:tbl"))
print("Database Structure section: %d tables, %d field rows" % (n_tbl, n_rows))
if n_tbl != 35 or n_rows != 301:
    problems.append("table section damaged: %d tables / %d rows" % (n_tbl, n_rows))

print()
print("RESULT:", "ALL CHECKS PASSED" if not problems else "PROBLEMS")
for p in problems:
    print("  -", p)
