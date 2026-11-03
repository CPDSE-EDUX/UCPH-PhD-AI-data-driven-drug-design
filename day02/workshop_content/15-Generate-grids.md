# 15 · Generate the two receptor grids

**Goal:** define a comparable docking search region around each bound LSD pose.

1. Include **only** the final prepared 5-HT2A receptor–LSD complex. Exclude the other receptor, free ligands and raw complexes.
2. Search **TASKS → Receptor Grid Generation**.
3. In the receptor definition, pick the bound **LSD molecule** as the reference ligand to exclude from the receptor. Check the highlighted atoms: LSD must define the site without becoming part of the rigid receptor.
4. In **Site**, center the grid on the **centroid of the selected Workspace ligand**.
5. Inspect the inner and outer boxes. The starting teaching choice is an **inner box of 10 × 10 × 10 Å** and an **outer box of 30 × 30 × 30 Å**. The instructor must verify that the outer box accommodates the candidate series in both sites; revise both grids together if necessary.
6. Keep the common receptor van der Waals settings, with no added docking constraints or optional rotatable receptor groups. Record the actual values from the panel; the course baseline uses the installed defaults consistently.
7. Name the job `G04_2A_grid` and run. Retain the grid archive, job settings and prepared receptor coordinates.
8. Repeat from the final prepared 5-HT2B complex, centering on **its own** bound LSD, with the same box dimensions and settings. Save as `G04_2B_grid`.

The inner box controls the ligand-center search region; all ligand atoms must fit in the outer box. See Schrödinger's [grid box explanation](https://my.schrodinger.com/support/article/701). The 30 Å outer box is a proposed workshop setting, not a universal default.

Do not move or re-prepare a receptor after generating its grid and then compare its poses in the new coordinates. If coordinates change, regenerate the grid or restore the matching saved receptor. Use each grid with its own receptor output.

**Checkpoint:** two completed grid archives, each associated with the correct prepared receptor, with bound LSD excluded and the site centered correctly. If time is short, use the instructor's matching grids **and receptor coordinates**.

[Previous](14-Prepare-ligands.md) · [Home](index.md) · [Next: docking](16-Dock-to-both-receptors.md)
