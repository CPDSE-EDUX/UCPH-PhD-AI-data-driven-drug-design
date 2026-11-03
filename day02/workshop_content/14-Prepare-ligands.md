# 14 · Prepare the ligand library

**Goal:** generate chemically checked 3D ligand states for the same input library at both receptors.

1. Import your exported `.smi` using **File → Import Structures**. Confirm that the generated compound IDs become entry titles or a preserved parent-ID property.
2. Add the instructor's checked isomeric LSD reference as **LSD_control**. A group therefore has **seven parent compounds**: six designs plus the control. The control must be the same chemical input in both docking runs.
3. Open **TASKS → LigPrep** and select only these ligand entries as input.
4. Set the shared force field (**OPLS4** where available), **Epik**, target **pH 7.4 ± 1.0**, desalting and tautomer generation. Match the instructor's installed Epik version and settings.
5. Choose **Retain specified chiralities** for the SMILES input. Resolve missing intended stereochemistry before running; do not generate every possible ergoline stereoisomer as a substitute for specifying the intended molecule.
6. Name the job `G04_ligprep`, choose Maestro output, and run on the assigned host.
7. Incorporate the output and inspect the 2D structures, charges, stereochemistry and any state penalties. Keep the mapping from each generated state to its submitted parent.
8. Record the number of input parents, successful parents, generated states and failed structures. Investigate a missing parent before docking.
9. Export the prepared library as `G04_ligprep.maegz` (or the Maestro format offered by your release). Use this **same file** for both receptors.

LigPrep can create multiple protonation, tautomeric and stereochemical variants depending on its inputs and settings. The [official LigPrep configuration documentation](https://learn.schrodinger.com/public/python_api/2026-2/api/schrodinger.application.transforms.ligprep.html) describes the available state-generation controls.

A prepared state is not a new competition entry. Keep a parent ID and a unique state ID, for example `G4AIClaude1` and `G4AIClaude1_state02`. Do not overwrite the submitted SMILES with a different proposed molecule while resolving preparation problems.

**Checkpoint:** every parent is accounted for, LSD is included, and one checked prepared library is ready to dock to both receptors.

[Previous](13-Submit-designs.md) · [Home](index.md) · [Next: receptor grids](15-Generate-grids.md)
