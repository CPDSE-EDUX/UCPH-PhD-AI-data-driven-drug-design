# Human vs AI: ligand design and docking evaluation

**Day 2 · 10 November 2026 · 13:00–17:00 · Groups of 2–3**

Starting from LSD-bound 5-HT2A and 5-HT2B structures, design molecules that might retain 5-HT2A binding while reducing 5-HT2B binding. Compare three human designs with three AI suggestions, dock all six to both receptors, and evaluate the hypotheses using poses and scores.

Use **Maestro** throughout, with Protein Preparation Workflow, LigPrep and Glide, plus a chatbot and the [submission dashboard](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/). Ligand Designer is an optional drawing route. Menu labels vary between Maestro releases; use **TASKS** to search for the named tool if its location differs.

## What you will learn

- Diagnose and prepare experimental receptor structures.
- Align related receptors and compare ligand contacts and pocket shape.
- Turn structural observations into affinity and selectivity hypotheses.
- Draw molecules, check stereochemistry, and evaluate AI-generated SMILES.
- Prepare ligands, generate receptor grids, and dock to two targets.
- Interpret scores alongside poses, and distinguish docking rankings from measured affinity.

## Before you begin

Join your assigned group and download the [Word worksheet](downloads/Group-worksheet.docx) or [Excel worksheet](downloads/Group-worksheet.xlsx). Save one group copy for observations, predictions and analysis. Submit the six SMILES and their hypotheses through the [GitHub Pages web app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/) in step 13; record its generated compound IDs in the worksheet.

Rotate the mouse, note-taking and chemistry-checking roles. Each participant proposes at least one human design; a pair develops its third design together. Save three human designs before requesting the three AI designs.

You need a working Maestro installation or teaching desktop with the required licenses and job host, a writable working folder, a browser, and chatbot access. The instructor will confirm the common calculation settings. If a job stalls, ask for the corresponding instructor checkpoint and continue with the scientific exercise.

## Follow the manual

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
| [13](13-Submit-designs.md) | Collect six SMILES through the interface | Three Human + three AI entries |
| [14](14-Prepare-ligands.md) | Run LigPrep | Prepared candidates and LSD control |
| [15](15-Generate-grids.md) | Generate receptor grids | One grid per prepared receptor |
| [16](16-Dock-to-both-receptors.md) | Dock the same library to both | Two sets of poses and scores |
| [17](17-Analyse-affinity-and-selectivity.md) | Analyse scores, Ki and fold selectivity | Pose assessment and paired score table |
| [18](18-Ranking-and-debrief.md) | Rank, award prizes and discuss | Defensible conclusion and next experiment |

## Afternoon schedule

| Time | Steps | Activity |
| --- | --- | --- |
| 13:00–13:10 | 01–02 | Introduction, interface and project |
| 13:10–13:25 | 03–04 | Import and diagnostics |
| 13:25–13:35 | 05–06 | Clean up and align |
| 13:35–13:55 | 07 | Protein preparation and checks |
| 13:55–14:20 | 08 | Interactions, surfaces and comparison |
| 14:20–14:35 | 09 | Design hypotheses |
| 14:35–14:45 | — | Break |
| 14:45–15:10 | 10–11 | Human drawing and selection |
| 15:10–15:25 | 12 | AI suggestions and checks |
| 15:25–15:35 | 13 | Submission and predictions locked |
| 15:35–15:50 | 14 | Ligand preparation |
| 15:50–16:05 | 15 | Grid generation |
| 16:05–16:25 | 16 | Live pooled docking; groups dock their own designs |
| 16:25–16:50 | 17 | Pose inspection, affinity and selectivity analysis |
| 16:50–17:00 | 18 | Awards and discussion |

Calculation times depend on hardware, licenses and the number of ligand states. The instructor may provide prepared files to preserve time for analysis.

## Keep these distinctions in view

An observation is something you can point to in a structure. A design hypothesis predicts what a modification might change. A docking result tests that hypothesis within a particular model. Experimental binding and functional assays are needed to establish affinity, subtype selectivity and activity.

[Start step 01](01-Maestro-interface.md) · [Group worksheet](Group-worksheet.md) · [Instructor notes](Instructor-notes.md) · [References](References.md)
