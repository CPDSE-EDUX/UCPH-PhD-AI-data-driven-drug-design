#!/usr/bin/env python3
"""Build editable Word and Excel group worksheets. Requires openpyxl for Excel."""

from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.properties import CalcProperties


OUT = Path(__file__).resolve().parent / "downloads"
APP = "https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/"
GUIDE = "https://github.com/cpdse-edux/UCPH-PhD-AI-data-driven-drug-design/blob/main/day02/workshop_manual/Home.md"
PARENTS = ["LSD_control", "H1", "H2", "H3", "AI1", "AI2", "AI3"]
SETTINGS = [
    ("Group ID and participants", ""),
    ("Working folder / project", ""),
    ("Maestro release / job host", ""),
    ("PDB versions / download date", "9WPQ (2A); 7SRS (2B)"),
    ("Receptor / ligand chain IDs", ""),
    ("Removed components / retained modifications", ""),
    ("Alignment selection / coverage / RMSD", ""),
    ("Protein pH / force field / refinement / water / capping choices", ""),
    ("LigPrep pH / Epik version / stereochemistry / state settings", ""),
    ("Input parents / successful parents / generated states", ""),
    ("Grid files / centers / box sizes / receptor vdW settings", ""),
    ("Glide mode / ligand vdW / state penalties / pose limit / minimization", ""),
    ("LSD redocking assessment: 2A and 2B", ""),
    ("Score property / parent summarization rule", "DockingScore; lowest score per parent per receptor"),
]
QUESTIONS = [
    "Which original hypothesis was supported, contradicted or unresolved? Cite pose and score evidence.",
    "Did the selected state differ between receptors, and how does that affect the interpretation?",
    "What did AI contribute, and what required correction?",
    "Which candidate would you test next? Name the binding and functional assays and the main uncertainty.",
]
NAVY = "17365D"
BLUE = "EAF2F8"
GREEN = "E8F3E8"
GRAY = "5B6573"


