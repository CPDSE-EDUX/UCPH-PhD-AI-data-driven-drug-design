# 03 · ChEMBL from Python

**Goal:** continue the thread into ChEMBL — from an approved diabetes drug to its target, the potent compounds measured on it, and molecules similar to the drug.

Work through **Part B** of the notebook.

## The idea

Open Targets tells us *which* targets and drugs matter; ChEMBL tells us *which molecules* have been measured on a target and *how potent* they are. The notebook uses the `chembl_webresource_client` package, which turns each question into one line, for example `new_client.molecule.filter(pref_name__iexact="sitagliptin")`.

**The thread in Part B:** sitagliptin (an approved diabetes drug from A4) → its target DPP4 → the most potent compounds on DPP4 → molecules similar to sitagliptin.

## The steps

- **B1 · Look up a molecule.** Sitagliptin's ChEMBL ID, highest phase, SMILES, InChIKey and a drawing of its structure. ✏️ Try `imatinib` or `ibuprofen`, then change it back.
- **B2 · Drug → target in ChEMBL.** Maps sitagliptin's target (DPP4) from an Ensembl ID to a UniProt accession to a ChEMBL target ID — the identifier mapping from the lecture.
- **B3 · Potent compounds.** Every activity on DPP4 with pChEMBL ≥ 7, cleaned to one median value per compound, with a potency histogram and the most potent structures drawn.
- **B4 · Similar molecules.** Sitagliptin's structure sent to ChEMBL's similarity search, returning molecules at least 70% similar, drawn so you can see which parts of the structure change.

## What to look for

The 2D structures are the payoff: the first similarity hits are sitagliptin and its salts (100%), and the rest share its core. Compare which fragments vary between analogues.

Next: [C · Worked example](04-worked-example.md).
