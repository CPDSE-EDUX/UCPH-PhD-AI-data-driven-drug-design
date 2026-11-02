# Day 2 – Structure-based drug design (small molecules)

[Course overview](../README.md) · [Full program](../PROGRAM.md)

**10 November 2026** · Lectures 09:00–12:00 · Lunch 12:00–13:00 · Workshop 13:00–17:00

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

**Start here: [Workshop manual](workshop_manual/Home.md)** · [Word worksheet](workshop_manual/downloads/Group-worksheet.docx) · [Excel worksheet](workshop_manual/downloads/Group-worksheet.xlsx) · [Instructor notes](workshop_manual/Instructor-notes.md)

**Tools:** Maestro with Protein Preparation Workflow, LigPrep and Glide; optional Ligand Designer; a chatbot; and the [design submission dashboard](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/).

**Starting structures:** [9WPQ, LSD-bound 5-HT2A](https://www.rcsb.org/structure/9WPQ) and [7SRS, LSD-bound 5-HT2B](https://www.rcsb.org/structure/7SRS). Use the receptor chain and retain bound LSD in each working complex.

### Manual structure

Each step has its own Markdown page with actions, a checkpoint and previous/next navigation. The manual includes screenshots of the Maestro operations.

| Phase | Step-by-step guide |
| --- | --- |
| Getting started | [01 · Maestro interface](workshop_manual/01-Maestro-interface.md) · [02 · Create project](workshop_manual/02-Create-project.md) |
| Structure setup | [03 · Fetch structures](workshop_manual/03-Fetch-structures.md) · [04 · Diagnostics](workshop_manual/04-Protein-diagnostics.md) · [05 · Remove unwanted chains](workshop_manual/05-Remove-unwanted-chains.md) |
| Receptor comparison | [06 · Align receptors](workshop_manual/06-Align-receptors.md) · [07 · Protein preparation](workshop_manual/07-Prepare-proteins.md) · [08 · Interactions, surfaces and side-by-side views](workshop_manual/08-Inspect-interactions.md) |
| Human design | [09 · Interaction and cavity hypotheses](workshop_manual/09-Form-design-hypotheses.md) · [10 · Draw molecules](workshop_manual/10-Draw-molecules.md) · [11 · Choose three human designs](workshop_manual/11-Choose-human-designs.md) |
| AI and collection | [12 · Generate three AI designs](workshop_manual/12-Generate-AI-designs.md) · [13 · Submit six SMILES](workshop_manual/13-Submit-designs.md) |
| Live docking | [14 · Ligand preparation](workshop_manual/14-Prepare-ligands.md) · [15 · Receptor grids](workshop_manual/15-Generate-grids.md) · [16 · Dock to both receptors](workshop_manual/16-Dock-to-both-receptors.md) |
| Evaluation | [17 · Poses, scores, Ki and fold selectivity](workshop_manual/17-Analyse-affinity-and-selectivity.md) · [18 · Ranking, prizes and debrief](workshop_manual/18-Ranking-and-debrief.md) |

### Afternoon schedule

| Time | Activity |
| --- | --- |
| 13:00–13:10 | Introduction, Maestro interface and project |
| 13:10–13:35 | Fetch structures, inspect diagnostics, remove chains and align |
| 13:35–13:55 | Protein preparation and checks |
| 13:55–14:20 | Ligand contacts, binding-site surfaces and receptor comparison |
| 14:20–14:35 | Affinity and selectivity hypotheses |
| 14:35–14:45 | Break |
| 14:45–15:10 | Draw and select three human candidates |
| 15:10–15:25 | Generate and check three AI candidates |
| 15:25–15:35 | Submit designs and lock predictions |
| 15:35–16:25 | LigPrep, grid generation and live paired docking |
| 16:25–16:50 | Analyse poses, affinity and selectivity |
| 16:50–17:00 | Rankings, prizes and discussion |

The [manual home](workshop_manual/Home.md) gives the detailed step timings. Instructors provide matching prepared files if calculation delays would reduce analysis time.

### Outputs and interpretation

Each group leaves with six submitted structures and hypotheses, a saved Maestro project, paired receptor docking results and a short comparison of Human and AI design. The shared LSD control provides the reference for the docking-score comparison.

Groups choose a Word or Excel worksheet for their observations, predictions and analysis. They submit the six SMILES and hypotheses through the [GitHub Pages web app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/) and record its generated compound IDs in the worksheet. The Excel version calculates paired docking-score differences and comparisons with LSD.

The selectivity score proxy is **DockingScore(2B) − DockingScore(2A)**; a positive value favors 2A in this model. Scores are empirical rankings. The analysis guide separates measured Ki ratios from an optional, explicitly hypothetical score-to-Ki calculation. Pose plausibility and experimental follow-up remain central to interpreting any leaderboard.

### GitHub Wiki delivery

**GitHub Wiki is a good fit for the participant manual**, with short linked pages and a sidebar. Keep the Markdown in this repository as the reviewed source and publish it to the Wiki for delivery. The Wiki uses a separate Git repository, so source edits need a separate publication step; see [GitHub's Wiki workflow](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages).

The [publishing guide](workshop_manual/PUBLISHING.md) explains local staging, namespaced pages for the shared course Wiki, screenshot links and publication checks. The Wiki has not been published by adding these files. The submission interface remains on GitHub Pages.

### Files and supporting guides

```text
day02/
├── README.md                  Day program and workshop entry point
├── workshop_manual/
│   ├── Home.md                Participant landing page and schedule
│   ├── 01-…md through 18-…md  One page per workflow step
│   ├── Group-worksheet.md     Worksheet downloads and instructions
│   ├── Instructor-notes.md    Rehearsal, pooled docking and contingencies
│   ├── References.md          Scientific and software sources
│   ├── _Sidebar.md            Manual navigation
│   ├── PUBLISHING.md          GitHub Wiki delivery instructions
│   ├── export_wiki.py         Local Wiki staging; no automatic publication
│   ├── build_worksheets.py    Regenerate the editable worksheets
│   ├── downloads/             Word and Excel group worksheets
│   └── assets/                Maestro screenshots
├── workshop_content/          Design submission dashboard and setup guide
├── workshop_materials/        Teaching materials
└── slides/                    Lecture slides
```

[Dashboard setup](workshop_content/README.md) · [Scientific and software references](workshop_manual/References.md) · [Wiki publishing](workshop_manual/PUBLISHING.md)
