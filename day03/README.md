# Day 3 – AI/ML tools for drug design (peptides & proteins)

[Course overview](../README.md) · [Full program](../PROGRAM.md)

**11 November 2026**

Explore AI and machine-learning tools for protein modeling and peptide drug design, with industry examples and a workshop on protein models and peptide or mini-protein binders.

## Day program

| Session | Content | Teacher | Affiliation |
| --- | --- | --- | --- |
| Lecture 7 | Deep learning for protein structure and protein design - from folding to co-folding to design | [Albert Kooistra](https://www.linkedin.com/in/ajkooistra/) | ILF, UCPH |
| Lecture 8 | Industry’s toolbox and case story<br>Commercially used methods and case stories | [Rodrigo Alonso Ochoa](https://www.linkedin.com/in/rodrigo-ochoa-compchem) | Novo Nordisk A/S |
| Lecture 9 | AI-/ML-based peptide design at Gubra | [Kasper Einarson](https://www.linkedin.com/in/kasper-einarson-a26104159/) | Gubra |
| Workshop 3 | *De novo* binder design for GLP-1R<br>Design a protein binder for the GLP-1 receptor with RFD4-Proteina, ProteinMPNN and OpenFold3 in a Colab notebook. | [Albert Kooistra](https://www.linkedin.com/in/ajkooistra/), [Jody Pacalon](https://www.linkedin.com/in/jody-pacalon-56668214b),<br>[Jonas Verhellen](https://www.linkedin.com/in/jonas-verhellen-634bba12b/))| ILF, UCPH |

## Lectures

Download the lecture slides (PDF):
- [Lecture 7 – Deep learning for protein structure and protein design - from folding to co-folding to design](lectures/Lecture7_AJKooistra.pdf)
- [Lecture 8 – Modelling and cheminformatics approaches for peptide analysis and design](lectures/L8_Modelling%20and%20cheminformatics....pdf)

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

### Outcomes

The groups handed in 272 scored designs. The scores plateau at the GLP-1 level, redesign rounds rarely improved on the best RFD4 design, and the confidence scores say nothing about liabilities or charge. Read the full [analysis of the hand-ins](workshop_content/analysis.md).
