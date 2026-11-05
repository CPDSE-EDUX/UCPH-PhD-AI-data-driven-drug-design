# Day 2 – Structure-based drug design (small molecules)

[Course overview](../README.md) · [Full program](../PROGRAM.md)

**10 November 2026**

Explore the structure-based drug design toolbox, computational hit identification and hit-to-lead optimization, and drug–target molecular interactions. Apply these concepts in a structure-based ligand optimization workshop.

## Day program

| Session | Content | Teacher | Affiliation |
| --- | --- | --- | --- |
| Lecture 4 | The structure-based drug design toolbox<br>Docking, LigPlot, SiteMap etc. | David Gloriam | ILF, UCPH |
| Lecture 5 | Computational hit identification & hit-to-lead optimization<br>Compounds properties being optimized and case story. | Henrik Daver | Lundbeck A/S |
| Lecture 6 | Drug-target molecular interactions<br>Molecular interactions (H-bonds etc.), shape fit and its role in selectivity etc. | David Gloriam | ILF, UCPH |
| Workshop 2 | Structure-based ligand optimization<br>Competition to build the best drug | Kasper Harpsøe, Icaro Simon, Pablo Macho, Jody Pacalon, David Gloriam | ILF, UCPH |

## Workshop: Human vs AI

**Ligand design and docking evaluation towards selectivity**

Working in **groups of 2–3**, participants use Maestro to inspect LSD-bound 5-HT2A and 5-HT2B structures, propose three human designs and obtain three AI designs, then dock all six compounds to both receptors. Each participant picks or draws one human candidate; pairs develop their third together.

5-HT2A is the receptor of interest. 5-HT2B carries a well-documented cardiac-valve liability, so the brief is to keep binding at one and lose it at the other — a selectivity problem between two close relatives with very similar pockets, not an affinity problem.

Everyone runs the pipeline on their own machine, so each participant has done the preparation, grid and docking steps themselves. Instructors separately dock the pooled library of every group's compounds against shared prevalidated grids, and the awards are decided on that single run, so that all the scores being compared came out of one calculation.

**Start here: [Workshop guide](workshop_content/index.md)** · [Set up Schrödinger](workshop_content/setup.md) · [Maestro basics](workshop_content/maestro-basics.md)

**Tools:** Maestro with Protein Preparation Workflow, LigPrep and Glide; optional Ligand Designer; a chatbot; the [design submission app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/smiles/) and the [selectivity calculator](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/selectivity/).

**Starting structures:** [9WPQ, LSD-bound 5-HT2A](https://www.rcsb.org/structure/9WPQ) and [7SRS, LSD-bound 5-HT2B](https://www.rcsb.org/structure/7SRS). Use the receptor chain and retain bound LSD in each working complex.

### Apps

Two browser apps carry the workshop. Nothing to install, and no spreadsheet to fill in.

| App | What it is for | Used in |
| --- | --- | --- |
| [Submit your designs](workshop_content/submit.md) | Validates each SMILES, draws the structure and issues the compound ID that follows the molecule through docking | [Step 12](workshop_content/12-Submit-designs.md) |
| [Selectivity calculator](workshop_content/selectivity.md) | Reads the CSV exported from the Project Table and works out ΔScore, estimated Ki and fold selectivity, then ranks the designs | [Step 16](workshop_content/16-Analyse-selectivity.md) |

### Workshop steps

The guide runs in five phases: get oriented, prepare the receptors, design, dock, judge the results. [Open the workshop guide](workshop_content/index.md) for the steps, or use the sidebar on the course website. Two reference pages sit outside the numbered steps: [Set up Schrödinger](workshop_content/setup.md) and [Maestro basics](workshop_content/maestro-basics.md).

### Outputs

Each group leaves with six submitted structures and hypotheses, a saved Maestro project, paired docking results at both receptors and a comparison of human and AI design.

Every score is read against the LSD control, and the selectivity proxy is **ΔScore = score(2B) − score(2A)**, where a positive value favours 2A *in this model*. The control is also the calibration: the same pipeline misestimates LSD's own affinity and its own selectivity, which is the limit the closing discussion works from.

[Submission app guide](workshop_content/submit.md) · [Selectivity calculator](workshop_content/selectivity.md) · [References](workshop_content/references.md)
