# 16 · Dock to both receptors

**Goal:** compare the same ligand library against two receptor models under a common protocol.

## Set up the jobs

1. Open **TASKS → Ligand Docking / Glide**.
2. Select the **5-HT2A grid archive** and your checked **LigPrep output**.
3. Choose **Standard Precision (SP)** and flexible ligand sampling. Keep the common installed ligand van der Waals defaults; leave optional constraints off.
4. Enable **Add Epik state penalties to docking score** when available for your prepared library. Apply the same choice in both jobs and check that the library retains the required state-penalty properties.
5. Request up to **five output poses per prepared state**, where the panel offers that control. This supports pose inspection without excessive output. Record the actual pose limit and post-docking minimization settings.
6. Name the job `G04_2A_SP`, select the assigned host and run.
7. Repeat with the **5-HT2B grid**, the **same prepared ligand file**, and identical docking settings; name it `G04_2B_SP`.

For the distinction between the empirical scoring function and pose selection, see [Schrödinger: docking and scoring](https://www.schrodinger.com/life-science/learn/white-papers/docking-and-scoring/). DockingScore includes an Epik state penalty when configured, whereas GlideScore alone does not; see the [score definitions](https://my.schrodinger.com/support/article/27).

## Check the results before ranking

1. Monitor **JOBS**. Read the log if a job fails or produces fewer compounds than expected.
2. Incorporate each result with its matching receptor. Keep the subtype in the result-group title.
3. Inspect **LSD_control** first. Overlay its docked pose with the experimental ligand and compare the scaffold orientation and key contacts. If you compute a heavy-atom RMSD, specify atom matching and use the same receptor frame. A roughly 2 Å or better scaffold fit is a useful teaching check, not a guarantee of validity.
4. If neither site reproduces a plausible LSD pose, investigate protonation, grid placement, ligand exclusion and receptor preparation before interpreting design rankings. Use the instructor's validated outputs if needed.
5. Confirm which parents have valid poses in both receptors. Record failed or missing results as **NA** with a reason. Do not turn a failed 5-HT2B docking run into a claim of selectivity.
6. Export score properties and keep the pose files. Preserve parent IDs, state IDs and pose identifiers so that every score can be traced to the displayed pose.

The instructor docks the pooled class library live while groups follow the same operations on their own compounds. Avoid launching duplicate pooled jobs; follow the assigned job-host arrangement.

**Checkpoint:** paired 2A/2B outputs, a checked LSD redocking control, and a complete list of successful and missing parents.

[Previous](15-Generate-grids.md) · [Home](index.md) · [Next: analysis](17-Analyse-affinity-and-selectivity.md)
