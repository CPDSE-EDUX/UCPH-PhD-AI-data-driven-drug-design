# 17 · Ranking and debrief

**Goal:** hand out the prizes, then take them apart.

## The awards

Two prizes: one for the best **human** design, one for the best **AI** design.

| Award | How it is decided |
| --- | --- |
| **Best human design** | Largest ΔScore among the Human submissions, counting only compounds with plausible poses at *both* receptors and a 2A score no worse than the LSD control |
| **Best AI design** | The same rule, among the AI submissions |

Each prize goes to the group that submitted the winning compound. Origin is the `H` or `AI` in the compound ID from step 12, so one group can take both.

A pose that disagrees with your hypothesis is not disqualified. A pose that is physically implausible is. If nobody on one side passes the selectivity rule, that is a result worth announcing.

> **The awards are judged on the pooled run, not your local one.** Every group's compounds are docked once, against the same two prevalidated grids, so that the scores being compared came out of one calculation. Your own numbers from step 15 will be close but not identical — you prepared your own receptors and built your own grids. That gap between two runs of the same molecule is itself worth a look.
> {: .tip }

Where scores are a few tenths of a kcal/mol apart, share the prize. Turning a 0.2 kcal/mol difference into a winner teaches exactly the wrong lesson.

## Human versus AI

Compare, for each origin: how many designs were submitted, how many survived LigPrep, how many docked, and the median 2A score and ΔScore of the ones that did. Report the failures next to the successes — a method that produces three brilliant molecules and twelve invalid SMILES is not obviously better than one that produces six adequate ones.

Do not count multiple LigPrep states of one molecule as separate designs.

> **Discuss** — whatever the leaderboard says, this is thirteen groups, one scaffold, one scoring function and one afternoon. What would you actually need to run before claiming that humans or AI design better selective ligands?
> {: .discuss }

## What this exercise could not tell you

Go through these as a group. Each one is a real limitation of what you did today:

- **A docking score is not a binding free energy.** It is an empirical function fitted to reproduce rankings across diverse systems. You saw it miss LSD's affinity by orders of magnitude.
- **The Ki numbers are arithmetic, not predictions.** Converting a score with `exp(ΔG/RT)` gives a number with units. It does not give it meaning.
- **Everything was rigid.** The receptor could not move. Real binding sites reorganise around a ligand.
- **Solvent was absent.** Desolvation is often the dominant term in selectivity, and you deleted the waters.
- **One structure per receptor.** You designed against two particular conformational snapshots, each with its own preparation decisions.
- **Selectivity is not the only thing that matters.** Nothing today addressed whether these molecules could be synthesised, whether they are agonists or antagonists, or what they would do at the dozens of other receptors an ergoline will hit.
- **The comparison was shaped by the prompt.** You gave the AI your observations. A different prompt gives different molecules.

## Close

Each group gives one minute:

- What did you see, and what did you predict?
- Did the pose support it? Where did it disagree?
- What did the AI get right, and what did it get wrong?
- Which experiment would you run first to find out whether you were right?

A docking winner is a hypothesis worth testing. That is all it is — and it is not nothing.

**Checkpoint**

- [ ] Your group can defend a conclusion using structure, chemistry and scores.
- [ ] You have named the next experiment and what it would resolve.
- [ ] You can state one thing today's method cannot tell you.
- [ ] The Maestro project and your exported results are saved.

[Previous](16-Analyse-selectivity.md) · [Workshop home](index.md) · [Selectivity calculator](selectivity.md)
