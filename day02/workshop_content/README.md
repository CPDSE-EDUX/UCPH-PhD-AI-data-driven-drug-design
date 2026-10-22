# Design submission dashboard

[Day 2](../README.md)

Students submit their human-designed and chatbot-generated molecules one at a time from this page. The page checks each SMILES by drawing it with RDKit and generates the compound ID. It then sends the entry through a Google Form into the course Google Sheet. The Dashboard tab shows all submissions grouped by team and can export a `.smi` file for LigPrep.

**Student link:** <https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/>

## Submission fields

| Field | Input |
| --- | --- |
| Group | Dropdown, Group 1–13 |
| Designed by | Human or AI |
| Name | Student name (Human) or chatbot name (AI), saved as e.g. `Peter`, `Claude` |
| Compound ID | Generated: group + `H`/`AI` + name + sequential number, e.g. `G1HPeter1`, `G2AIClaude1` |
| SMILES | Must be valid before the form can be submitted |
| Hypothesis | One or two sentences |
| Expected effect | Small, Medium or Large |

The sequential number is the next free number for that group, origin and name, based on what is already in the Sheet.

## Instructor setup (once)

1. **Create the Google Form from the Sheet:** in the course Sheet, choose *Tools → Create a new form*. The Form is linked to the Sheet and writes to a new tab called `Form responses 1`.
2. **Add seven *Short answer* questions**, in this order: Group, Origin, Name, Compound ID, SMILES, Hypothesis, Expected effect. Keep them all as short answer with no validation, because the page does the checking. Leave email collection and sign-in off.
3. **Get the pre-filled link:** in the Form, open *⋮ → Get pre-filled link* and type each field's key as its answer: `group`, `origin`, `name`, `id`, `smiles`, `hypothesis`, `effect`. Click *Get link → Copy link*.
4. **Configure the page:** paste that link into `FORM_PREFILL_LINK` at the top of the `<script>` in [index.html](index.html). The page reads which Form field is which from those answers.
5. **Share the Sheet** as *Anyone with the link: Viewer* so the dashboard can read it.
6. **Turn on GitHub Pages:** in the repository's *Settings → Pages*, deploy from the `main` branch, root folder.

## During the workshop

- The dashboard refreshes every 60 seconds. Filter by group or origin, then click **Download .smi for LigPrep** to get `SMILES ID` lines to import into Maestro.
- A row with an ID that already exists replaces the earlier one on the dashboard. The Sheet keeps every row.
- To lock predictions before docking, turn off *Accepting responses* in the Form.
