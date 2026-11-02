# Group worksheet

Download either format and save one copy for your group:

- [Word worksheet (.docx)](downloads/Group-worksheet.docx) — editable pages with space for observations, design rationales, predictions and discussion.
- [Excel worksheet (.xlsx)](downloads/Group-worksheet.xlsx) — separate tabs for settings, observations, Human designs, AI designs, submission IDs, docking results and debrief. It calculates paired score differences and improvements relative to LSD.

Use a filename such as `G04_worksheet.docx` or `G04_worksheet.xlsx`. Groups can choose the format they prefer; completing both is optional.

## Submit SMILES through the web app

Submit **three Human and three AI SMILES**, with hypotheses, through the [GitHub Pages submission app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/). The app previews each structure and generates its compound ID. Record those IDs in the worksheet and confirm that the entries persist in the Dashboard after reloading.

Use the worksheet for your group observations, predictions and interpretation. Keep the submitted structures in the app and exported `.smi` file so there is one agreed submission record. Follow [step 13](13-Submit-designs.md) for the full collection and export workflow.

## Complete the worksheet during the exercise

1. **Setup and observations:** record the actual preparation/alignment settings and identify pocket features that motivate your hypotheses.
2. **Human designs:** save your three designs and predictions before requesting AI ideas.
3. **AI designs:** record model/version, proposed changes, chemistry checks and human interventions. Save the exact prompt and responses alongside the worksheet.
4. **Submission IDs:** copy the app-generated IDs, confirm receipt and nominate winners before docking results are shown.
5. **Docking results:** enter paired parent-level scores, retain selected state/pose identifiers and assess pose plausibility.
6. **Debrief:** compare the results with your original hypotheses and propose binding and functional experiments.

## Using the Excel score table

Blue cells are editable. Green cells contain formulas, including the compound IDs linked from the Submission IDs tab. Enter numeric scores in the 2A and 2B score columns; leave a missing score blank or enter `NA`. Formula results appear only when the required scores are numeric.

- **ΔS = score(2B) − score(2A):** positive values favor 2A in this docking model.
- **2A score improvement = score2A(LSD) − score2A(candidate):** positive values indicate a more favorable 2A score than LSD.
- **Selectivity score improvement = ΔS(candidate) − ΔS(LSD):** positive values indicate improvement in the selectivity score proxy.

Formulas recalculate when the workbook is opened in Excel or another compatible spreadsheet application. Scores are empirical rankings, not measured Ki values. Keep any optional hypothetical Ki* arithmetic separately labelled, as described in [step 17](17-Analyse-affinity-and-selectivity.md).

[Home](Home.md)
