# 12 · Ask an LLM for three design ideas

**Goal:** obtain three AI-origin hypotheses for the same design problem.

Use this starting prompt, supplying the parent isomeric SMILES exported from your checked LSD entry:

```text
Generate 3 ideas of 5HT2A-over-5HT2B selective ergoline analogs as SMILES.

This is a computational structure-based design workshop. Start from the
following checked LSD isomeric SMILES:
[paste the parent SMILES here]

Aim to retain 5-HT2A binding while reducing 5-HT2B binding. Keep the ergoline
scaffold and its specified stereochemistry. Suggest three distinct, modest
modifications. For each, return one isomeric SMILES, the change relative to
the parent, a short structural hypothesis, and one reason the idea might fail.
Treat selectivity as a hypothesis, not an established property. Do not invent
measured affinities or imply that a SMILES string establishes selectivity.

Our structural observations from 9WPQ and 7SRS are:
[paste your observations, with corresponding residue labels if available]
```

1. Save the model name, displayed version if available, date, exact prompt and first response in your group notes.
2. Paste each proposed SMILES into the interface preview or import it into Maestro.
3. Check connectivity, valence, charge and stereochemistry against the parent. Confirm that the stated modification matches the drawing.
4. Compare the AI's proposed contact with your actual pocket view. A confident explanation is not structural evidence.
5. If a string is invalid or encodes the wrong chemistry, request a correction and keep both versions in your notes. Do not select candidates based on docking scores at this stage.
6. Choose three valid AI-origin candidates and record their expected directions and uncertainties. Nominate your predicted AI winner.

If you materially redesign an AI suggestion, label that intervention in the hypothesis/notes. It remains an AI-origin submission for this exercise. Invalid ideas and correction attempts are useful outcomes to discuss, even though only the final three valid structures are submitted.

**Checkpoint:** three checked AI structures, saved prompt/response, and a short critique of at least one suggestion.

[Previous](11-Choose-human-designs.md) · [Home](Home.md) · [Next: submit six designs](13-Submit-designs.md)
