# References and further reading

## Experimental structures

- [RCSB PDB 9WPQ](https://www.rcsb.org/structure/9WPQ): LSD-bound 5-HT2A complex. Use its entry and validation report to check identity, chain annotations and coordinate quality.
- [RCSB PDB 7SRS](https://www.rcsb.org/structure/7SRS): LSD-bound 5-HT2B–β-arrestin-1 complex, with chain annotations and validation report.
- [Li et al., Structure-based design of subtype-selective psychedelic analogs](https://doi.org/10.1038/s41467-026-77658-y): primary publication associated with 9WPQ. Suitable for reading after the prospective design exercise.
- [Cao et al., Signaling snapshots of a serotonin receptor activated by the prototypical psychedelic LSD](https://doi.org/10.1016/j.neuron.2022.08.006): primary publication associated with 7SRS and related receptor states.

## Why 5-HT2A over 5-HT2B

- [Rothman et al., *Circulation* 2000;102:2836–2841](https://doi.org/10.1161/01.cir.102.23.2836): the work linking 5-HT2B agonism to the valve disease seen with fenfluramine, and the origin of the recommendation that serotonergic drugs be screened for 5-HT2B activity.
- [Zanettini et al., *N Engl J Med* 2007;356:39–46](https://doi.org/10.1056/NEJMoa054830): valvular heart disease in patients treated with the ergoline dopamine agonists pergolide and cabergoline. The clinical reason an ergoline scaffold with 5-HT2B activity is a liability.

## Maestro, preparation and Glide

- [Protein Preparation Workflow overview](https://www.schrodinger.com/life-science/learn/white-papers/protein-preparation-workflow/): chemical repair, protonation and restrained refinement.
- [Protein Ligand Docking lesson plan](https://www.schrodinger.com/wp-content/uploads/2023/11/gb-docking-ls.pdf): an official worked workflow for preparation, grids, docking and analysis. Its example system and interface release differ from this workshop.
- [LigPrep configuration documentation](https://learn.schrodinger.com/public/python_api/2026-2/api/schrodinger.application.transforms.ligprep.html): state-generation and stereochemistry controls; use installed panel help for your GUI release.
- [Impact of grid box sizes on Glide docking](https://my.schrodinger.com/support/article/701): distinction between ligand-center and enclosing boxes.
- [How to configure and interpret Glide docking scores](https://my.schrodinger.com/support/article/27): GlideScore, DockingScore and Epik penalties.
- [Docking and scoring](https://www.schrodinger.com/life-science/learn/white-papers/docking-and-scoring/): empirical scoring and the use of docking results.

Screenshots in this guide come from Maestro 2026-4. If a panel or a setting is not where the guide shows it, use the installed **Help** for that panel or ask the Maestro Assistant. Where a setting changes the result rather than only the view, check with an instructor before changing it — the comparison between groups at the end of the day only holds if everyone docked the same way.

[Workshop home](index.md)
