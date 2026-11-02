# Design submission dashboard

[Day 2](../README.md)

[Workshop manual](../workshop_manual/Home.md) · [Participant submission instructions](../workshop_manual/13-Submit-designs.md)

Submit your human-designed and chatbot-generated molecules one at a time through this GitHub Pages app. It checks each SMILES, draws the structure and generates a compound ID. The Dashboard tab shows submissions grouped by team and can export a `.smi` file for LigPrep.

The [group worksheet is available in Word and Excel](../workshop_manual/Group-worksheet.md) for observations, predictions, returned compound IDs and docking analysis. Participants submit SMILES and hypotheses through this GitHub Pages web app and record its generated IDs in their worksheet.

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

## During the workshop

- Confirm your group has three Human and three AI entries after reloading the Dashboard. Record the generated IDs in your worksheet.
- To prepare your group library, filter by group and include both origins, then click **Download .smi for LigPrep** to get `SMILES ID` lines to import into Maestro.
- Save your predictions and nominated winner before the submission deadline. Ask an instructor if an entry is missing or needs correction.
