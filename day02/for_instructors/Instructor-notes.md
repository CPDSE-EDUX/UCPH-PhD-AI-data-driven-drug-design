# Instructor notes

The four-hour exercise combines structural inspection, design and live docking. Rehearse the full protocol on the teaching installation and prepare checkpoints so that calculation delays do not consume the analysis time.

## Decisions to finalize before delivery

| Item | Proposed protocol / action |
| --- | --- |
| Structures | 9WPQ and 7SRS; keep receptor plus LSD; check chain mappings in step 05 |
| Shared preparation | Step 07: pH 7.4, ligand states at 7.4 ± 1.0, OPLS4, restrained refinement, no explicit waters |
| Pocket integrity | Check unresolved segments, added side chains, covalent modifications and chemical assignments in both prepared models |
| Drawing route | Demonstrate 2D Sketcher; offer Ligand Designer if installed and licensed |
| LigPrep | Step 14; preserve specified stereochemistry and parent IDs; same prepared library for both sites |
| Grids | Step 15: proposed 10 Å inner / 30 Å outer cubes, ligand-centered, common defaults, no optional constraints |
| Docking | Step 16: SP, flexible ligands, state penalties included, up to five poses/state |
| Score convention | Lowest DockingScore per parent per receptor, with selected state/pose retained; ΔS = S2B − S2A |
| Awards | Announce step 18 rules and pose-review criteria before results |
| Ki teaching | Present the measured-Ki ratio; use score-derived Ki* only as the labelled optional illustration |

These are proposed teaching settings. GUI controls, calculation outputs and turnaround have **not** been validated by this Markdown guide. Confirm or revise the shared settings after rehearsal, then update the relevant pages and announce any course-wide changes. Record numerical vdW settings and any state/pose limits from the actual release.

## Before participants arrive

- Test each required license, job host, writable directory and browser connection on the teaching desktops. Confirm whether local or remote jobs are intended and how many concurrent jobs the class can run.
- Run both protein preparations, grids and LSD redocking controls. Inspect each pose and log. Prepare a small ligand test set to measure turnaround and verify that generated titles, parent IDs and state penalties survive export/import.
- Save matching checkpoints: raw complexes, cleaned/aligned complexes, prepared complexes, checked LSD SMILES, prepared control, both grid archives **with their matching receptor coordinates**, and example docking outputs. Distribute them through the course materials location announced in class.
- Test the submission page using a clearly marked instructor test entry. Confirm it persists in the linked Sheet after reload, that group/origin filtering works, and that the `.smi` export has the expected IDs. Remove test entries from the workshop collection before opening it.
- Check all assigned group numbers exist in the dashboard dropdown (currently Groups 1–13). Explain the definition of Expected effect and how joint human designs should be named.
- Provide the [Word and Excel worksheets](../workshop_manual/Group-worksheet.md). Groups choose one format for notes and analysis; all six SMILES and their hypotheses are collected through the GitHub Pages web app. The worksheet records returned compound IDs so the notes can be matched to submitted designs.
- Prepare a separate results spreadsheet with parent ID, origin, group, both scores, state/pose IDs, ΔS, comparison with LSD, pose assessment and eligibility. The current dashboard collects designs; it does not import scores or calculate a docking leaderboard.
- Publish and check the manual's page links and images in GitHub Wiki. Give participants a single entry URL and have a downloadable/offline copy available.

The [dashboard setup guide](Dashboard-setup.md) describes the Google Form / Sheet integration. Because the Sheet is readable for the dashboard, participants should use the agreed display names and enter only workshop content.

## Staffing and pacing

| Role | Responsibility |
| --- | --- |
| Lead instructor | Explain challenge, keep time, announce freeze and lead discussion |
| Structure / Maestro support | Help with chain selection, alignment, preparation and surfaces |
| Chemistry / AI support | Check drawn structures, stereochemistry and testable rationales |
| Docking operator | Freeze collection, prepare pooled library, run both targets and assemble results |

Roles may be combined. Groups rotate the driver and note-taker so every participant makes a design choice. At 15:25, ask groups to finish rather than expand their candidate sets. Freeze collection at approximately 15:35 and start the pooled pipeline immediately; prevalidated receptor grids can make the pooled run independent of student grid jobs.

## Freeze and pooled calculation

1. Confirm six entries per group: three Human and three AI. Save predictions and nominated winners outside the dashboard if necessary.
2. Turn off **Accepting responses** in the Google Form. Export the complete dashboard with group and origin filters cleared, and save a copy of the metadata table / collection Sheet snapshot.
3. Check duplicate IDs and duplicate chemical structures. Resolve accidental duplicate submissions before the freeze; if duplicate molecules legitimately occur across designers, flag them and avoid treating them as independent evidence.
4. Add one checked `LSD_control` parent to the pooled library. With N complete groups there should be **6N + 1 parents** before LigPrep. State expansion will increase the docking input count.
5. Run the common LigPrep protocol once. Save parent-to-state mapping, input/output counts, settings and failures. Use the identical prepared file at both receptors.
6. Dock using the prevalidated grids and common SP settings. Preserve all logs, pose files and per-state scores. Use the pooled results for awards even if local group results differ.
7. Join paired results by parent ID, not row position. Summarize by the stated rule, keep missing results as NA, and flag different winning states.
8. Review poses with a second instructor for award contenders. Show raw scores and explicit exclusion reasons as well as the eligible ranking.

## Contingencies

| Problem | Continue with |
| --- | --- |
| Fetching or chain editing fails | Raw or cleaned coordinate checkpoint; still discuss chain identity |
| Preparation takes too long | Shared prepared complex; inspect its diagnostics and settings |
| Alignment is poor | Instructor-aligned pair; compare residue mapping and local fit |
| Drawing tool unavailable | 2D Sketcher, or checked isomeric SMILES supplied through the instructor |
| Submission service unavailable | Timestamped local `.smi` plus metadata tables; freeze before showing scores |
| Grid or student docking queue stalls | Matching shared grids/receptors or pooled outputs |
| Pooled jobs miss the deadline | Clearly labelled rehearsal/example results for analysis; defer prizes on submitted designs |
| No valid pose at 2B | NA selectivity, investigate failure; do not interpret as no binding |

Do not describe rehearsal results as live results for the submitted designs. Preserve at least 25 minutes for pose and score interpretation, even if calculations become a demonstration.

## Debrief emphasis

Keep affinity, selectivity and functional activity separate. Discuss receptor-state and preparation dependence, missing waters, rigid-receptor approximations, ligand-state choices and score uncertainty. Pair an empirical binding assay at both receptors with functional characterization before drawing conclusions about agonism, antagonism or biological benefit.

[Instructor resources](README.md) · [Manual home](../workshop_manual/Home.md) · [References](../workshop_manual/References.md)
