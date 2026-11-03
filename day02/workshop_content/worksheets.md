# Group worksheets

Download either format and save one copy for your group:

- [Word worksheet (.docx)](downloads/Group-worksheet.docx) — editable pages with space for observations, design rationales, predictions and discussion.
- [Excel worksheet (.xlsx)](downloads/Group-worksheet.xlsx) — separate tabs for settings, observations, Human designs, AI designs, submission IDs, docking results and debrief. It calculates paired score differences and improvements relative to LSD.

Use a filename such as `G04_worksheet.docx` or `G04_worksheet.xlsx`. Choose the format you prefer; completing both is optional.

## What goes where

The worksheet holds your group's observations, predictions and interpretation. The [submission app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/smiles/) holds the six SMILES and hypotheses, previews each structure and generates its compound ID. Record those IDs in the worksheet so your notes can be matched to the submitted designs. [Step 13](13-Submit-designs.md) describes the full collection and export workflow.

1. **Setup and observations:** record the actual preparation and alignment settings, and the pocket features that motivate your hypotheses.
2. **Human designs:** save your three designs and predictions before requesting AI ideas.
3. **AI designs:** record model and version, proposed changes, chemistry checks and human interventions. Save the exact prompt and responses alongside the worksheet.
4. **Submission IDs:** copy the generated IDs, confirm receipt and nominate winners before docking results are shown.
5. **Docking results:** enter paired parent-level scores, retain the selected state and pose identifiers, and assess pose plausibility.
6. **Debrief:** compare the results with your original hypotheses and propose binding and functional experiments.

## Using the Excel score table

Blue cells are editable. Green cells contain formulas, including the compound IDs linked from the Submission IDs tab. Enter numeric scores in the 2A and 2B score columns; leave a missing score blank or enter `NA`. Formula results appear only when the required scores are numeric.

- **ΔS = score(2B) − score(2A):** positive values favor 2A in this docking model.
- **2A score improvement = score2A(LSD) − score2A(candidate):** positive values indicate a more favorable 2A score than LSD.
- **Selectivity score improvement = ΔS(candidate) − ΔS(LSD):** positive values indicate improvement in the selectivity score proxy.

[Step 17](17-Analyse-affinity-and-selectivity.md) explains how to read these numbers, including the optional hypothetical Ki\* arithmetic.

[Workshop home](index.md)
