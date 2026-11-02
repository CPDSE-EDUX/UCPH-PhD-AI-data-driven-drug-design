# 18 · Ranking, prizes and debrief

**Goal:** reward interpretable design and discuss the evidence behind the leaderboard.

Use the instructor's pooled run for the class comparison. Publish the scoring and eligibility rules before revealing results.

## Suggested awards

| Award | Rule |
| --- | --- |
| Best 2A docking result | Lowest 2A parent DockingScore among candidates with a plausible 2A pose |
| Best selectivity score | Largest ΔS among candidates with plausible poses at both receptors and a 2A score no worse than LSD_control in the pooled run |
| Best structural hypothesis | Clearest observation-to-design rationale, assessed against the saved prediction and resulting poses |

For selectivity, also show the improvement in ΔS relative to LSD. If no design passes the selectivity eligibility rule, report that outcome and award the structural-hypothesis prize. A pose should not be disqualified simply because it differs from the initial idea: explain the structural reason for any exclusion.

Show all raw results, pose flags, missing results and exclusion reasons. If rounded scores are tied or effectively indistinguishable, share the award; do not turn tiny score differences into a strong scientific claim. Hypothetical Ki* values are illustrative and do not determine prizes.

## Compare Human and AI

1. Count submitted, successfully prepared and successfully docked parents, plus valid paired results, for each origin.
2. Compare median 2A scores and median ΔS among the relevant successful parents; report the sample size and failures alongside each summary.
3. Show a scatter plot if available: **x = S2A** (more favorable to the left), **y = ΔS** (more 2A preference upward), colored by Human / AI, with LSD marked as a reference. Flag questionable poses.
4. Discuss chemically distinct ideas, invalid suggestions and corrections as well as the winning scores. Do not count multiple LigPrep states as independent designs. Flag duplicate molecules across submissions.

This is a small classroom comparison shaped by the chosen structures, prompts, human intervention and scoring protocol. It does not establish general superiority of human or AI design.

## Close the exercise

Each group gives a one-minute account:

- What did you observe, and what change did you predict would help?
- Did the pose and scores support the prediction? Where did they disagree?
- What useful idea or mistake came from the chatbot?
- Which binding experiment would test affinity and subtype selectivity? Which functional assays would establish agonism or antagonism?

Save the group worksheet, six submitted SMILES and IDs, prepared project, grid/job settings, pose files and score table. Nominate one candidate for experimental follow-up with an explicit uncertainty. A docking winner is a hypothesis worth testing, not an established selective ligand.

**Checkpoint:** the group can defend a conclusion using structure, chemistry and docking, and propose the next experiment.

[Previous](17-Analyse-affinity-and-selectivity.md) · [Home](Home.md) · [Group worksheet](Group-worksheet.md)
