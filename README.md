# AI- & data-driven drug design – An introduction

A one-week University of Copenhagen PhD course introducing AI- and data-driven approaches to drug design. The course combines lectures, industry examples and hands-on workshops on databases, small-molecule structure-based drug design, peptide and protein design, data visualization, and data analysis using AI and machine learning.

**Dates:** 9–13 November 2026. Lectures 09:00–12:00, lunch 12:00–13:00, hands-on workshops 13:00–17:00.

## Course days

| Day | Date | Topic | Hands-on workshop |
| --- | --- | --- | --- |
| [Day 1](day01/README.md) | Monday, 9 November | Databases | Find drug, target and disease data for an exercise or your own project. |
| [Day 2](day02/README.md) | Tuesday, 10 November | Structure-based drug design (small molecules) | Structure-based ligand optimization: human versus AI design. |
| [Day 3](day03/README.md) | Wednesday, 11 November | AI/ML tools for drug design (peptides & proteins) | *De novo* binder design for GLP-1R. |
| [Day 4](day04/README.md) | Thursday, 12 November | Data visualization | Data visualization using Claude. |
| [Day 5](day05/README.md) | Friday, 13 November | Data analysis using AI/ML | Data analysis using Claude, followed by the course wrap-up. |

Start with the [full course program](PROGRAM.md) for sessions, teachers and affiliations, or follow a day link for its description and materials.

## Course website

The whole course is published from this repository with GitHub Pages, built from the Markdown each day keeps in `dayNN/workshop_content/`.

**Website:** <https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/>

Teaching teams: see [adding your day's content](for_instructors/ADDING-CONTENT.md) for the conventions, and [publishing](for_instructors/PUBLISHING.md) to build, preview and deploy. Day 2 is a complete worked example, including a browser app for collecting molecule designs.

## Structure

```text
├── day01/ … day05/        One directory per course day
│   ├── README.md          Day description and session table
│   ├── workshop_content/  Markdown pages, images and downloads for that day's workshop
│   └── apps/              Optional browser features (Day 2: SMILES submission)
├── for_instructors/       Site builder, publishing guides and per-day teaching notes
├── assets/brand/          Logos and the day banner illustrations
├── PROGRAM.md             Full course program
└── README.md              Course overview
```

Instructor material, archives and temporary files are excluded from the published site.

## Data science learning outcomes

The course introduces participants to:

- Finding and interpreting drug, target and disease data in relevant databases.
- Using molecular structures and drug–target interactions to formulate ligand design hypotheses.
- Exploring AI/ML tools for protein modeling and peptide design.
- Choosing visual representations and using tools to communicate data.
- Preparing molecular data and exploring predictive machine learning.
- Critically assessing AI suggestions and computational predictions.

## Setup

Consult the relevant day's README for preparation and software requirements. Day 2 uses Maestro with Protein Preparation Workflow, LigPrep and Glide, a chatbot, and the SMILES submission app. Day 3 uses a Google Colab notebook, so bring a Google account. Days 4 and 5 include workshops using Claude.

## Repository conventions

This repository follows the [CPDSE educational repository conventions](https://github.com/CPDSE-EDUX/.github/blob/main/profile/README.md). The default branch holds the current course materials; completed course runs are preserved in branches named for their year.

## License

Teaching content is licensed under [CC BY 4.0](LICENSE). Code, including notebook code cells, is additionally available under the [MIT license](LICENSE-code).
