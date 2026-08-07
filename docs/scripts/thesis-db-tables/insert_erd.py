# -*- coding: utf-8 -*-
"""Swap the regenerated ERD into Figure 5 and put it on its own landscape page.

Run AFTER rewrite_section.py and build_erd.py. Modifies the generated output file in place;
the user's original manuscript is never touched.

Two edits:
  1. Replace the bytes of word/media/image5.png (the Figure 5 image) and resize the drawing to
     fill a landscape page.
  2. Wrap the caption + image in their own landscape section, leaving the rest portrait.
"""
import shutil
import sys
import zipfile
from copy import deepcopy

from docx import Document
from docx.oxml.ns import qn

DOCX = r"C:\Users\ryand\Downloads\Group7_Final Evaluation (updated DB tables).docx"
NEW_IMAGE = "erd_studybuddy.png"
IMAGE_PART = "word/media/image5.png"

CAPTION = "Entity-Relationship Diagram (ERD) of StudyBuddy"

EMU_PER_IN = 914400
TWIPS_PER_IN = 1440
# Measured from a Word PDF export of this document: on the landscape page the body band runs
# y=0.91in to y=7.59in (header and footer take the rest), and the two-line caption above the
# figure occupies 0.92in to 1.44in. That leaves 6.15in for the image; anything taller makes Word
# push the figure onto a page of its own and strand the caption. 6.0in was still too tall once
# the paragraph mark is counted; 5.6in clears it with room to spare (1.44 + 5.6 = 7.04 vs 7.59).
# Aspect ratio is preserved (9.5 : 6.5), so the 300 DPI source renders at ~340 DPI here.
FIG_H_IN = 5.6
FIG_W_IN = round(FIG_H_IN * (9.5 / 6.5), 3)
# 0.5in on a full-page figure: the caption sits above the image, and at 0.75in margins the
# caption (~0.4in) plus a 6.5in image exceeds the 7.0in usable height, pushing the image onto
# its own page. At 0.5in the usable height is 7.5in and the two stay together.
LAND_MARGIN_IN = 0.5


def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def main():
    doc = Document(DOCX)
    body = doc.element.body
    kids = list(body.iterchildren())

    # --- locate the caption and the image paragraph that follows it --------------------
    cap_i = None
    for i, el in enumerate(kids):
        if el.tag == qn("w:p") and CAPTION in ptext(el) and el.findall(qn("w:r")):
            # the caption, not the LIST OF FIGURES entry (that one sits inside a TOC field)
            if "PAGEREF" not in "".join(
                t.text or "" for t in el.iter(qn("w:instrText"))
            ):
                cap_i = i
    if cap_i is None:
        sys.exit("could not find the Figure 5 caption")

    img_i = None
    for j in range(cap_i + 1, min(cap_i + 4, len(kids))):
        if kids[j].tag == qn("w:p") and kids[j].find(".//" + qn("w:drawing")) is not None:
            img_i = j
            break
    if img_i is None:
        sys.exit("could not find the Figure 5 image paragraph after the caption")

    print("caption at body index %d, image at %d" % (cap_i, img_i))

    # --- resize the drawing to fill the landscape page ---------------------------------
    cx, cy = int(FIG_W_IN * EMU_PER_IN), int(FIG_H_IN * EMU_PER_IN)
    n = 0
    for tag in ("wp:extent", "a:ext"):
        prefix, local = tag.split(":")
        for e in kids[img_i].iter():
            if e.tag.endswith("}" + local):
                if e.get("cx") is not None:
                    e.set("cx", str(cx))
                    e.set("cy", str(cy))
                    n += 1
    print("resized %d extent elements to %.2f x %.2f in" % (n, FIG_W_IN, FIG_H_IN))

    # The figure paragraph inherits the manuscript's double spacing (w:line="480" auto). For an
    # inline drawing Word multiplies the whole line box by that factor, so a 6in image demands
    # 12in of vertical space and can never share a page with its caption. Single-space this one
    # paragraph so the line box equals the image height. Body text is untouched.
    img_pPr = kids[img_i].find(qn("w:pPr"))
    if img_pPr is None:
        img_pPr = kids[img_i].makeelement(qn("w:pPr"), {})
        kids[img_i].insert(0, img_pPr)
    spacing = img_pPr.find(qn("w:spacing"))
    if spacing is None:
        spacing = img_pPr.makeelement(qn("w:spacing"), {})
        img_pPr.append(spacing)
    before = spacing.get(qn("w:line"))
    spacing.set(qn("w:line"), "240")
    spacing.set(qn("w:lineRule"), "auto")
    spacing.set(qn("w:after"), "0")
    print("figure paragraph line spacing: %s -> 240 (single)" % before)

    # --- build the two section-break paragraphs ----------------------------------------
    body_sect = body.find(qn("w:sectPr"))
    if body_sect is None:
        sys.exit("document has no body-level sectPr")

    def sect_para(landscape):
        p = body.makeelement(qn("w:p"), {})
        pPr = body.makeelement(qn("w:pPr"), {})
        sect = deepcopy(body_sect)
        if landscape:
            pgSz = sect.find(qn("w:pgSz"))
            w = pgSz.get(qn("w:w"))
            h = pgSz.get(qn("w:h"))
            pgSz.set(qn("w:w"), h)
            pgSz.set(qn("w:h"), w)
            pgSz.set(qn("w:orient"), "landscape")
            mar = sect.find(qn("w:pgMar"))
            m = str(int(LAND_MARGIN_IN * TWIPS_PER_IN))
            for side in ("top", "bottom", "left", "right"):
                mar.set(qn("w:" + side), m)
        pPr.append(sect)
        p.append(pPr)
        return p

    # A paragraph's sectPr describes the section ENDING at that paragraph. So a portrait
    # marker before the caption closes the preceding portrait section, and a landscape marker
    # after the image closes the landscape section holding the figure.
    kids[cap_i].addprevious(sect_para(landscape=False))
    kids[img_i].addnext(sect_para(landscape=True))
    print("inserted portrait section break before the caption and landscape after the image")

    doc.save(DOCX)

    # --- swap the image bytes ----------------------------------------------------------
    with open(NEW_IMAGE, "rb") as f:
        blob = f.read()

    tmp = DOCX + ".tmp"
    with zipfile.ZipFile(DOCX) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        if IMAGE_PART not in zin.namelist():
            sys.exit("%s not present in the package" % IMAGE_PART)
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == IMAGE_PART:
                print("replacing %s: %d -> %d bytes" % (IMAGE_PART, len(data), len(blob)))
                data = blob
            zout.writestr(item, data)
    shutil.move(tmp, DOCX)
    print("done: %s" % DOCX)


if __name__ == "__main__":
    main()
