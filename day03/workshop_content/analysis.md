# Analysis of the hand-ins

**Day 3 workshop · outcomes of 11 November**

All groups ended at the GLP-1 score level, with a candidate practically as good as the best RFD4 design they started from. The scores could no longer separate among designs. Six groups handed in 272 designs in total (90 RFD4, 179 ProteinMPNN and 3 manual), all scored against the same five reference peptides.

## Key takeaways

1. **The scores plateau at the GLP-1 level.** 142 of 272 designs (52%) have ipTM ≥ 0.90 and interface PAE ≤ 5.5 Å. Looking more closely, 4 reach GLP-1's interface PAE of 4.1 Å, and of those 1 has a similar ipSAE (0.828 vs 0.827). But keep in mind that even glucagon, a weak binder, scores similar to GLP-1 (ipTM 0.93, 4.0 Å). The scrambled control scores an ipTM of around 0.35. Scores can help separate binders from non-binders, but they do not separate strong from weak binders.
2. **RFD4 does the heavy lifting.** 23 of 90 RFD4 designs (26%) reach the top tier and every group got at least two, but 22 have an ipTM below 0.8. You also found novelty: sequence identity to GLP-1 is only 10% on average, and the most similar design has 40% identity.
3. **The best RFD4 designs have a GLP-1-like start.** 15 of 33 designs with Ala-Glu in the first six residues are top tier, against 8 of 57 without. A phenylalanine (F) at positions 6 and 22 (GLP-1 F12 and F28) occurs in 35% of top-tier designs, and in 10% and 0% of the rest.
4. **Redesign rounds rarely helped.** Only 23 of 182 children (13%) beat their parent on interface PAE, the best gain was 0.36 Å, and the median child is worse than its parent in 8 of 9 rounds. Final nominees differ from the best RFD4 design by −0.24 to +0.64 Å. This is likely due to the nature of ProteinMPNN: it takes the structure of the binder into account, but it does not "see" the receptor.
5. **The confidence scores do not see liabilities, charge or clashes.** ProteinMPNN introduced a free cysteine in 81 of 179 children, and half of the nominees carry a liability flag. RFD4 designs turned out to be relatively acidic (median net charge −3 vs −1 for GLP-1). RFD4's own clash count and the OpenFold3 clash count are unrelated, which again shows that they are completely independent methods.
6. **Hotspot count did not predict success.** Four hotspots gave 3 top-tier designs of 15, eight gave 2 and 6. The groups that included R388 got 16 of 45 top-tier designs, against 7 of 45 for the others.

> **A score is a filter, not a ranking.** A passing ipTM and interface PAE tells you a design is plausible. It does not tell you which of the many passing designs to take to the lab, and none of these numbers is a measured affinity.
> {: .warn }

## The six groups at a glance

| Group | Hotspots | RFD4 top tier (of 15) | Nominee and origin | PAE (Å) / ipSAE | Flag |
| --- | --- | --- | --- | --- | --- |
| 01 | 4 | 3 | ProteinMPNN child of RFD4 design, chosen on pose RMSD | 5.39 / 0.738 | none |
| 02 | 8 | 2 | RFD4 design with one His swap | 4.77 / 0.807 | none |
| 03 | 7 | 2 | ProteinMPNN child of RFD4 design | 4.19 / 0.795 | Cys |
| 04 | 8 | 6 | RFD4 design 08, no redesign used | 4.25 / 0.816 | none |
| 07 | 6 | 5 | round 2 child of RFD4 design 15 | 4.10 / 0.816 | Cys |
| 09 | 6 | 5 | RFD4 design 11, no redesign used | 4.83 / 0.795 | Met |

## Scores stop at the GLP-1 level

![Scatter plot of ipTM against interface PAE for 272 designs. RFD4 designs spread from interface PAE 4 to 12 Å and ipTM 0.66 to 0.93. ProteinMPNN and manual variants crowd into the top left, mostly between 4 and 6.5 Å and ipTM 0.86 to 0.93, up against dashed lines marking GLP-1 at ipTM 0.93 and interface PAE 4.11 Å.](assets/analysis-scorecards.png)

*Scorecards of groups 01, 02, 03, 04, 07 and 09: 272 designs, OpenFold3 predictions. The five reference peptides are not plotted, and 8 designs with interface PAE above 12.5 Å or ipTM below 0.6 (ipTM 0.26 to 0.68) are off the chart.*

The top tier is crowded (142 designs), and the best designs sit within 0.25 Å of GLP-1's interface PAE, less than the spread among sibling sequences in one round. A passing score therefore says little about which candidate to carry forward.

[Workshop guide](index.md) · [Day 3 overview](../README.md)
