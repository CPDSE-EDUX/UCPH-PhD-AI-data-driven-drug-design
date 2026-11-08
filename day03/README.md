# Day 3 – AI/ML tools for drug design (peptides & proteins)

[Course overview](../README.md) · [Full program](../PROGRAM.md)

**11 November 2026**

Explore AI and machine-learning tools for protein modeling and peptide drug design, with industry examples and a workshop on protein models and peptide or mini-protein binders.

## Day program

| Session | Content | Teacher | Affiliation |
| --- | --- | --- | --- |
| Lecture 7 | Software for protein modeling & peptide drug design<br>AlphaFold, Rosetta, ProteinMPNN, BindCraft … | Albert Kooistra | ILF, UCPH |
| Lecture 8 | Industry’s toolbox and case story<br>Commercially used methods and case stories | Rodrigo Alonso Ochoa | Novo Nordisk A/S |
| Lecture 9 | AI-/ML-based peptide design at Gubra | Kasper Einarson | Gubra |
| Workshop 3 | *De novo* binder design for GLP-1R<br>Design a protein binder for the GLP-1 receptor with RFD4-Proteina, ProteinMPNN and OpenFold3 in a Colab notebook. | Albert Kooistra, Jody Pacalon,<br>Jonas Verhellen, David Gloriam | ILF, UCPH |

## Workshop: *De novo* binder design for GLP-1R

Working in **groups of 3** (10 groups), participants will design a protein binder for the GLP-1 receptor, starting from the cryo-EM structure [6X18](https://www.rcsb.org/structure/6X18) of GLP-1 bound to the receptor and the G-protein. The group chooses hotspots on the GLP-1 binding site, checks how far OpenFold3 can be trusted on known peptides, generates candidate binders, redesigns the most promising parent in up to three rounds, and nominates the one candidate with the most evidence that it would bind in the lab.

Every number is a computed prediction, not a measured affinity. The workshop is about reading that evidence critically.

**Start here: [Workshop guide](workshop_content/index.md)**

**Tools:** the [workshop notebook](https://colab.research.google.com/github/CPDSE-EDUX/UCPH-PhD-AI-data-driven-drug-design/blob/main/day03/workshop_content/Workshop3_GLP1R_binder_design.ipynb) in Google Colab, with RFD4-Proteina (binder design), ProteinMPNN (sequence redesign) and OpenFold3 (independent structure prediction) running on the course server.

### Timetable

| Time | Topic |
| --- | --- |
| 13:00–13:15 | Set-up: group, token, first check |
| 13:15–13:45 | Step 1: 6X18 interface and hotspots |
| 13:45–14:10 | Step 2: calibrate OpenFold3 on known peptides |
| 14:10–14:30 | Step 3: hypothesis and 15 candidates |
| 14:30–14:45 | Rolling break |
| 14:45–15:15 | Step 4: inspect designs, re-run with OpenFold3, choose parents |
| 15:15–16:15 | Step 5: up to three redesign rounds |
| 16:15–16:35 | Step 6: compare, nominate and export |
| 16:35–17:00 | Step 7: cluster reports and class discussion |

### Outputs

Each group hands in a scorecard (CSV), one candidate card (HTML) and a three-minute report.