def excel():
    wb = Workbook()
    wb.remove(wb.active)
    wb.calculation = CalcProperties(calcId=191029, fullCalcOnLoad=True, forceFullCalc=True)
    thin = Side(style="thin", color="CFD8E3")

    def sheet(name, title, instruction, headers=None, rows=None, widths=None):
        ws = wb.create_sheet(name)
        n = max(len(headers or []), len(widths or []), 2)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
        ws.cell(1, 1, title).font = Font(name="Calibri", size=18, bold=True, color=NAVY)
        ws.row_dimensions[1].height = 32
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n)
        ws.cell(2, 1, instruction).font = Font(name="Calibri", size=11, color=GRAY)
        ws.cell(2, 1).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[2].height = 46
        if headers:
            for col, header in enumerate(headers, 1):
                c = ws.cell(4, col, header)
                c.fill = PatternFill("solid", fgColor=NAVY)
                c.font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
                c.alignment = Alignment(wrap_text=True, vertical="center")
            ws.row_dimensions[4].height = 34
        for row, values in enumerate(rows or [], 5):
            ws.row_dimensions[row].height = 58
            for col in range(1, n + 1):
                c = ws.cell(row, col, values[col - 1] if col <= len(values) else "")
                c.font = Font(name="Calibri", size=11, color="17202A")
                c.alignment = Alignment(wrap_text=True, vertical="top")
                c.fill = PatternFill("solid", fgColor=BLUE)
                c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        for col, width in enumerate(widths or [40, 70], 1):
            ws.column_dimensions[chr(64 + col)].width = width
        ws.freeze_panes = "C5" if n > 3 else "A5"
        ws.sheet_view.showGridLines = False
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.orientation = "landscape" if n > 3 else "portrait"
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.print_title_rows = "1:4"
        ws.print_options.horizontalCentered = True
        ws.oddFooter.center.text = "Day 2 · Group worksheet · Page &P"
        ws.print_area = f"A1:{chr(64+n)}{max(ws.max_row, 4)}"
        return ws

    ws = sheet("Start here", "Human vs AI · Group worksheet", "Use either this workbook or the Word worksheet. Work in groups of 2–3.",
               ["Task", "Instructions"], [
                   ("1 · Save a group copy", "Save as G##_worksheet.xlsx. Blue cells are editable; green cells contain score formulas."),
                   ("2 · Submit molecules in the web app", "Submit three Human and three AI SMILES with hypotheses. This workbook records the returned compound IDs and your analysis."),
                   ("3 · Open the submission app", APP),
                   ("4 · Follow the manual", GUIDE),
                   ("5 · Lock predictions", "Complete Human designs before asking AI; save AI prompts/responses and nominate winners before seeing scores."),
                   ("6 · Enter docking results", "Use the same score property at both receptors. Enter one selected result per parent and retain state/pose IDs. Leave missing scores blank or enter NA."),
                   ("7 · Interpret carefully", "ΔS = score(2B) − score(2A); positive values favor 2A in this model. Scores are not measured Ki or validated fold selectivity. See step 17."),
               ], [35, 100])
    ws["B7"].hyperlink = APP
    ws["B8"].hyperlink = GUIDE
    for cell in (ws["B7"], ws["B8"]):
        cell.font = Font(name="Calibri", size=11, color="0563C1", underline="single")

    sheet("Setup", "Group and calculation settings", "Record the common settings actually used. Keep full job logs and the per-state score export alongside the worksheet.",
          ["Item", "Record"], SETTINGS, [55, 95])
    sheet("Observations", "Structure observations and hypotheses", "Compare aligned 9WPQ (2A) and 7SRS (2B); distinguish experimental observations from design predictions.",
          ["Receptor / region", "Observation / residue labels", "Uncertainty / design consequence"],
          [("", "", "") for _ in range(3)] + [
              ("Affinity hypothesis", "Changing ___ could improve 2A binding because ___", "Main failure mode:"),
              ("Selectivity hypothesis", "The same change could be less favorable in 2B because ___", "Expected supportive pose:"),
          ], [30, 65, 65])
    ws = sheet("Human designs", "Human designs · complete before asking AI", "Each person proposes one design; a pair develops its third together. Preserve the predictions after scores are revealed.",
               ["Local ID", "Designer", "Modification / structural rationale", "Expected 2A affinity", "Expected 2A-over-2B selectivity", "Main failure mode"],
               [(p, "", "", "", "", "") for p in PARENTS[1:4]], [14, 22, 65, 26, 30, 50])
    ws.row_dimensions[9].height = 55
    ws["A9"] = "Predicted human winner / reason"
    ws.merge_cells("A9:B9")
    ws.merge_cells("C9:F9")
    ws["C9"].fill = PatternFill("solid", fgColor=BLUE)
    ws.print_area = "A1:F9"

    ws = sheet("AI designs", "AI designs and critical review", "Keep the exact prompt, first response and correction attempts in the cells below or in named files saved alongside this workbook.",
               ["Local ID", "Model", "Proposed change / rationale", "Chemistry checks / corrections", "Expected affinity / selectivity", "Human intervention"],
               [(p, "", "", "", "", "") for p in PARENTS[4:]], [14, 22, 65, 55, 40, 45])
    for row, label in enumerate(["Model version / date", "Exact prompt / saved file", "First response / saved file", "Correction attempts / saved file", "Predicted AI winner / reason"], 9):
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        ws.cell(row, 1, label).alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=6)
        ws.cell(row, 3).fill = PatternFill("solid", fgColor=BLUE)
        ws.cell(row, 3).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row].height = 66
    ws.print_area = "A1:F13"

    ws = sheet("Submission IDs", "Submit six SMILES through the web app", "Use the app for SMILES, structure preview and submission. Record each returned ID here; confirm the entry persists after reloading the Dashboard.",
               ["Local ID", "Generated compound ID", "Origin", "Designer / chatbot", "Persisted?", "Notes"],
               [(p, "", "Human" if p.startswith("H") else "AI", "", "", "") for p in PARENTS[1:]],
               [14, 30, 16, 25, 18, 60])
    ws["A12"] = "Submission app"
    ws.merge_cells("B12:F12")
    ws["B12"] = APP
    ws["B12"].hyperlink = APP
    ws["B12"].font = Font(color="0563C1", underline="single")
    for row, label in [(14, "Predicted overall winner / reason"), (16, "Submission freeze / instructor acknowledgment")]:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        ws.cell(row, 1, label).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=6)
        ws.cell(row, 3).fill = PatternFill("solid", fgColor=BLUE)
        ws.row_dimensions[row].height = 54
    validation = DataValidation(type="list", formula1='"Yes,No,Check"', allow_blank=True)
    ws.add_data_validation(validation)
    validation.add("E5:E10")
    ws.print_area = "A1:F16"

    ws = sheet("Docking results", "Paired receptor docking results", "Enter numeric DockingScores or leave blank / NA. For each parent, use the lowest score per receptor and record state/pose IDs. Green cells calculate only from paired numeric inputs; positive ΔS favors 2A.",
               ["Local ID", "Compound ID", "Origin", "2A score", "2A state / pose", "2B score", "2B state / pose", "ΔS = 2B − 2A", "2A improvement vs LSD", "ΔS improvement vs LSD", "Pose assessment / failure reason"],
               [(p, "LSD_control" if p == "LSD_control" else "", "Control" if p == "LSD_control" else "Human" if p.startswith("H") else "AI", "", "", "", "", "", "", "", "") for p in PARENTS],
               [16, 28, 14, 16, 30, 16, 30, 20, 23, 23, 65])
    ws.freeze_panes = "D5"
    for row in range(5, 12):
        if row > 5:
            submission_row = row - 1
            ws.cell(row, 2, f'=IF(\'Submission IDs\'!B{submission_row}="","",\'Submission IDs\'!B{submission_row})')
        ws.cell(row, 8, f'=IF(COUNT(D{row},F{row})=2,F{row}-D{row},"")')
        ws.cell(row, 9, f'=IF(COUNT($D$5,D{row})=2,$D$5-D{row},"")')
        ws.cell(row, 10, f'=IF(COUNT($H$5,H{row})=2,H{row}-$H$5,"")')
        for col in [4, 6, 8, 9, 10]:
            ws.cell(row, col).number_format = "0.00;-0.00;0.00"
        for col in [8, 9, 10] + ([2] if row > 5 else []):
            ws.cell(row, col).fill = PatternFill("solid", fgColor=GREEN)
    ws.auto_filter.ref = "A4:K11"
    ws.conditional_formatting.add("H6:H11", ColorScaleRule(start_type="min", start_color="FADBD8", end_type="max", end_color="D5F5E3"))
    ws.merge_cells("A14:K14")
    ws["A14"] = "Keep full per-state exports. Different winning states can occur at 2A and 2B. Missing docking at 2B does not establish selectivity. Hypothetical Ki* arithmetic belongs in a separately labelled analysis (manual step 17)."
    ws["A14"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[14].height = 36
    ws.print_area = "A1:K14"

    ws = sheet("Debrief", "Interpretation and next experiment", "Relate your original predictions to poses and scores; distinguish docking rankings from measured affinity and functional activity.",
               ["Question", "Group response"], [(q, "") for q in QUESTIONS], [65, 100])
    for row in range(5, 9):
        ws.row_dimensions[row].height = 100
    wb.save(OUT / "Group-worksheet.xlsx")


def word():
    """Write a standard OOXML document with seven intentional A4 pages."""
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ET.register_namespace("w", w)
    ET.register_namespace("r", r)

    def node(tag, parent=None, text=None, **attrs):
        e = ET.Element(f"{{{w}}}{tag}", {f"{{{w}}}{k}": str(v) for k, v in attrs.items()})
        if text is not None:
            e.text = text
        if parent is not None:
            parent.append(e)
        return e

    document = node("document")
    body = node("body", document)

    def paragraph(text="", style=None, parent=body, after=100):
        p = node("p", parent)
        props = node("pPr", p)
        if style:
            node("pStyle", props, val=style)
        node("spacing", props, after=after)
        run = node("r", p)
        node("t", run, text=text)
        return p

    def table(headers, rows, widths, height=480):
        tbl = node("tbl", body)
        props = node("tblPr", tbl)
        node("tblW", props, w=sum(widths), type="dxa")
        node("tblLayout", props, type="fixed")
        borders = node("tblBorders", props)
        for name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            node(name, borders, val="single", sz=4, color="CFD8E3")
        grid = node("tblGrid", tbl)
        for width in widths:
            node("gridCol", grid, w=width)
        for index, values in enumerate([headers] + list(rows)):
            tr = node("tr", tbl)
            trpr = node("trPr", tr)
            node("cantSplit", trpr)
            node("trHeight", trpr, val=380 if index == 0 else height, hRule="atLeast")
            if index == 0:
                node("tblHeader", trpr)
            for col, width in enumerate(widths):
                tc = node("tc", tr)
                tcpr = node("tcPr", tc)
                node("tcW", tcpr, w=width, type="dxa")
                node("shd", tcpr, fill=NAVY if index == 0 else "FFFFFF")
                node("vAlign", tcpr, val="top")
                p = paragraph(str(values[col]) if col < len(values) else "", parent=tc, after=70)
                run = p.find(f"{{{w}}}r")
                rp = node("rPr")
                run.insert(0, rp)
                node("sz", rp, val=19)
                if index == 0:
                    node("b", rp)
                    node("color", rp, val="FFFFFF")
        paragraph(after=40)

    def heading(text, new_page=False):
        if new_page:
            p = node("p", body)
            node("br", node("r", p), type="page")
        paragraph(text, "Heading1")

    def field(label, height=550):
        table([label], [[""]], [9638], height)

    heading("Human vs AI · Group worksheet")
    paragraph("Day 2 · 10 November 2026 · Groups of 2–3")
    paragraph("Save a group copy of this document, or use the Excel workbook. Submit three Human and three AI SMILES through the web app; use this worksheet for notes, predictions and analysis.")
    p = paragraph("Submission app: ")
    link = node("hyperlink", p)
    link.set(f"{{{r}}}id", "rIdApp")
    run = node("r", link)
    props = node("rPr", run)
    node("color", props, val="0563C1")
    node("u", props, val="single")
    node("t", run, text="Open the workshop SMILES submission app")
    paragraph("1 · Group and calculation settings", "Heading2")
    table(["Item", "Record"], SETTINGS, [3900, 5738], height=430)

    heading("2 · Structural observations and hypotheses", True)
    paragraph("Compare aligned 9WPQ (5-HT2A) and 7SRS (5-HT2B). Record residue labels and distinguish observations from predictions.")
    table(["Receptor / region", "Observation / residue labels", "Uncertainty / design consequence"], [["", "", ""] for _ in range(3)], [1900, 3869, 3869], height=1300)
    field("Affinity hypothesis: changing ___ could improve 2A binding because ___", 950)
    field("Selectivity hypothesis: the same change could be less favorable in 2B because ___", 950)
    field("Expected supportive docking pose and main failure mode", 950)

    heading("3 · Human designs", True)
    paragraph("Complete before asking AI. Each person proposes one candidate; a pair develops its third together. Save the original predictions before scores are revealed.")
    for local in PARENTS[1:4]:
        paragraph(local, "Heading2")
        table(["Design record", "Your prediction"], [
            ("Designer / modification relative to LSD", ""),
            ("Structural rationale / expected new contact", ""),
            ("Expected 2A affinity / 2A-over-2B selectivity directions", ""),
            ("Main failure mode", ""),
        ], [3900, 5738], height=480)
    field("Predicted human winner and reason", 600)

    heading("4 · AI designs and critical review", True)
    paragraph("Save the exact prompt, first response and correction attempts alongside this document. Record the model/version, date and saved filenames here.")
    table(["AI conversation", "Record"], [("Model / version / date", ""), ("Prompt / response / correction filenames", "")], [3900, 5738], height=550)
    for local in PARENTS[4:]:
        paragraph(local, "Heading2")
        table(["Design record", "Your assessment"], [
            ("Proposed change / structural rationale", ""),
            ("Chemistry checks / correction attempts", ""),
            ("Expected affinity / selectivity directions", ""),
            ("Human intervention", ""),
        ], [3900, 5738], height=440)
    field("Predicted AI winner and reason", 550)

    heading("5 · Submission IDs and locked predictions", True)
    paragraph("Submit SMILES and hypotheses through the workshop web app. Record its generated compound IDs below, then confirm that all six entries persist after reloading the Dashboard. Keep the submitted structures in the app and exported .smi file.")
    table(["Local ID", "Generated compound ID", "Designer / chatbot", "Persisted?"], [(p, "", "", "") for p in PARENTS[1:]], [1200, 3438, 3400, 1600], height=700)
    field("Predicted overall winner and reason · complete before results", 1000)
    field("Submission freeze time / instructor acknowledgment", 600)
    paragraph("If the app is unavailable, provide the instructor with a separate .smi file plus the submission metadata before the result reveal. Record the agreed fallback here.")
    field("Fallback submission record, if needed", 700)

    heading("6 · Paired docking results", True)
    paragraph("Use generated compound IDs. Take the lowest DockingScore per parent separately at each receptor; retain selected state/pose IDs in the detailed export. Enter missing scores as NA.")
    table(["Compound ID", "2A score", "2B score", "ΔS", "Pose assessment / failure reason"], [("LSD_control", "", "", "", "")] + [["", "", "", "", ""] for _ in range(6)], [2400, 1200, 1200, 1200, 3638], height=700)
    paragraph("ΔS = score(2B) − score(2A). Positive ΔS favors 2A in this model. 2A score improvement = score2A(LSD) − score2A(candidate); selectivity score improvement = ΔS(candidate) − ΔS(LSD). The Excel version calculates these differences automatically.")
    field("Selected state / pose IDs, or filename of the detailed score export", 750)
    field("Comparison with LSD and any different winning states at the two receptors", 900)
    paragraph("Docking scores are empirical rankings, not measured Ki. Use manual step 17 for the optional, separately labelled hypothetical Ki* exercise. Failed docking at 2B does not demonstrate selectivity.")

    heading("7 · Interpretation and next experiment", True)
    for question in QUESTIONS:
        field(question, 1550)
    paragraph("Save this worksheet with the submitted-ID list, exported SMILES, Maestro project, job settings, pose files and complete score table.")

    section = node("sectPr", body)
    footer_ref = node("footerReference", section, type="default")
    footer_ref.set(f"{{{r}}}id", "rIdFooter")
    node("pgSz", section, w=11906, h=16838)
    node("pgMar", section, top=1000, right=1134, bottom=1000, left=1134, header=400, footer=400, gutter=0)
    styles = node("styles")
    defaults = node("docDefaults", styles)
    rp = node("rPr", node("rPrDefault", defaults))
    node("rFonts", rp, ascii="Calibri", hAnsi="Calibri")
    node("sz", rp, val=21)
    pp = node("pPr", node("pPrDefault", defaults))
    node("spacing", pp, after=100, line=240, lineRule="auto")
    for name, size in [("Heading1", 32), ("Heading2", 24)]:
        st = node("style", styles, type="paragraph", styleId=name)
        node("name", st, val=name)
        stp = node("pPr", st)
        node("keepNext", stp)
        node("spacing", stp, before=140, after=100)
        sr = node("rPr", st)
        node("b", sr)
        node("color", sr, val=NAVY)
        node("sz", sr, val=size)
    footer = node("ftr")
    p = paragraph("Day 2 · Human vs AI · Group worksheet · ", parent=footer)
    node("jc", p.find(f"{{{w}}}pPr"), val="center")
    node("fldSimple", p, instr="PAGE")

    def xml(element):
        return ET.tostring(element, encoding="utf-8", xml_declaration=True)

    relns = "http://schemas.openxmlformats.org/package/2006/relationships"

    def rels(items):
        root = ET.Element("Relationships", xmlns=relns)
        for attrs in items:
            ET.SubElement(root, "Relationship", attrs)
        return xml(root)

    base = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
    types = ET.Element("Types", xmlns="http://schemas.openxmlformats.org/package/2006/content-types")
    for ext, content in [("rels", "application/vnd.openxmlformats-package.relationships+xml"), ("xml", "application/xml")]:
        ET.SubElement(types, "Default", Extension=ext, ContentType=content)
    for part, subtype in [("document", "document.main"), ("styles", "styles"), ("footer1", "footer")]:
        ET.SubElement(types, "Override", PartName=f"/word/{part}.xml", ContentType=f"application/vnd.openxmlformats-officedocument.wordprocessingml.{subtype}+xml")
    with ZipFile(OUT / "Group-worksheet.docx", "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", xml(types))
        z.writestr("_rels/.rels", rels([{"Id": "rId1", "Type": base + "officeDocument", "Target": "word/document.xml"}]))
        z.writestr("word/document.xml", xml(document))
        z.writestr("word/styles.xml", xml(styles))
        z.writestr("word/footer1.xml", xml(footer))
        z.writestr("word/_rels/document.xml.rels", rels([
            {"Id": "rIdStyles", "Type": base + "styles", "Target": "styles.xml"},
            {"Id": "rIdFooter", "Type": base + "footer", "Target": "footer1.xml"},
            {"Id": "rIdApp", "Type": base + "hyperlink", "Target": APP, "TargetMode": "External"},
        ]))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    word()
    excel()
    print(f"Created Word and Excel worksheets in {OUT}")
