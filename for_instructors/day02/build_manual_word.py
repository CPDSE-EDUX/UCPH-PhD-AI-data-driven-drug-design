#!/usr/bin/env python3
"""Build the complete review copy. Requires python-docx, mistune<3 and Pillow."""

from copy import deepcopy
from pathlib import Path
import re
from urllib.parse import urlparse

import mistune
from PIL import Image
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DAY = REPO / "day02"
OUT = HERE / "Day02-Workshop-Manual-Complete.docx"
GITHUB = "https://github.com/cpdse-edux/UCPH-PhD-AI-data-driven-drug-design/blob/main/"
MANUAL = DAY / "workshop_content"
PARSER = mistune.create_markdown(renderer="ast", plugins=["table"])
NAVY = "17365D"
# A line of only cross-reference links is website navigation, replaced here by
# document bookmarks.
NAV_LINE = re.compile(r"^(?:\[[^\]]+\]\([^)]+\)|·|\s)+$")


def element(tag, **attrs):
    e = OxmlElement("w:" + tag)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def plain(nodes):
    return "".join(n.get("text", plain(n.get("children", []))) for n in nodes)


def clean_markdown(path):
    return "\n".join(line for line in path.read_text().splitlines() if not NAV_LINE.match(line))


def build():
    steps = sorted(MANUAL.glob("[0-9][0-9]-*.md"))
    assert len(steps) == 18
    sources = [
        (MANUAL / "index.md", "Workshop overview"),
        *[(p, None) for p in steps],
        (MANUAL / "worksheets.md", "Worksheet instructions"),
        (MANUAL / "references.md", None),
        (MANUAL / "submit.md", "Appendix B · Submission app guide"),
        (HERE / "Instructor-notes.md", "Appendix C · Instructor notes"),
        (HERE / "Dashboard-setup.md", "Appendix D · Dashboard setup"),
        (REPO / "for_instructors/PUBLISHING.md", "Appendix E · Website publishing"),
    ]
    titles = {p: title or plain(PARSER(p.read_text())[0]["children"]) for p, title in sources}
    anchors = {p: f"section_{i}" for i, (p, _) in enumerate(sources)}
    anchors[MANUAL / "downloads/Group-worksheet.docx"] = "worksheet_full"
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin = section.bottom_margin = Mm(18)
    section.left_margin = section.right_margin = Mm(20)
    section.header_distance = section.footer_distance = Mm(8)
    usable_width = 170
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Calibri", Pt(11)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.08
    for name, size in [("Title", 30), ("Heading 1", 21), ("Heading 2", 14), ("Heading 3", 12)]:
        s = doc.styles[name]
        s.font.name, s.font.size = "Calibri", Pt(size)
        s.font.color.rgb = RGBColor.from_string(NAVY)
        s.paragraph_format.keep_with_next = True
    for name in ["Code block", "Inline code"]:
        s = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH if name == "Code block" else WD_STYLE_TYPE.CHARACTER)
        s.font.name, s.font.size = "Consolas", Pt(9)
    doc.styles["Code block"].paragraph_format.space_after = Pt(8)
    doc.styles["Code block"].paragraph_format.line_spacing = 1
    doc.styles["Caption"].font.size = Pt(9)
    doc.styles["Caption"].font.color.rgb = RGBColor.from_string("5B6573")
    header = section.header.paragraphs[0]
    header.text = "UCPH PhD course · Day 2 · Structure-based drug design"
    header.style = doc.styles["Caption"]
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run("Human vs AI · ").font.size = Pt(9)
    for name in ["PAGE", "NUMPAGES"]:
        if name == "NUMPAGES":
            footer.add_run(" / ")
        field = element("fldSimple", instr=name)
        footer._p.append(field)
    doc.core_properties.title = "Human vs AI: ligand design and docking evaluation"
    doc.core_properties.subject = "Day 2 workshop manual and instructor resources"
    doc.core_properties.author = "UCPH PhD course"
    doc.core_properties.keywords = "Maestro, 5-HT2A, 5-HT2B, Human vs AI, workshop"
    bookmark_counter = 0
    figures = []
    rendered_text = []

    def bookmark(p, name):
        nonlocal bookmark_counter
        bookmark_counter += 1
        p._p.insert(0, element("bookmarkStart", id=bookmark_counter, name=name))
        p._p.append(element("bookmarkEnd", id=bookmark_counter))

    def add_link(p, label, url=None, anchor=None):
        link = element("hyperlink")
        if anchor:
            link.set(qn("w:anchor"), anchor)
        else:
            rel = doc.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
            link.set(qn("r:id"), rel)
        run = element("r")
        props = element("rPr")
        props.append(element("color", val="0563C1"))
        props.append(element("u", val="single"))
        run.append(props)
        t = element("t")
        t.text = label
        run.append(t)
        link.append(run)
        p._p.append(link)

    def inline(p, nodes, source, bold=False, italic=False):
        for n in nodes:
            kind = n["type"]
            if kind in ["text", "codespan"]:
                r = p.add_run(n["text"])
                if kind == "codespan":
                    r.style = "Inline code"
                r.bold, r.italic = bold, italic
            elif kind in ["strong", "emphasis"]:
                inline(p, n["children"], source, bold or kind == "strong", italic or kind == "emphasis")
            elif kind == "link":
                url = n["link"]
                local = (source.parent / url.split("#")[0]).resolve()
                if not urlparse(url).scheme and local in anchors:
                    add_link(p, plain(n["children"]), anchor=anchors[local])
                else:
                    if not urlparse(url).scheme:
                        url = GITHUB + local.relative_to(REPO).as_posix()
                    add_link(p, plain(n["children"]), url=url)
            elif kind in ["softbreak", "linebreak"]:
                p.add_run("\n" if kind == "linebreak" else " ")
            elif kind == "inline_html":
                if n["text"].lower() in ["<br>", "<br/>", "<br />"]:
                    p.add_run("\n")
                else:
                    raise ValueError(n)
            else:
                raise ValueError(f"Unhandled inline: {n}")

    def render(nodes, source, parent=doc):
        for n in nodes:
            kind = n["type"]
            if kind == "heading":
                p = parent.add_paragraph(style=f"Heading {min(n['level'], 3)}")
                inline(p, n["children"], source)
            elif kind in ["paragraph", "block_text"]:
                images = [x for x in n["children"] if x["type"] == "image"]
                if images:
                    assert len(images) == len(n["children"])
                    for im in images:
                        path = source.parent / im["src"]
                        w, h = Image.open(path).size
                        width = min(usable_width, 145 * w / h)
                        p = parent.add_paragraph()
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p.paragraph_format.keep_with_next = True
                        p.add_run().add_picture(str(path), width=Mm(width))
                        caption = plain(im.get("children", [])) or im.get("alt", "")
                        if not caption:
                            caption = im.get("title", path.stem)
                        cp = parent.add_paragraph(f"Figure {len(figures)+1}. {caption}", "Caption")
                        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        figures.append(path)
                else:
                    p = parent.add_paragraph()
                    inline(p, n["children"], source)
            elif kind == "list":
                for i, item in enumerate(n["children"], n.get("start", 1)):
                    for j, child in enumerate(item["children"]):
                        if child["type"] in ["block_text", "paragraph"]:
                            p = parent.add_paragraph()
                            p.paragraph_format.left_indent = Mm(5)
                            p.paragraph_format.first_line_indent = Mm(-5)
                            p.add_run((f"{i}. " if n["ordered"] else "• ") if j == 0 else "")
                            inline(p, child["children"], source)
                        else:
                            render([child], source, parent)
            elif kind == "table":
                head, body = n["children"]
                rows = [head["children"]] + [r["children"] for r in body["children"]]
                cols = len(rows[0])
                table = parent.add_table(rows=0, cols=cols)
                table.style = "Table Grid"
                table.autofit = False
                weights = [max(9, min(40, max(len(plain(row[c].get('children', []))) for row in rows) ** 0.7 * 2)) for c in range(cols)]
                for c, weight in zip(table.columns, weights):
                    c.width = Mm(usable_width * weight / sum(weights))
                for ri, cells in enumerate(rows):
                    row = table.add_row()
                    row._tr.get_or_add_trPr().append(element("cantSplit"))
                    if ri == 0:
                        row._tr.get_or_add_trPr().append(element("tblHeader"))
                    for ci, cell_node in enumerate(cells):
                        cell = row.cells[ci]
                        cell.width = Mm(usable_width * weights[ci] / sum(weights))
                        p = cell.paragraphs[0]
                        p.paragraph_format.space_after = Pt(4)
                        p.paragraph_format.space_before = Pt(3)
                        inline(p, cell_node.get("children", []), source, bold=ri == 0)
                        for r in p.runs:
                            r.font.size = Pt(9 if cols > 4 else 10)
                        if ri == 0:
                            cell._tc.get_or_add_tcPr().append(element("shd", fill="EAF2F8"))
                parent.add_paragraph().paragraph_format.space_after = Pt(0)
            elif kind == "block_code":
                p = parent.add_paragraph(style="Code block")
                p.add_run(n["text"].rstrip("\n"))
                p.paragraph_format.keep_together = True
                p._p.get_or_add_pPr().append(element("shd", fill="F3F5F7"))
            elif kind in ["newline", "thematic_break"]:
                pass
            else:
                raise ValueError(f"Unhandled block: {n}")
            if kind not in ["newline", "thematic_break"]:
                rendered_text.append(plain([n]))

    doc.add_paragraph("Human vs AI", "Title")
    doc.add_paragraph("Ligand design and docking evaluation", "Subtitle")
    doc.add_paragraph("5-HT2A over 5-HT2B", "Heading 2")
    doc.add_paragraph("Day 2 · 10 November 2026 · 13:00–17:00 · Groups of 2–3")
    doc.add_paragraph("UCPH PhD course · AI and data-driven drug design")
    doc.add_paragraph("Complete workshop manual", "Heading 2")
    doc.add_paragraph("Workshop schedule, all 18 steps, Maestro screenshots, references, editable group worksheet and instructor resources.")
    doc.add_page_break()
    doc.add_heading("Contents", 1)
    add_link(doc.add_paragraph(), "Day program", anchor="day_program")
    for p, _ in sources[:21]:
        add_link(doc.add_paragraph(), titles[p], anchor=anchors[p])
    add_link(doc.add_paragraph(), "Appendix A · Full editable group worksheet", anchor="worksheet_full")
    for p, _ in sources[21:]:
        add_link(doc.add_paragraph(), titles[p], anchor=anchors[p])
    doc.add_page_break()
    p = doc.add_heading("Day program", 1)
    bookmark(p, "day_program")
    day = (DAY / "README.md").read_text().split("## Workshop: Human vs AI")[0]
    day = "\n".join(x for x in day.splitlines() if not x.startswith("# Day 2") and not NAV_LINE.match(x))
    render(PARSER(day), DAY / "README.md")

    def append_worksheet():
        doc.add_page_break()
        p = doc.add_heading("Appendix A · Full editable group worksheet", 1)
        bookmark(p, "worksheet_full")
        worksheet = Document(MANUAL / "downloads/Group-worksheet.docx")
        for child in worksheet.element.body:
            if child.tag == qn("w:sectPr"):
                continue
            child = deepcopy(child)
            for style in child.iter(qn("w:pStyle")):
                value = style.get(qn("w:val"))
                if value in ["Heading1", "Heading2"]:
                    style.set(qn("w:val"), "Heading2" if value == "Heading1" else "Heading3")
            for link in child.iter(qn("w:hyperlink")):
                old_id = link.get(qn("r:id"))
                if old_id:
                    rel = worksheet.part.rels[old_id]
                    new_id = doc.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
                    link.set(qn("r:id"), new_id)
            doc.element.body.insert(-1, child)

    for i, (source, _) in enumerate(sources):
        if i == 21:
            append_worksheet()
        doc.add_page_break()
        nodes = PARSER(clean_markdown(source))
        assert nodes[0]["type"] == "heading"
        p = doc.add_heading(titles[source], 1)
        bookmark(p, anchors[source])
        render(nodes[1:], source)
    assert len(figures) == 16
    OUT.parent.mkdir(exist_ok=True)
    doc.save(OUT)
    print(f"Created {OUT} ({OUT.stat().st_size:,} bytes)")
    print(f"Included {len(steps)} steps, {len(figures)} images, all manual pages, full worksheet and 4 supporting guides.")


if __name__ == "__main__":
    build()
