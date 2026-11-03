# Human vs AI: ligand design and docking evaluation

**Day 2 workshop · groups of 2–3**

Starting from LSD-bound 5-HT2A and 5-HT2B structures, design molecules that might retain 5-HT2A binding while reducing 5-HT2B binding. Compare three human designs with three AI suggestions, dock all six to both receptors, and evaluate the hypotheses using poses and scores.

Use **Maestro** throughout, with Protein Preparation Workflow, LigPrep and Glide, plus a chatbot and the [submission app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/smiles/). Ligand Designer is an optional drawing route. Menu labels vary between Maestro releases; use **TASKS** to search for the named tool if its location differs.

## What you will learn

- Diagnose and prepare experimental receptor structures.
- Align related receptors and compare ligand contacts and pocket shape.
- Turn structural observations into affinity and selectivity hypotheses.
- Draw molecules, check stereochemistry, and evaluate AI-generated SMILES.
- Prepare ligands, generate receptor grids, and dock to two targets.
- Interpret scores alongside poses, and distinguish docking rankings from measured affinity.

## Before you begin

Join your assigned group and download the [Word or Excel worksheet](worksheets.md). Save one group copy for observations, predictions and analysis. Submit the six SMILES and their hypotheses through the [submission app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/smiles/) in step 13, and record its generated compound IDs in the worksheet.

Rotate the mouse, note-taking and chemistry-checking roles. Each participant proposes at least one human design; a pair develops its third design together. Save three human designs before requesting the three AI designs.

You need Maestro with the required licenses and job host, a writable working folder, a browser and chatbot access. The instructor confirms the common calculation settings. If a job stalls, ask for the corresponding instructor checkpoint and continue with the scientific exercise.

## Workshop steps

| Step | Activity | Checkpoint |
| --- | --- | --- |
| [01](01-Maestro-interface.md) | Explore the Maestro interface | Find entries, workspace, TASKS and JOBS |
| [02](02-Create-project.md) | Create and save a project | Named project and working directory |
| [03](03-Fetch-structures.md) | Fetch 9WPQ and 7SRS | Two intact LSD-bound complexes |
| [04](04-Protein-diagnostics.md) | Inspect protein preparation diagnostics | Missing features and their significance recorded |
| [05](05-Remove-unwanted-chains.md) | Remove unwanted chains | One receptor plus LSD per working entry |
| [06](06-Align-receptors.md) | Align receptors | Receptor cores and pockets overlap |
| [07](07-Prepare-proteins.md) | Prepare proteins | Two checked, prepared complexes |
| [08](08-Inspect-interactions.md) | Compare contacts and binding-site surfaces | Matched pocket views and observations |
| [09](09-Form-design-hypotheses.md) | Think about interactions and cavities | Affinity and selectivity hypotheses |
| [10](10-Draw-molecules.md) | Draw in 2D Sketcher or Ligand Designer | Valid candidate structures |
| [11](11-Choose-human-designs.md) | Choose one design per participant | Three human designs locked |
| [12](12-Generate-AI-designs.md) | Ask an LLM for three ideas | Three checked AI suggestions |
| [13](13-Submit-designs.md) | Collect six SMILES through the app | Three Human + three AI entries |
| [14](14-Prepare-ligands.md) | Run LigPrep | Prepared candidates and LSD control |
| [15](15-Generate-grids.md) | Generate receptor grids | One grid per prepared receptor |
| [16](16-Dock-to-both-receptors.md) | Dock the same library to both | Two sets of poses and scores |
| [17](17-Analyse-affinity-and-selectivity.md) | Analyse scores, Ki and fold selectivity | Pose assessment and paired score table |
| [18](18-Ranking-and-debrief.md) | Rank, award prizes and discuss | Defensible conclusion and next experiment |

## Keep these distinctions in view

An observation is something you can point to in a structure. A design hypothesis predicts what a modification might change. A docking result tests that hypothesis within a particular model. Experimental binding and functional assays are needed to establish affinity, subtype selectivity and activity.

[Start step 01](01-Maestro-interface.md) · [Group worksheet](worksheets.md) · [References](references.md)
