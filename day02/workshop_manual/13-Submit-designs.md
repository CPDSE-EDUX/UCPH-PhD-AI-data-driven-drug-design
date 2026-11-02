# 13 · Collect the six designs through the interface

**Goal:** submit three Human and three AI structures with predictions before docking.

Open the [design submission dashboard](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/).

This GitHub Pages web app is the route for submitting SMILES and hypotheses. Use your [Word or Excel worksheet](Group-worksheet.md) for observations, predictions, returned compound IDs and result analysis.

1. Select your assigned **Group** and **Designed by: Human** or **AI**.
2. For Human, enter the student's name; for AI, enter the chatbot name. For a joint human design, use the agreed group designer label and note the collaboration in your worksheet.
3. Paste one isomeric **SMILES** and inspect the molecular drawing.
4. Enter a short **Hypothesis**. Include the predicted direction: for example, “2A affinity retained; 2A-over-2B selectivity increased, because …”.
5. Choose **Expected effect: Small / Medium / Large**. For this exercise, use it as a qualitative estimate of the predicted selectivity improvement over LSD, not a numerical fold-change. Put separate affinity expectations in the hypothesis.
6. Record the generated **Compound ID**, submit, and repeat for all six molecules. IDs look like `G4HPeter1` or `G4AIClaude1`; use the actual generated IDs in all subsequent files.
7. Open **Dashboard**, refresh after about a minute, and check the group filter. Confirm exactly three Human and three AI designs with the intended structures and IDs.
8. Verify persistence after reloading the page. If an entry is missing, ask the instructor to check the collection Sheet before resubmitting. The immediate confirmation alone cannot verify receipt by Google Forms.
9. Record your predicted overall winner in the worksheet and tell the instructor before the submission deadline. The interface does not have a separate winner field.

The dashboard collects designs and exports SMILES. Docking results and the final leaderboard will be handled separately by the instructor.

## Export for LigPrep

Filter **Dashboard** to your group and **all origins**, then choose **Download .smi for LigPrep**. Check that the file contains six non-empty lines, each in this format:

```text
SMILES_STRING GENERATED_COMPOUND_ID
```

The instructor exports all groups for the pooled run and adds the checked LSD control separately. Keep the submitted parent IDs intact when LigPrep generates multiple states.

If the interface is unavailable, provide the instructor with a separate `.smi` file plus the submission fields in an ID-to-hypothesis table. Record the agreed fallback submission in your worksheet before the result reveal.

**Checkpoint:** six persisted submissions, six unique IDs, an exported group file and locked predictions. The instructor closes Google Form responses and freezes the pooled export before docking results are shown.

[Previous](12-Generate-AI-designs.md) · [Home](Home.md) · [Next: ligand preparation](14-Prepare-ligands.md)
