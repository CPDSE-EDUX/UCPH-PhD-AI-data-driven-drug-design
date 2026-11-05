# 03 · Clean the structures

**Goal:** one receptor plus LSD in each working entry, and nothing else.

A deposited structure contains whatever was needed to get a picture: G proteins, antibodies, waters, lipids, buffer. For docking you want the receptor and its ligand.

## Work on a copy

1. Right-click each entry and choose **Duplicate → In place**. Do this for both structures.

![Duplicating an entry](assets/03-duplicate-entry.png)

2. Rename the duplicates from `raw` to **`edit`** — `2a_9WPQ_edit` and `2b_7SRS_edit`.

![Renaming the duplicate to edit](assets/03-rename-edit.png)

3. Select both `raw` entries (hold `Ctrl`/`Cmd`), right-click, and put them in a **New group** called `archive`.

![Creating a new group](assets/03-new-group.png)

![The archive group in the Project Table](assets/03-archive-group.png)

Deleting atoms is not undoable once you have moved on. The archive is your way back.

## Delete what you do not need

4. Include one `edit` entry. In the **Hierarchy** panel, work through the chains one at a time and watch which atoms highlight in the Workspace.

![Chains listed in the Hierarchy panel](assets/03-hierarchy-chains.png)

5. Delete everything that is not the receptor or LSD: the G protein or arrestin, antibody chains, waters, lipids and buffer components.

![Deleting a chain](assets/03-delete-chain.png)

6. Repeat for the second structure.

![Both cleaned entries](assets/03-cleaned-entries.png)

7. In **7SRS** there is a second "ligand" that is actually a phosphopeptide from the receptor C-terminus. It sits far from the LSD site, so remove it too.

![The phosphopeptide in 7SRS](assets/03-7srs-phosphopeptide.png)

> **Discuss** — you have just deleted the G protein and arrestin. Those proteins were bound to the receptor for a reason. What does their presence tell you about the *state* each receptor was captured in, and does removing them change the pocket you are about to dock into?
> {: .discuss }

> **Not sure whether something belongs?** Waters, lipids and buffer go. Disulfides stay. If you find a covalent modification or something that looks like a cofactor, ask an instructor rather than guessing.
> {: .warn }

**Checkpoint**

- [ ] Both `raw` entries are safe in the `archive` group.
- [ ] Each `edit` entry shows one seven-helix receptor with LSD in the pocket.
- [ ] No transducer, antibody or peptide chains remain.
- [ ] The Hierarchy confirms it — not just the picture.

[Previous](02-Create-project.md) · [Workshop home](index.md) · [Next: run the diagnostics](04-Protein-diagnostics.md)
