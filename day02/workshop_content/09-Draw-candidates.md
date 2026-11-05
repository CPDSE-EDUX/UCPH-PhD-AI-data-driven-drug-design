# 09 · Draw your candidates

**Goal:** turn each hypothesis into an actual molecule.

Two routes. Route A edits LSD directly and is the quickest way to make a small, deliberate change. Route B uses Ligand Designer to enumerate variations around a position. Use whichever suits your idea — or both.

## Route A · Edit LSD directly

1. Include one of your **prepared** complexes. In the **Hierarchy**, select the ligand — its residue code in these structures is **7LD** — and copy it into a new entry. Take it from the prepared structure, not the raw one, so that the ergoline charge you checked in step 07 comes with it.

![Copying the ligand to a new entry](assets/09-copy-ligand.png)

2. Rename the new entry **`LSD`**. This is your docking control and every score today is read against it, so leave it unmodified from here on.

![Renaming the entry to LSD](assets/09-rename-lsd.png)

3. Make your change, then use **Save as New** so the original survives.

![Save as New](assets/09-save-as-new.png)

## Route B · Ligand Designer

4. In **TASKS**, open **Ligand Designer**.

![Opening Ligand Designer](assets/09-ligand-designer-task.png)

5. Click **Analyze Workspace**. It reads the pocket around your ligand and tells you what is available where.

![Analyze Workspace](assets/09-analyze-workspace.png)

6. Explore the **Display** options to see what the pocket offers.

![Ligand Designer display options](assets/09-designer-display.png)

7. To grow a substituent, use **Attach R-group**. Open the settings with the gear icon.

![R-group settings](assets/09-rgroup-settings.png)

8. Pick a **modest** number of R-groups and click **Enumerate**. Asking for hundreds will not help you choose and will slow everything down.

![Enumerating R-groups](assets/09-enumerate.png)

9. Alternatively, use **Build** to add atoms, bonds and groups by hand.

![The build tools](assets/09-build-tools.png)

## Get the SMILES out

10. Select your finished molecule, then **Edit → Copy as SMILES**.

![Copy as SMILES](assets/09-copy-as-smiles.png)

Paste it somewhere safe. You will need it in step 12.

> **Discuss** — look at what you drew, not at what you meant to draw. Did the ergoline nitrogen keep its charge? Are the stereocentres still the ones LSD has? Has the ring system survived intact? Hand your molecule to someone else in the group and have them find the mistake.
> {: .discuss }

**Checkpoint**

- [ ] You have an unmodified `LSD` entry to use as the control.
- [ ] Each participant has at least one candidate molecule.
- [ ] Every candidate's SMILES is saved somewhere you can paste from.
- [ ] Someone other than the author has checked each structure.

[Previous](08-Form-design-hypotheses.md) · [Workshop home](index.md) · [Next: choose the human designs](10-Choose-human-designs.md)
