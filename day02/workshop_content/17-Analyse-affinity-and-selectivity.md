# 17 · Analyse poses, affinity and selectivity

**Goal:** determine what the docking model says about your designs and what it cannot establish.

## 1. Inspect the poses

For each parent compound, inspect its strongest-scoring poses in both receptors. Check the scaffold orientation, the conserved anchor, the proposed new contact, clashes, buried unsatisfied polar groups and unusually strained geometry. Compare with the corresponding LSD control.

Record **plausible / questionable / failed** and explain the judgment. Keep the raw score even if the pose is questionable. Do not silently substitute a worse-scoring pose because it supports your original hypothesis.

## 2. Make one paired result per parent

Use the **DockingScore** property with Epik penalties included for both receptors. Record its exact column name. Do not mix it with GlideScore, Emodel or a score from a different docking precision. The [official score definitions](https://my.schrodinger.com/support/article/27) distinguish DockingScore from GlideScore.

For the classroom summary, take the **lowest DockingScore across all returned states and poses of each parent, separately at each receptor**. Record the selected state and pose IDs. This is an optimistic parent-level convention: different states may win at the two receptors, and the minimum does not perform a thermodynamic population average. Note state mismatches and inspect whether the apparent preference depends on them.

Keep questionable poses flagged for the awards review. A parent without a score at either receptor has no paired selectivity result.

| Compound ID | Origin | S2A | 2A state / pose | S2B | 2B state / pose | ΔS | Pose assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LSD_control | Control | | | | | | |
| Your submitted ID | Human / AI | | | | | | |

Define:

```text
ΔS = S2B − S2A
```

More negative scores are more favorable within this scoring convention. A positive ΔS indicates a score preference for 5-HT2A; a negative value indicates a preference for 5-HT2B. Cross-receptor score differences are a teaching proxy and may contain receptor-dependent bias.

Compare with LSD from the **same run**:

```text
2A score improvement = S2A(LSD) − S2A(candidate)
Selectivity score improvement = ΔS(candidate) − ΔS(LSD)
```

Positive values indicate improvement according to these score metrics. A compound can improve ΔS while weakening predicted binding at both receptors, so inspect its 2A score as well.

## 3. Relate affinity to fold selectivity

For measured equilibrium inhibition constants under comparable assay conditions, define:

```text
Fold preference for 2A = Ki(2B) / Ki(2A)
pKi = −log10(Ki in mol/L)
Fold preference for 2A = 10^[pKi(2A) − pKi(2B)]
```

For example, **Ki(2A) = 10 nM** and **Ki(2B) = 100 nM** mean a **10-fold preference for 2A**. Smaller Ki means stronger binding. Do not substitute EC50 or IC50 values for Ki without a suitable assay model.

## 4. Optional: illustrate a score-to-Ki conversion

**Glide scores do not provide a validated direct conversion to Ki.** They are empirical ranking quantities; see [Schrödinger's scoring explanation](https://www.schrodinger.com/life-science/learn/white-papers/docking-and-scoring/). Use this optional exercise to understand the exponential relationship and its assumptions, not to report predicted experimental potency.

For a true standard binding free energy, the equilibrium relation is:

```text
ΔG° = RT ln(Kd / C°), with C° = 1 mol/L
```

Only under an appropriate equilibrium competitive-binding model can Ki be identified with Kd. If we additionally **pretend that a docking score S is ΔG° in kcal/mol**, define a hypothetical **Ki***:

```text
R = 0.0019872 kcal mol⁻¹ K⁻¹
T = 298 K
RT ≈ 0.5922 kcal/mol

Ki* (mol/L) = exp[S / (RT)] × 1 mol/L
Ki* (nM) = 10^9 × exp[S / (RT)]
pKi* = −S / [RT ln(10)] ≈ −S / 1.364
Fold* preference for 2A = exp[(S2B − S2A) / (RT)]
```

Illustrative arithmetic, **not actual docking results**:

| S2A | S2B | ΔS | Hypothetical Ki*2A | Hypothetical Ki*2B | Fold*2A |
| --- | --- | --- | --- | --- | --- |
| −10.0 | −8.0 | +2.0 | ≈ 46 nM | ≈ 1,360 nM | ≈ 29 |

In a spreadsheet, if `B2` contains S2A and `C2` contains S2B:

```text
ΔS:          =C2-B2
Ki*2A (nM):  =1E9*EXP(B2/(0.0019872*298))
Ki*2B (nM):  =1E9*EXP(C2/(0.0019872*298))
Fold*2A:     =EXP((C2-B2)/(0.0019872*298))
```

Use these formulas only on rows with two numeric scores; keep missing results as NA. Label every converted column **hypothetical Ki*** or **illustrative fold***. Exponentiation magnifies score differences and their uncertainty. It adds no predictive evidence and gives the same ordering as ΔS.

**Checkpoint:** a paired parent-level score table, pose judgments, comparison with LSD, and a statement about whether docking supported each original hypothesis.

[Previous](16-Dock-to-both-receptors.md) · [Home](index.md) · [Next: ranking and debrief](18-Ranking-and-debrief.md)
