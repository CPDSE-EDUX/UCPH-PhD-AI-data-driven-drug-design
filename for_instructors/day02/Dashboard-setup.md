# Design submission app: instructor setup

The student-facing app is [apps/smiles/index.html](../../day02/apps/smiles/index.html), deployed through GitHub Pages. It validates and draws SMILES with RDKit, generates compound IDs, then sends submissions through a Google Form into the course Google Sheet. The Dashboard reads that Sheet and can export `.smi` files for LigPrep.

**Student link:** <https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/smiles/>

## Instructor setup (once)

1. **Create the Google Form from the Sheet:** in the course Sheet, choose *Tools → Create a new form*. The Form is linked to the Sheet and writes to a new tab called `Form responses 1`.
2. **Add seven Short answer questions**, in this order: Group, Origin, Name, Compound ID, SMILES, Hypothesis, Expected effect. Keep them all as short answer with no validation, because the page does the checking. Leave email collection and sign-in off.
3. **Get the pre-filled link:** in the Form, open *⋮ → Get pre-filled link* and type each field's key as its answer: `group`, `origin`, `name`, `id`, `smiles`, `hypothesis`, `effect`. Click *Get link → Copy link*.
4. **Configure the page:** paste that link into `FORM_PREFILL_LINK` at the top of the `<script>` in [index.html](../../day02/apps/smiles/index.html). The page reads which Form field is which from those answers. Confirm `SHEET_ID` and `SHEET_TAB` point to the intended collection Sheet and response tab.
5. **Share the Sheet** as *Anyone with the link: Viewer* so the dashboard can read it.
6. **Configure GitHub Pages:** follow the [website publishing guide](../PUBLISHING.md). In *Settings → Pages*, choose **GitHub Actions** as the source. The course-site workflow includes this app at its existing path and embeds it in the course submission page.

## During the workshop

- Test a submission and confirm persistence after reloading; the app's no-cors POST cannot confirm Google Forms receipt directly.
- The dashboard refreshes every 60 seconds. Clear group and origin filters before the pooled export, then click **Download .smi for LigPrep** to get `SMILES ID` lines.
- A row with an ID that already exists replaces the earlier one on the dashboard. The Sheet keeps every row.
- To lock predictions before docking, turn off *Accepting responses* in the Form and save the frozen export and metadata.

[Day 2 resources](README.md) · [Student app guide](../../day02/workshop_content/submit.md) · [Instructor notes](Instructor-notes.md)
