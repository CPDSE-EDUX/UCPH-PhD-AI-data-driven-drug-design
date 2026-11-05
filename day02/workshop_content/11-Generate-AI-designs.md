# 11 · Ask an AI for three designs

**Goal:** three AI-origin designs for the same problem — and an honest look at what you got.

Give the model the same information you had. Paste in the isomeric SMILES from your checked LSD entry, and your own observations from step 07:

```text
This is a computational structure-based design workshop. Start from the
following checked LSD isomeric SMILES:
[paste the parent SMILES here]

Suggest three distinct, modest modifications that aim to retain 5-HT2A binding
while reducing 5-HT2B binding, keeping the ergoline scaffold and its
stereochemistry. For each, return one isomeric SMILES, the change relative to
the parent, a short structural hypothesis, and one reason the idea might fail.

Treat selectivity as a hypothesis, not an established property. Do not invent
measured affinities.

Our structural observations from 9WPQ and 7SRS are:
[paste your observations]
```

1. Note which model you used and when.
2. Paste each SMILES into the [submission app](https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/apps/smiles/) preview, or import it into Maestro, and **look at the structure it actually drew**.
3. Check connectivity, valence, charge and stereochemistry against the parent. Does the drawing match the modification the model claimed to make?
4. Compare the contact the AI says it is making with what you can see in your own pocket view.
5. If a SMILES is invalid or encodes the wrong chemistry, ask for a correction — and keep the broken version. It is interesting.
6. Pick three valid candidates and nominate your predicted AI winner.

> **Discuss** — the model gave you a confident structural explanation. Check one of them against the pocket you looked at in step 07. Is the residue it names actually there? Is the contact it describes geometrically possible? What would you have believed if you had not checked?
> {: .discuss }

If you substantially redesign a suggestion, say so in the hypothesis field. It still counts as AI-origin for the competition.

**Checkpoint**

- [ ] Three valid AI structures.
- [ ] The prompt and responses are saved.
- [ ] Your group can describe at least one thing the AI got wrong or could not support.
- [ ] You have nominated a predicted AI winner.

[Previous](10-Choose-human-designs.md) · [Workshop home](index.md) · [Next: submit the designs](12-Submit-designs.md)
