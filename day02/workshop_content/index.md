# Human vs AI: ligand design and docking evaluation towards selectivity

![Fresco-style illustration: a human arm and a robotic arm locked in an evenly matched arm-wrestle](../../assets/brand/human-vs-ai.jpg){: .page-banner }

**Day 2 workshop · groups of 2–3**

Starting from LSD-bound 5-HT2A and 5-HT2B structures, design molecules that might keep 5-HT2A binding while losing 5-HT2B binding. Three human designs, three AI designs, docked into both receptors, judged on poses and scores.

## Intro slides

The slides that open the workshop introduce the receptors, the challenge and the rules. [Download the slides (PDF, 8 MB)](downloads/workshop-intro-slides.pdf)

<iframe class="pdf-embed" src="downloads/workshop-intro-slides.pdf" title="Workshop intro slides: Human vs AI challenge" loading="lazy"></iframe>

## Why this receptor pair

5-HT2A is the receptor of interest: it mediates the effects of the classical psychedelics, and compounds acting at it are being pursued for psychiatric indications. 5-HT2B is the one you want to miss. Sustained 5-HT2B agonism drives proliferation of heart valve tissue, and that liability has already removed drugs from the market — the appetite suppressant fenfluramine, and the ergoline dopamine agonist pergolide ([references](references.md#why-5-ht2a-over-5-ht2b)).

So the design problem is not "bind 5-HT2A tightly". It is "bind 5-HT2A and *not* 5-HT2B" — a selectivity problem, between two receptors that are close relatives with very similar pockets. LSD is the natural place to start, because it binds both well enough that structures exist of it in each.

> **Selectivity in this workshop is a structural hypothesis.** Docking two receptors and subtracting the scores is not a measurement, and nothing you produce today says anything about safety. [Step 17](17-Ranking-and-debrief.md) is where you take that apart.
> {: .warn }

## What you will learn

- Diagnose and prepare experimental receptor structures.
- Align two related receptors and compare their contacts and pocket shape.
- Turn a structural observation into a design hypothesis you can test.
- Draw molecules, check what you drew, and judge AI-generated SMILES.
- Prepare ligands, build grids and dock to two targets.
- Read scores alongside poses, and say what docking cannot tell you.

## Before you begin

1. **[Set up Schrödinger](setup.md)** — installation and licence, with separate instructions for KU and external participants. Do this before the workshop starts.
2. Skim **[Maestro basics](maestro-basics.md)** — the panels, the mouse and the built-in assistant.
3. Join your group. Everyone runs Maestro on their own machine, so work through the steps in parallel and compare what you each get.

Each participant brings at least one human design; the group develops a third together. Lock in your three human designs **before** you ask the AI for ideas — otherwise you are no longer comparing.

Your group submits **one** set of six designs, so you will need to agree on which three human designs go forward. Running the structure preparation yourself, rather than watching someone else do it, is the point of the morning.

If a calculation fails or runs long, ask for the instructor's checkpoint files and keep going. The science matters more than the job queue.

## The workshop in five phases

### Phase 1 · Get oriented

| Step | What you do |
| --- | --- |
| [01 · Get to know Maestro](01-Get-to-know-Maestro.md) | Fetch 9WPQ and 7SRS, find your way around the interface |
| [02 · Create and save the project](02-Create-project.md) | A named project in your group folder, with a naming convention |

### Phase 2 · Prepare the receptors

| Step | What you do |
| --- | --- |
| [03 · Clean the structures](03-Clean-structures.md) | Keep a working copy, delete everything that is not receptor or LSD |
| [04 · Run the diagnostics](04-Protein-diagnostics.md) | Find out what is wrong with a published structure |
| [05 · Prepare the proteins](05-Prepare-proteins.md) | Add hydrogens, fix the H-bond network, minimise |
| [06 · Align the receptors](06-Align-receptors.md) | Put both pockets in the same frame of reference |

### Phase 3 · Design

| Step | What you do |
| --- | --- |
| [07 · Compare the two pockets](07-Compare-interactions.md) | Interactions, surfaces and what differs between 2A and 2B |
| [08 · Form design hypotheses](08-Form-design-hypotheses.md) | Write predictions before you draw anything |
| [09 · Draw your candidates](09-Draw-candidates.md) | Edit LSD directly, or enumerate with Ligand Designer |
| [10 · Choose the human designs](10-Choose-human-designs.md) | Three molecules, locked in |
| [11 · Ask an AI for three designs](11-Generate-AI-designs.md) | And check what it gives you |
| [12 · Submit the six designs](12-Submit-designs.md) | Through the submission app, which issues the compound IDs |

### Phase 4 · Dock

| Step | What you do |
| --- | --- |
| [13 · Prepare the ligand library](13-Prepare-ligands.md) | LigPrep: states, stereochemistry, protonation |
| [14 · Generate the receptor grids](14-Generate-grids.md) | One box per receptor, centred on LSD |
| [15 · Dock to both receptors](15-Dock-to-both-receptors.md) | The same library, twice |

### Phase 5 · Judge the results

| Step | What you do |
| --- | --- |
| [16 · Analyse poses and selectivity](16-Analyse-selectivity.md) | Inspect poses, export scores, run the selectivity calculator |
| [17 · Ranking and debrief](17-Ranking-and-debrief.md) | Who won, and what the numbers are actually worth |

## Three things that are not the same

An **observation** is something you can point at in a structure. A **hypothesis** predicts what a change will do. A **docking result** tests that hypothesis inside one particular model, with all of its assumptions. None of them is a measured binding affinity.

Hold on to that distinction all day. Step 17 comes back to it.

[Start step 01](01-Get-to-know-Maestro.md) · [Selectivity calculator](selectivity.md) · [References](references.md)
