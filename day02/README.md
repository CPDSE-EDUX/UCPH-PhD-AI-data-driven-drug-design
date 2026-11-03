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

**Ligand design and docking evaluation: 5-HT2A over 5-HT2B**

Working in **groups of 2–3**, participants use Maestro to inspect LSD-bound 5-HT2A and 5-HT2B structures, propose three human designs and obtain three AI designs, then dock all six compounds to both receptors. Each participant picks or draws one human candidate; pairs develop their third together. Instructors run a pooled live docking calculation while groups follow along on their own compounds.

**Start here: [Workshop guide](workshop_content/index.md)** · [Group worksheets](workshop_content/worksheets.md)

**Tools:** Maestro with Protein Preparation Workflow, LigPrep and Glide; optional Ligand Designer; a chatbot; and the [design submission app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/smiles/).

**Starting structures:** [9WPQ, LSD-bound 5-HT2A](https://www.rcsb.org/structure/9WPQ) and [7SRS, LSD-bound 5-HT2B](https://www.rcsb.org/structure/7SRS). Use the receptor chain and retain bound LSD in each working complex.

### Workshop steps

Each step has its own page with actions, a checkpoint and screenshots of the Maestro operations.

| Phase | Steps |
| --- | --- |
| Getting started | [01 · Maestro interface](workshop_content/01-Maestro-interface.md) · [02 · Create project](workshop_content/02-Create-project.md) |
| Structure setup | [03 · Fetch structures](workshop_content/03-Fetch-structures.md) · [04 · Diagnostics](workshop_content/04-Protein-diagnostics.md) · [05 · Remove unwanted chains](workshop_content/05-Remove-unwanted-chains.md) |
| Receptor comparison | [06 · Align receptors](workshop_content/06-Align-receptors.md) · [07 · Protein preparation](workshop_content/07-Prepare-proteins.md) · [08 · Interactions and surfaces](workshop_content/08-Inspect-interactions.md) |
| Human design | [09 · Design hypotheses](workshop_content/09-Form-design-hypotheses.md) · [10 · Draw molecules](workshop_content/10-Draw-molecules.md) · [11 · Choose three human designs](workshop_content/11-Choose-human-designs.md) |
| AI and collection | [12 · Generate three AI designs](workshop_content/12-Generate-AI-designs.md) · [13 · Submit six SMILES](workshop_content/13-Submit-designs.md) |
| Live docking | [14 · Ligand preparation](workshop_content/14-Prepare-ligands.md) · [15 · Receptor grids](workshop_content/15-Generate-grids.md) · [16 · Dock to both receptors](workshop_content/16-Dock-to-both-receptors.md) |
| Evaluation | [17 · Poses, scores and selectivity](workshop_content/17-Analyse-affinity-and-selectivity.md) · [18 · Ranking and debrief](workshop_content/18-Ranking-and-debrief.md) |

### Outputs

Each group leaves with six submitted structures and hypotheses, a saved Maestro project, paired receptor docking results and a short comparison of human and AI design. The shared LSD control is the reference for the docking-score comparison, and the selectivity proxy is **DockingScore(2B) − DockingScore(2A)**, where a positive value favors 2A in this model.

[Submission app guide](workshop_content/submit.md) · [Scientific and software references](workshop_content/references.md)
