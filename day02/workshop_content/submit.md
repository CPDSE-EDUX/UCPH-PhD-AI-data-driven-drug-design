# Submit your molecule designs

Submit your human-designed and chatbot-generated molecules one at a time. The app checks each SMILES, draws the structure and generates a compound ID. The Dashboard tab shows submissions grouped by team and can export a `.smi` file for LigPrep.

Follow [step 12](12-Submit-designs.md) for the full submission and export workflow. Note the generated compound IDs against your hypotheses — they follow each molecule through docking and into the [selectivity calculator](selectivity.md).

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

The sequential number is the next free number for that group, origin and name, based on what has already been submitted.

## During the workshop

- Confirm your group has three Human and three AI entries after reloading the Dashboard.
- To prepare your group library, filter by group and include both origins, then choose **Download .smi for LigPrep** to get `SMILES ID` lines to import into Maestro.
- Save your predictions and nominated winner before the submission deadline. Ask an instructor if an entry is missing or needs correction.
