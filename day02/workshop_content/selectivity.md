# Selectivity calculator

Takes the CSV you export from the Maestro Project Table in [step 16](16-Analyse-selectivity.md) and turns it into a ranked comparison.

## How to use it

1. In Maestro, show only **Glide → Primary** properties, select both docking result groups, and use **Data → Export → Spreadsheet (CSV)**.
2. Drop that file above. You can drop two files if you exported each receptor separately.
3. Check that it picked the right receptor for 2A and for 2B. It guesses from the entry names; the dropdowns let you correct it.
4. Check which compound it is treating as the control — normally `LSD`.

No data leaves your computer. Everything is calculated in the browser.

## What it does with your numbers

| Column | How it is worked out |
| --- | --- |
| Score 2A, Score 2B | The **best (most negative)** docking score for that compound against that receptor |
| ΔScore | `score(2B) − score(2A)`. Positive favours 2A |
| Ki | `exp(score / RT)`, converted to µM. RT defaults to 0.5925 kcal/mol (298.15 K) and you can change it |
| Fold 2A/2B | `Ki(2B) / Ki(2A)`, which is the same as `exp(ΔScore / RT)` |
| Poses | How many poses or LigPrep states that compound had. Only the best one is used |

If a compound was only docked against one receptor, it appears in the table without a ΔScore. That is usually a sign that something failed in one of the two runs — worth finding out which.

> **A Ki here is arithmetic, not a prediction.** Running a docking score through `exp(ΔG/RT)` gives you a number with molar units. It does not give you a binding affinity. Step 16 shows how far off it is for LSD itself, in the structure LSD was solved in.
> {: .warn }

[Workshop home](index.md) · [Step 16](16-Analyse-selectivity.md) · [Submit designs](submit.md)
