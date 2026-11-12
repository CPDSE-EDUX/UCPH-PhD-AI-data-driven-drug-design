# Discussion questions

A reference page, not a step. Every discussion prompt from the workshop, in the order the steps raise them. Each heading links to its step.

## [01 · Get to know Maestro](01-Get-to-know-Maestro.md)

In the Project Table, what is the difference between an entry being *selected* and being *included*? Try both and watch the Workspace. Which one do you think a task like docking will use as its input?

## [03 · Clean the structures](03-Clean-structures.md)

You have just deleted the G protein and arrestin. Those proteins were bound to the receptor for a reason. What does their presence tell you about the *state* each receptor was captured in, and does removing them change the pocket you are about to dock into?

## [04 · Run the diagnostics](04-Protein-diagnostics.md)

Take the main problems one at a time. What does each one actually mean for a docking calculation? Missing side chains near the pocket are not the same problem as a missing loop on the other side of the protein. Which of these would change your results, and which are cosmetic?

Click on the problems the report flags. What is it complaining about? Does anything it found sit in or near the LSD binding site?

## [05 · Prepare the proteins](05-Prepare-proteins.md)

The H-bond optimisation may flip residues in your binding site. You are about to design ligands against whichever answer it picks. How confident should you be in it? And what would it mean for your designs if it picked wrong?

## [06 · Align the receptors](06-Align-receptors.md)

Now that the bundles overlap, look at the two LSD molecules. Do they sit in the same place and the same orientation? If they differ, is that a real difference between the receptors, or an artefact of how you aligned?

## [07 · Compare the two pockets](07-Compare-interactions.md)

This is the step that decides your designs, so take your time with it.

- Which LSD contacts are present in **both** receptors? Those are the ones you probably want to keep.
- Where does the pocket have room in 2A that it does not have in 2B, or the other way round?
- Find at least one position where the two receptors present a **different residue**. Is the difference in the side chain itself, or only in the conformation it has taken?
- If you wanted to lose 2B binding without losing 2A, which part of the molecule would you change?

## [08 · Form design hypotheses](08-Form-design-hypotheses.md)

Before you draw: decide as a group what a *supportive* docking result would look like. Not "a good score" — an actual pose. Which contact must survive? Where should your new group end up? Agreeing on this now is what lets you interpret the result later.

## [09 · Draw your candidates](09-Draw-candidates.md)

Look at what you drew, not at what you meant to draw. Did the ergoline nitrogen keep its charge? Are the stereocentres still the ones LSD has? Has the ring system survived intact? Hand your molecule to someone else in the group and have them find the mistake.

## [10 · Choose the three human designs](10-Choose-human-designs.md)

Your three designs: are they three genuinely different hypotheses, or the same idea three times with different substituents? If they all fail, how much will you have learned?

## [11 · Ask an AI for three designs](11-Generate-AI-designs.md)

The model gave you a confident structural explanation. Check one of them against the pocket you looked at in step 07. Is the residue it names actually there? Is the contact it describes geometrically possible? What would you have believed if you had not checked?

## [13 · Prepare the ligand library](13-Prepare-ligands.md)

LigPrep will hand back more structures than you gave it. Before you look: which of your molecules do you expect to produce several states, and why? What does it mean for the docking that you are about to dock several versions of "the same" molecule?

## [14 · Generate the receptor grids](14-Generate-grids.md)

The box was placed using LSD. Your designs are bigger than LSD in places. What happens to a substituent that would like to reach outside the box? And since you built the two grids from two separately prepared structures, how comparable are the two scores you are about to get?

## [15 · Dock to both receptors](15-Dock-to-both-receptors.md)

While the jobs run: your LSD control is in both runs. What score do you expect it to get, and what would it tell you if LSD scored badly in a structure that was *solved with LSD in it*?

## [16 · Analyse poses and selectivity](16-Analyse-selectivity.md)

**Checks to run on each pose**

- Does the pose keep the salt bridge to the TM3 aspartate?
- Is your new substituent where you predicted it would be in step 08?
- Does the ergoline scaffold sit where LSD sits in the experimental structure?
- Does the pose look physically sensible, or is it threaded through something?

Find the pose that most clearly contradicts the hypothesis that produced it. What did the molecule do instead of what you expected? That is usually more informative than the one that worked.

The pipeline got LSD's affinity wrong by orders of magnitude, and then invented a large selectivity for a molecule that is not selective. A difference of two unreliable numbers is only more reliable than either one if their errors cancel, which needs the two calculations to be wrong in the *same way*. Two separately prepared receptors, two separately built grids: are they? And if the control's ΔScore is this far off, what does your own compound's ΔScore entitle you to claim?

## [17 · Ranking and debrief](17-Ranking-and-debrief.md)

Whatever the leaderboard says, this is thirteen groups, one scaffold, one scoring function and one afternoon. What would you actually need to run before claiming that humans or AI design better selective ligands?

**Each group gives one minute**

- What did you see, and what did you predict?
- Did the pose support it? Where did it disagree?
- What did the AI get right, and what did it get wrong?
- Which experiment would you run first to find out whether you were right?

Steps 02 and 12 have no discussion prompts.

[Workshop guide](index.md) · [Start step 01](01-Get-to-know-Maestro.md)
