# 04 · Worked example: a novel-mechanism diabetes drug

**Goal:** put the pieces together to answer a real question — which proteins could be targeted to treat type 2 diabetes that are **not** already the targets of approved diabetes drugs?

Work through **Part C** of the notebook. The instructor walks through this part live; you then repeat it for your own disease in [Part D](05-your-project.md).

## The five steps

| Step | Database | What it does |
| --- | --- | --- |
| 1 | Open Targets | Download the 300 targets most associated with the disease, with their evidence types |
| 2 | Open Targets (from ChEMBL) | List every drug for the disease, with its mechanism of action and targets |
| 3 | — | Remove the targets that approved drugs already hit; what remains is "novel" |
| 4 | Open Targets | Profile the candidates: class, tractability, location, drugs for other diseases |
| 5 | ChEMBL | For one candidate: potent compounds and similar molecules |

Only one line changes between diseases: the disease ID at the top of Part C.

## What the results show

- A heat map of the evidence behind the top targets — notice which are supported by **genetics** and which mostly by **literature**.
- The targets of approved diabetes drugs, which are then removed.
- A scatter of the remaining candidates by overall score and genetic evidence, marking which can be reached by a small molecule.
- Tissue expression for a chosen candidate, and its chemistry in ChEMBL.

## Questions to discuss

- Which candidates have strong *genetic* evidence, and which rely mostly on literature?
- Which already have approved drugs for other diseases (a repurposing opportunity), and which have none?
- Small molecule, antibody or another modality — given the target's location and tractability?
- What could go wrong: safety, expression in other tissues, redundancy with existing mechanisms?

Next: [D · Your group project](05-your-project.md).
