# De novo binder design for GLP-1R

**Day 3 workshop · groups of 4 · 13:00–17:00**

In four hours your group will design a protein binder for the GLP-1 receptor and nominate the one candidate with the most evidence that it could be a good binder in the lab.

You will make the scientific decisions; the notebook handles the infrastructure.

The receptor is GLP-1R, and we start from the cryo-EM structure [6X18](https://www.rcsb.org/structure/6X18), which holds GLP-1 on the receptor together with the G-protein. The structure shows where GLP-1 sits in the receptor, and we will try to exploit that same region during the *de novo* design.

## What you will do

1. Look at how GLP-1 sits in the receptor in 6X18 and identify hotspots.
2. Check how far OpenFold3 can be trusted on known peptides, including a scrambled one.
3. Write a hypothesis and generate 15 candidate binders with RFD4-Proteina.
4. Inspect the batch, re-run it with OpenFold3 and pick one "parent".
5. Redesign a parent with ProteinMPNN, in up to three rounds of 25 variants.
6. Compare the whole history and nominate one candidate.
7. Report to your cluster and take part in the class discussion.

## The three tools

| Tool | What it does |
| --- | --- |
| **RFD4-Proteina** | Designs a binder structure and its sequence together, against a fixed target and the hotspots you choose. |
| **ProteinMPNN** | Writes new sequences for a backbone you keep. You decide which residues stay fixed. |
| **OpenFold3** | Predicts the complex from sequences alone, so it acts as an independent check. |

## Your deliverables

- The scorecard, a CSV file the notebook writes.
- One candidate card, a one-page HTML file the notebook writes.
- A three-minute report.

## Ground rules

- Write your hypothesis **before** you see the results. The notebook stamps the time.
- Every number is a computed prediction.
- A redesign can make a candidate worse. The last round does not have to be your best one, and a clear negative result also counts as a result and gives new insights.

> **Scores are not measured affinities.** ipTM, pLDDT and PAE describe how confident a model is about a structure. None of them is a binding constant, and nothing you produce today says that a design binds in the lab.
> {: .warn }

## Before you begin

1. **Open the notebook.** [Open Workshop3_GLP1R_binder_design.ipynb in Google Colab](https://colab.research.google.com/github/CPDSE-EDUX/UCPH-PhD-AI-data-driven-drug-design/blob/main/day03/workshop_content/Workshop3_GLP1R_binder_design.ipynb) or [view it on GitHub](https://github.com/CPDSE-EDUX/UCPH-PhD-AI-data-driven-drug-design/blob/main/day03/workshop_content/Workshop3_GLP1R_binder_design.ipynb). Use the default Colab **CPU** runtime and do not request a GPU, because the models run on the course server.
2. **Join your group.** Your group number (1 to 10) is given by the instructors. The token and the server address you need in cell 0.2 are on the screen.
3. **Get the mutagenesis handout.** [GLP-1 / GLP-1R alanine-scanning handout (PDF)](assets/GLP1_GLP1R_alanine_scanning_handout.pdf) summarises the literature data on GLP-1 and the receptor. You use it in cell 1.4, so keep it open.
4. **Have a Google account ready.** The notebook saves your work to Google Drive, so that a disconnected session does not lose it.

## Schedule

The break is rolling: you take it once your generation job is submitted, so the server does not get every group at the same minute.

| Time | Minutes | Step |
| --- | --- | --- |
| 13:00 to 13:15 | 15 | [Set-up](#set-up): group, token, first check |
| 13:15 to 13:45 | 30 | [Step 1](#step-1-the-6x18-interface-and-your-hotspots): 6X18 interface and hotspots |
| 13:45 to 14:10 | 25 | [Step 2](#step-2-calibrate-openfold3-on-known-peptides): calibrate OpenFold3 on references |
| 14:10 to 14:30 | 20 | [Step 3](#step-3-hypothesis-and-15-candidates): hypothesis, submit candidate generation |
| about 14:30 to 14:45 | 15 | Rolling break: peptide generation runs while you are away |
| 14:45 to 15:15 | 30 | [Step 4](#step-4-inspect-the-designs-re-run-with-openfold3-choose-parents): inspect designs, re-run with OpenFold3, choose parents |
| 15:15 to 16:15 | 60 | [Step 5](#step-5-redesign-rounds): up to three redesign rounds, about 20 minutes each |
| 16:15 to 16:35 | 20 | [Step 6](#step-6-compare-nominate-and-export): compare, nominate, prepare the report |
| 16:35 to 17:00 | 25 | Step 7: cluster reports and class discussion |

## Set-up

*13:00 to 13:15*

You need the notebook **Workshop3_GLP1R_binder_design.ipynb** open.

1. **Cell 0.1** loads the toolbox. Run it once and do not edit it. It also checks that all required libraries are there.
2. **Cell 0.2** is where you choose your group (1 to 10; nothing is selected at the start) and type the token and the server address. The latter two are on the screen.
3. **Cell 0.3** mounts your Google Drive (Colab only). Run it on its own and accept the pop-up with your Google account. If it says *credential propagation was unsuccessful*, run the cell again and allow the pop-up. If the Drive still does not mount, set `SAVE_TO` to `local` in cell 0.2. Everything works, but a disconnected session then loses your work.
4. **Cell 0.4** connects. It also prints the time your submission slot starts, your reporting cluster and your random seed (2026 plus your group number), so your group always gets the same designs from the same request.
5. Agree on roles for the first step: one person drives the notebook, one checks every number against the references, one writes the worksheet. Rotate.

Everything you do is saved in `ws3_data/group<NN>/state.json` after each step, in your Google Drive if you chose it in cell 0.2. If the notebook stops and you have to restart, run cells 0.1 to 0.4 again and carry on. The submit cells refuse to send the same job twice, so re-running them is safe.

## Step 1. The 6X18 interface and your hotspots

*13:15 to 13:45*

**Goal:** understand how GLP-1 sits on the receptor and choose 3 to 8 **hotspots**: receptor residues you want your binder to touch. The design model tries to place the binder against them.

**Choose, run, inspect, conclude**

- **Cell 1.1** loads 6X18. The notebook finds the receptor and the GLP-1 chain by itself: GLP-1 is the short chain with most contacts to a long chain. The Gs protein is left out. Check that the printed GLP-1 sequence looks right (about 30 residues starting with H-A-E-G-T-F).
- **Cell 1.2** shows the complex in 3D. Grey is the receptor, orange is GLP-1, cyan sticks are receptor residues within 4.5 Å of GLP-1. Dashed lines are potential interactions found by ProLIF (blue hydrogen bond, red ionic, purple aromatic). Rotate with the mouse and hover over a bead or a stick to see the residue and its UniProt number.
- **Cell 1.3** shows the interface as a bar chart (heavy-atom contacts per GLP-1 residue), as a table and as two heat maps. The interaction types are calculated with ProLIF, a program that finds hydrophobic contacts, hydrogen bonds, ionic interactions, cation-π and π-stacking from the geometry (hydrogens are added first because the structure file has none). If ProLIF is not installed the notebook says so and uses simple distance rules instead. The heat maps have the rows *any contact* (heavy-atom pairs within 4.5 Å), *aromatic* (π-stacking and cation-π), *H-bond* and *ionic*. The first one is seen from the GLP-1 side (columns: GLP-1 residues, letter and number), the second from the GLP-1R side (columns: receptor residues, letter and UniProt number).
- **Cell 1.4** has two parts. First interpret the interactions: which GLP-1 residues carry the most contacts, of which kind, and which receptor residues are the anchors. Then take the [mutagenesis data handout](assets/GLP1_GLP1R_alanine_scanning_handout.pdf) and use the small look-up form (receptor with the UniProt number, or GLP-1) to see what each residue in the handout does in 6X18. Four short questions follow: two about contacts and interactions, and two about the mutagenesis data (do the effects fit the contacts, and is there a residue that matters in the data but makes no contact, or the reverse).
- **Cell 1.5** is the hotspot picker. Choose a preset, then add or remove residues in the list. To select several residues in the list, hold Cmd (Mac) or Ctrl (Windows) while you click (Shift-click selects a range); this is how you build a custom set. You can also type residue numbers in the box (for example `R:120, 125-127`). The line under the picker tells you how many hotspots you have and warns when it is fewer than 3 or more than 8.
- **Cell 1.6** saves your choice together with your reason and shows the hotspots in magenta on the structure.

**The three presets** come from the 6X18 contacts:

| Preset | Residues it selects |
| --- | --- |
| *ECD groove* | Contacts of the C-terminal half of GLP-1 |
| *Pocket rim* | Contacts of the N-terminal half of GLP-1 |
| *Whole footprint* | The strongest contacts overall |

> **Think about** — a binder that covers the whole GLP-1 footprint competes with GLP-1 for the same surface. A binder on one side touches less but may be easier to design. Both are legitimate. Write down which one you chose and why; you will be asked in Step 3 and in the report.
> {: .discuss }

**Done when:** hotspots are saved (cell 1.6 prints them) and your worksheet has the rationale.

## Step 2. Calibrate OpenFold3 on known peptides

*13:45 to 14:10*

**Goal:** learn what OpenFold3 says about peptides where we know something, before you trust it on your own designs.

The notebook predicts five peptides together with the full receptor: GLP-1 (the peptide from 6X18), exendin-4, oxyntomodulin, glucagon, and a scrambled GLP-1 (the same letters in a shuffled order, fixed seed). From the literature we expect, roughly, strong, strong, moderate, weak and no binding in that order. That ranking is approximate and is not something we measured.

OpenFold3 only sees the sequences: it is not told the 6X18 pose, so recovering the pose is a real test. For exendin-4 there is also an experimental structure to compare with, [9BYO](https://www.rcsb.org/structure/9BYO). Note that the peptide in 9BYO is exendin-D3, a close variant of exendin-4.

- **Cell 2.1** runs the five predictions and prints a table with ipTM, pTM, binder pLDDT, interface PAE, ipSAE, pose RMSD, overlap with the GLP-1 site and the threshold checks. Metrics that are missing show as NaN, never as zero.
- **Cell 2.2** plots the full PAE matrix and the per-residue pLDDT for GLP-1 and for the scrambled peptide, with the colours of the AlphaFold database. PAE is the expected position error in Å: the residue on the horizontal axis (scored residue) is scored when the structure is aligned on the residue on the vertical axis (aligned residue). Receptor residues come first, the peptide last. The two off-diagonal blocks are the receptor-peptide part. Dark green means confident, white means a large expected error. Then answer a question about the PAE: for the scrambled peptide, do you also see a lower PAE (darker green) for a specific segment of the receptor? If yes, which segment, and why could this happen?
- **Cell 2.3** overlays the predicted GLP-1 on the crystal GLP-1 (orange, transparent). The prediction is superposed on the receptor first. Does it sit where GLP-1 sits in 6X18?
- **Cell 2.3b** does the same test for exendin-4 against the experimental structure 9BYO (exendin-D3, not exactly exendin-4). The prediction (coloured by confidence), the 9BYO peptide (brown sticks) and GLP-1 from 6X18 (transparent orange) are all superposed on the receptor. The first table counts the receptor residues in contact and how many are shared, the second gives the Cα distance for each aligned residue pair.
- **Cell 2.4** plots the five peptides as stars on ipTM against interface PAE, coloured by the mean binder pLDDT (colour bar), so that three quantities are visible at once. Stars that would overlap are nudged apart and the labels have a thin line to the true position. Your own designs are added to this plot in Step 4 as circles.
- **Cell 2.5** asks four questions and shows the teaching thresholds. If the scrambled peptide passes a threshold, that threshold tells you little. You may change a threshold with `S.set_thresholds(why=..., iptm=0.70)` (the example line is in the cell); you must say why.

**Questions to answer**

- Does OpenFold3 rank the five peptides as expected? Where not?
- How close is the predicted exendin-4 to the experimental structure 9BYO (exendin-D3)? Where does it differ?
- What does the scrambled control tell you about how far a high score can be trusted?
- What can these numbers not tell you about GLP-1R binding in the lab?

This is calibration, not proof that the method predicts new binders correctly.

## Step 3. Hypothesis and 15 candidates

*14:10 to 14:30*

**Goal:** state what you expect, then submit one RFD4-Proteina job that designs 15 binders against your hotspots.

RFD4-Proteina designs the binder backbone and its sequence together. You first get the designs with the metrics of the design model itself; in Step 4 you send the sequences to OpenFold3, which predicts each complex from the sequence alone as an independent check. The design runs on the server after you submit.

- **Cell 3.1** asks three questions *before* any result exists: what kind of binder you expect to work and why (length, position, hotspots), which metrics you expect to look good and which to be the weak point, and what result would make you doubt your idea. The notebook stamps the time when you save.
- **Cell 3.2** fixes the binder length to the length of GLP-1, so that all groups design binders of the same size and you can compare them directly with GLP-1. A longer binder can bury more surface but is harder to design and to predict; you will not vary this today.
- **Cell 3.3** saves the hypothesis and submits the job. It returns at once and prints `Submitted`. Any problem is printed as `NOT submitted:` with the reason.
- **Cell 3.4** shows the job status. Run it whenever you like.

> **The break is rolling.** As soon as `Submitted` appears, take your break (about 15 minutes).
> {: .tip }

## Step 4. Inspect the designs, re-run with OpenFold3, choose parents

*14:45 to 15:15*

**Goal:** look at the design model's own view first, then ask OpenFold3 for a second opinion, compare the two, and choose one or two parents for redesign.

The order is deliberate: cells 4.1 to 4.4 only have what RFD4-Proteina reports, cell 4.5 sends the sequences to OpenFold3, and cells 4.6 and 4.7 compare the two views with each other and with the five reference peptides. Do not study all 15 in depth.

- **Cell 4.1** collects the RFD4-Proteina designs. If the job is still running it waits and prints the status; when it is done it prints one line with the number of designs.
- **Cell 4.2** is the RFD4-Proteina scorecard and an exercise. These are the metrics the design model itself reports (columns starting with `rfd4_`; the server decides which ones exist) and the contacts of the designed complex (columns starting with `des_`: hotspots touched, overlap with the GLP-1 site, clashes, closest distance), plus sequence liabilities. There is no OpenFold3 number yet. Choose a column to sort by, or leave it empty to keep the server's order. Then investigate what the scores mean: a drop-down shows one metric at a time (how it varies over the 15 designs, which designs have the highest and the lowest values). Switch on only those designs in cell 4.3 and look at them in 3D. Choose three metrics and say, for each, what you think it measures, whether you want a high or a low value, and what the highest and lowest designs look like. If a metric stays unclear, ask a staff member.
- **Cell 4.3** shows all 15 binders on top of each other, superposed on the receptor (grey), with GLP-1 from 6X18 as a dark transparent cartoon. Every design has its own colour. Use the check boxes to switch each design, and the GLP-1 reference, on and off (*Show none*, then tick the ones you want), for example to look at one design alone. Hover over a bead to see which design and residue it is and its RFD4 value. You can choose which RFD4 metric appears in the label before you run the cell.
- **Cell 4.4** is about diversity and scores. The bar charts show every RFD4 metric per design (the number is the design's number in its id). The two heat maps show how different the designs are: how far apart the binders sit on the receptor (Cα RMSD in Å) and how similar the sequences are (% identical). Both are hierarchically clustered (average linkage): the dendrogram joins the most similar designs first and similar designs sit next to each other. Look for blocks. Do the designs all do the same thing, or do they find different solutions? Does a high RFD4 score go with a design that looks different from the others?
- **Cell 4.5** re-runs the 15 sequences with OpenFold3. OpenFold3 sees only the sequence and the receptor, not the design. It returns at once; collect the result in cell 4.6 after a few minutes (the status shows when it is done).
- **Cell 4.6** collects the OpenFold3 results and compares. For every design you now see the RFD4 numbers (`rfd4_`), the contacts of the design (`des_`) and the OpenFold3 numbers: ipTM, pTM, binder pLDDT, interface PAE, ipSAE, backbone RMSD (design against prediction), pose RMSD, hotspots touched, overlap with the GLP-1 site and clashes. The five reference peptides (OpenFold3 only) are at the bottom for comparison. `checks` is the number of teaching thresholds met out of those that could be evaluated, for example 4/6; a missing metric is neither a pass nor a fail. Change `SORT_BY` to sort by another column (try `iface_pae`, `binder_plddt`, `pose_rmsd`, `hotspot_hits`, `site_overlap`).
- **Cell 4.7** gives two interactive plots. Use the drop-downs to choose the metrics; the plots are redrawn after every change. On the left: does an RFD4 metric (or a contact count of the design file) predict an OpenFold3 metric (the rank correlation is in the title)? On the right: any two OpenFold3 metrics for your 15 designs (circles) and the five reference peptides (stars), coloured by the mean binder pLDDT; overlapping points are nudged apart. Is anything clearly better than the scrambled control? Anything close to GLP-1 or exendin-4? Where do the RFD4 metrics and OpenFold3 disagree?
- **Cell 4.8** is the inspector. Choose a design in the drop-down, then run the next cell: it shows its row, the full PAE matrix, the per-residue pLDDT, the sequence with flagged liabilities, and the 3D structure coloured by pLDDT with your hotspots in magenta. Look at three: the best by your main metric, one in the middle, one at the bottom.
- **Cell 4.9** looks at one binder residue (`POS`) and lists the receptor residues it touches, the interaction types, and whether GLP-1 touches the same receptor residue in 6X18. Try a few positions, especially in the middle of the interface.
- **Cell 4.10** chooses one or two parents and asks why, and whether the batch matches your Step 3 hypothesis. Run the second cell to save.

**Read the evidence in layers**

1. The design model's view against OpenFold3's: do the RFD4 metrics and the OpenFold3 metrics rank the designs the same way?
2. Confidence: ipTM, binder pLDDT, interface PAE.
3. Agreement with the design: backbone RMSD and pose RMSD.
4. The interface itself: hotspots touched, overlap with the GLP-1 site, clashes.
5. Obvious problems: a PAE block that is bright where the interface should be, a binder that floats away from the receptor, sequence liabilities.

> **If two metrics disagree, write that down.** It is a finding.
> {: .tip }

**Done when:** parents are saved and your worksheet has the reason in terms of these layers.

## Step 5. Redesign rounds

*15:15 to 16:15*

ProteinMPNN writes new sequences for a **backbone that stays fixed**. You decide which binder residues stay and which may change; the receptor is never changed. Afterwards OpenFold3 predicts each new complex from its sequence, so you see whether the new sequence is still predicted to hold the same shape and the same pose. A redesign can make a candidate worse. A clear negative result counts.

Up to three rounds, 25 variants each, about 20 minutes per round. Cells 5.1 to 5.8 are the same in every round. For rounds 2 and 3, change `ROUND` in cell 5.1, choose the new parent and run 5.1 to 5.8 again.

- **Cell 5.1** sets `ROUND` and shows a drop-down of all candidates so far (first designs and earlier variants). Choose the parent.
- **Cell 5.2** is the residue interface. Each binder residue is classed as *interface* (heavy atoms within 4.5 Å of the receptor), *core* (buried in the binder) or *surface*. The buttons make a first choice: *Fix interface*, *Fix core*, *Fix interface + core*, *Fix nothing*. Then adjust by hand: Cmd (Mac) or Ctrl (Windows) -click in the list, type positions in *Also fix* or *Make free* (for example `5-12, 40`). The coloured strip shows the sequence with fixed residues in bold and underlined. *Show in 3D* colours fixed residues orange on the parent; if it shows nothing (this can happen in Google Colab), run cell 5.2b after every change. The slider sets the sampling temperature: higher means more diverse sequences.
- **Cell 5.3** is the round hypothesis, three sentences: *We preserve these residues because … We change these positions to test … We expect to observe …*
- **Cell 5.4** (optional) lets you write your own variants of the parent, one per line, as old letter, position, new letter, for example `A12K`, `L20D`. In Colab, separate them with `;` because a form field has one line. At most 5 variants with at most 5 changes each. They are predicted by OpenFold3 together with the ProteinMPNN variants. This needs the live server.
- **Cell 5.5** submits the round and returns at once. A message starting `NOT submitted:` tells you why not.
- **Cell 5.6** collects the round and shows each variant next to its parent. `n_changed` is the number of residues that differ from the parent. The `d_` columns are changes relative to the parent: negative `d_iface_pae` and positive `d_iptm` are improvements.
- **Cell 5.7** inspects a variant: the best, one that got worse, and any manual variant. The variant is coloured by confidence and its parent has a second colour; both are superposed on the receptor. Which of the free positions changed? Is the interface kept?
- **Cell 5.8** records your decision (retain, revise or reject) and what the round showed, including when your expectation was wrong.

> **Using the time** — while a round runs, inspect structures from the previous round or fill in the worksheet. Do not leave a round unfinished: a conclusion matters more than a fourth candidate.
> {: .tip }

## Step 6. Compare, nominate and export

*16:15 to 16:35*

**Goal:** choose the one candidate with the best evidence that it would also bind in the lab, state what the evidence is and is not, and hand in your files. The best candidate is not necessarily from the last round.

- **Cell 6.1** plots the whole history: ipTM and interface PAE of every design by round, with lines joining each design to its parent. Look for what changed from round to round and what did not.
- **Cell 6.2** is the nominee drop-down (all designs from all rounds, sorted by ipTM; ipTM alone is not the answer).
- **Cell 6.3** compares the nominee with the five reference peptides on the main metrics and lists which teaching thresholds it meets, fails, or could not be evaluated.
- **Cell 6.4** asks four things: the strongest evidence, the biggest weakness or trade-off, what the computation cannot tell you, and the first experiment you would do (and what result would count against the candidate).
- **Cell 6.5** writes the hand-in into the folder `handin`: the scorecard (`scorecard_group<NN>.csv`), the candidate card (`candidate_card_group<NN>.html`, one page with metrics against the references, plots, lineage and your own words), the 6X18 contact table (`crystal_contacts_6X18_experimental_structure.csv`) and the session file. In Colab the zip is downloaded by the browser; with `SAVE_TO` set to `drive` the folder `handin` is also in your Google Drive. Keep the card open for the report.

**What goes in the scorecard.** The columns are kept separate on purpose:

- group and target;
- candidate, parent and round;
- origin (RFD4-Proteina, ProteinMPNN or manual);
- sequence and length;
- fixed positions and your hypothesis for the round;
- binder pLDDT, ipTM, pTM, interface PAE and ipSAE;
- backbone and pose RMSD;
- hotspots touched, overlap with the GLP-1 site and clashes;
- liabilities, the threshold checks and your decision.

The per-residue pLDDT and the full PAE matrices stay in the files of each design.

Only the contact table from 6X18 is based on an experimental structure; it is exported separately. Everything in the scorecard is a computed prediction.

**Done when:** the `handin` folder contains the files and you can say your nominee, one intervention and what it did, and one uncertainty in three minutes.

## Step 7. Report and discuss

*16:35 to 17:00*

Report to your cluster, using the candidate card, and take part in the class discussion. Your three-minute report covers three things:

- your nominee and the evidence for it;
- one intervention and what it did;
- one uncertainty you could not resolve.

After the workshop, read the [analysis of the hand-ins](analysis.md) to see how all groups did.

[Open the notebook in Colab](https://colab.research.google.com/github/CPDSE-EDUX/UCPH-PhD-AI-data-driven-drug-design/blob/main/day03/workshop_content/Workshop3_GLP1R_binder_design.ipynb) · [6X18 on RCSB](https://www.rcsb.org/structure/6X18) · [9BYO on RCSB](https://www.rcsb.org/structure/9BYO)
