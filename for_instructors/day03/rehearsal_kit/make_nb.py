import json, uuid, sys
SRC = open("/home/claude/nb2/ws3_helpers.py").read()
cells = []


def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "id": uuid.uuid4().hex[:8], "source": text.strip("\n").splitlines(True)})


def code(text, hidden=False, tag=None, form=False):
    meta = {}
    if hidden:
        meta["jupyter"] = {"source_hidden": True}
    if hidden or form:
        meta["cellView"] = "form"          # Google Colab: show only the title / form fields, not the code
    if tag:
        meta["tags"] = [tag]
    cells.append({"cell_type": "code", "metadata": meta, "id": uuid.uuid4().hex[:8], "execution_count": None, "outputs": [],
                  "source": text.strip("\n").splitlines(True)})


# ------------------------------------------------------------------------------------------------------------------------
md('# Workshop 3: *De novo* binder design for GLP-1R\n**Summary.** In this workshop you design a protein binder for the GLP-1 receptor, starting from the cryo-EM structure 6X18, using RFD4-Proteina (design), ProteinMPNN (sequence redesign) and OpenFold3 (independent structure prediction).\nYou test the predictions on known peptides, redesign your best candidate over up to three rounds, and nominate the candidate with the most computational evidence for a lab test.\n\n**Created for:** the PhD course *AI- and data-driven drug design* (Day 3, Lecture 7 and Workshop 3) at the University of Copenhagen, offered by the [Center for Pharmaceutical Data Science Education (CPDSE)](https://cpdse.ku.dk).\n\n**Author:** Albert J. Kooistra, Data Science for Drug Design (DSDD) research group, CPSDE, ILF, University of Copenhagen, November 2026.\n**AI assistance:** this notebook was developed with the assistance of Claude (Anthropic).')
md('## Outline\n\n**GOAL ** Four hours, one question: *which design candidate has the best evidence that it would also bind in the lab?*\n\nYou will work with the GLP-1 receptor based on the cryo-EM structure **6X18** (GLP-1 bound to the receptor and Gs). GLP-1 shows you where a binder can sit.\n\n| Step | What you will do | Cells |\n|---|---|---|\n| 0 | Set up, connect | 0.1 to 0.4 |\n| 1 | Look at the 6X18 interface, choose hotspots | 1.1 to 1.6 |\n| 2 | Calibrate OpenFold3 on known peptides, a scrambled control and the exendin structure 9BYO | 2.1 to 2.5 |\n| 3 | Write a hypothesis, submit 15 candidates (then take your break) | 3.1 to 3.4 |\n| 4 | Inspect the RFD4 designs, re-run them with OpenFold3, compare, choose one or two parents | 4.1 to 4.10 |\n| 5 | Up to three redesign rounds with ProteinMPNN, 25 variants each | 5.1 to 5.8 |\n| 6 | Compare the whole history, nominate one candidate, export | 6.1 to 6.5 |\n| 7 | Report in your cluster | 7.1 |\n\n**Google Colab/Jupyter UCloud.** This notebook runs in Google Colab or Jupyter on UCloud on the normal CPU runtime (no GPU needed; the models - OF3/RFD4-Proteina/ProteinMPNN - run on the DSDD servers).\n\n**Rules of the game.** Run the cells in order. Cells marked **CHOOSE** are where you decide something. Write your hypothesis *before* you see results: the notebook stamps the time. Every number here is a computed prediction, so keep in mind that a computed score is not a measured affinity. Often a redesign can make a candidate worse, but also clear negative results counts as a results which you can use to improve the designs.\n\n**In every 3D view:** hover over a bead/sphere (a Cα atom) or a stick to see the residue ID. Receptor residues show the residue and its UniProt number, binder residues the residue and its position. Dashed lines are potential interactions found by ProLIF (blue: H-bond, red: ionic, purple: aromatic; a rough geometric analysis of a static model, not a measured interaction). Whenever two structures are compared, they are first superposed on the receptor (the residues around the GLP-1 site), so differences you see are differences of the peptide or binder.')


md("## Step 0. Set up")
md("**Cell 0.1.** Load the toolbox. Run it once and do not edit it. (The source is hidden; click the three dots to open it if you are curious.)")
DEP = """
# dependencies for the pictures and the little interfaces
import subprocess
PIP_NAMES = {"ipywidgets": "ipywidgets", "py3Dmol": "py3Dmol", "matplotlib": "matplotlib", "pandas": "pandas", "numpy": "numpy", "scipy": "scipy", "prolif": "prolif"}
OPTIONAL = {"prolif"}      # without ProLIF the interactions are found with simple distance rules
missing = []
for mod in PIP_NAMES:
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)
if missing and in_colab():
    print("Installing", ", ".join(missing), "...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + [PIP_NAMES[x] for x in missing], timeout=300)
        missing = [x for x in missing if subprocess.call([sys.executable, "-c", "import " + x], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)]
    except Exception as e:
        print("Automatic install failed:", str(e)[:100])
if in_colab():
    try:
        from google.colab import output
        output.enable_custom_widget_manager()
    except Exception:
        pass
hard = [x for x in missing if x not in OPTIONAL]
if "prolif" in missing:
    print("Note: ProLIF (interaction analysis) is not available; simple distance rules are used instead.")
print("Toolbox loaded. All needed packages are there." if not missing else ("Toolbox loaded." if not hard else f"Missing: {hard}. Run in a new cell:  pip install " + " ".join(hard) + "  and restart the kernel."))
import matplotlib.pyplot as plt
from IPython.display import display, HTML
"""
code('#@title Cell 0.1  Load the toolbox (run once, do not edit) { display-mode: "form" }\n' + SRC + DEP, hidden=True, tag="toolbox")


md("""
**Cell 0.2.** CHOOSE your group (1 to 10, nothing is selected at the start) and fill in the token and server address from the board. In Colab this cell is a form; in Jupyter edit the values. `MODE`: `auto` uses the server if it answers and otherwise the stored results. `SAVE_TO`: `drive` saves your work in your Google Drive (run cell 0.3), `local` keeps it only in this session. `PACK_URL` is optional: a link to `ws3_pack.zip` if the board gives one (otherwise upload the zip to the Colab file browser).
""")
code("""
#@title Cell 0.2  Settings { display-mode: "form" }
GROUP    = ""                        #@param ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
TOKEN    = "paste-your-token-here"   #@param {type:"string"}
SERVER   = ""  #@param {type:"string"}
MODE     = "auto"                    #@param ["auto", "server", "stored"]
SAVE_TO  = "drive"                   #@param ["drive", "local"]
PACK_URL = ""                        #@param {type:"string"}
""", form=True)
md("""
**Cell 0.3.** Google Drive (Colab only). Run this cell on its own and accept the permission pop-up with your Google account. If it says *credential propagation was unsuccessful*, run the cell again and allow the pop-up; it usually helps to be signed in to only one Google account in the browser and to allow third-party cookies for colab.research.google.com. If the Drive still does not mount, set `SAVE_TO` to `local` in cell 0.2: everything works, but a disconnected runtime then loses your work. In Jupyter this cell does nothing.
""")
code("""
if SAVE_TO == "drive" and in_colab():
    from google.colab import drive
    drive.mount("/content/drive")
else:
    print("Nothing to mount here.")
""")
md("**Cell 0.4.** Connect. This also tells you when your submission slot starts (the slots are spread out so the GPUs are not hit all at once) and which reporting cluster you are in.")
code("""
ROOT = workspace_root(SAVE_TO)
S = Session(GROUP, TOKEN, SERVER, MODE, root=ROOT, pack_url=PACK_URL)
print(f"Group {S.group}: slot for Step 3 starts at {slot_for(GROUP)}; reporting cluster {cluster_of(GROUP)}.")
print(f"Random seed for your designs: {S.seed} (2026 + your group number). The same request from your group always gives the same designs.")
print(f"Everything you do is saved in ws3_data/group{S.group}/state.json, so a restart loses nothing.")
""")

# ------------------------------------------------------------------------------------------------------------------------
md("""
## Step 1. The 6X18 interface and your hotspots (about 30 minutes)

**Choose, run, inspect, conclude.** First you look at how GLP-1 sits on the receptor. Then you choose 3 to 8 **hotspots**: receptor residues you want the binder to touch. The design model (RFD4-Proteina) tries to place the binder against them.
""")
md("**Cell 1.1.** Load 6X18. The notebook finds the receptor and the GLP-1 chain by itself (the receptor is the chain that GLP-1 touches most). The Gs protein in the structure is left out of the design.")
code("""
ref = S.load_reference("6X18")
display(HTML(f"<b>GLP-1 (chain {ref['pep_chain']}):</b> <span style='font-family:monospace'>{ref['pep_seq']}</span><br><small>Receptor numbering in the hover labels: UniProt P43220 ({ref['uniprot_source']}).</small>"))
""")
md("**Cell 1.2.** Look at it. Grey: receptor. Orange: GLP-1. Cyan sticks: receptor residues within 4.5 Å of GLP-1. Dashed lines: potential interactions (blue H-bond, red ionic, purple aromatic). Rotate with the mouse and hover over a bead or stick to see the residue and its UniProt number.")
code("""
v = view_crystal(ref)
if v: v.show()
""")
md("""
**Cell 1.3.** Inspect the interface. The bar chart shows which GLP-1 residues carry the contacts and the table lists each residue pair with the closest distance and the interaction types. The interaction types are calculated with **ProLIF**, a program that finds hydrophobic contacts, hydrogen bonds, ionic interactions, cation-π and π-stacking from the geometry of a structure (hydrogens are added first, because the structure file has none). *H-bond* = donor and acceptor in either direction, *ionic* = anionic and cationic groups, *aromatic* = π-stacking and cation-π. If ProLIF is not installed the notebook says so and uses simple distance rules instead. The geometry is that of one static model, so these are potential interactions.

The two heat maps count, per interaction type, the interactions found (rows: any contact = heavy-atom pairs within 4.5 Å, aromatic, H-bond, ionic). The first one is seen from the GLP-1 side (columns: GLP-1 residues, letter and number), the second from the GLP-1R side (columns: receptor residues, letter and UniProt number).
""")
code("""
plot_footprint(ref); plt.show()
fig = plot_interaction_heatmaps(ref); plt.show()
print("Interactions calculated with:", ref["interaction_engine"])
display(ref["table"])
""")
md("""
**Cell 1.4.** Interpret the interactions, then compare them with experiment.

**Step 1: interpret.** Which GLP-1 residues make the most contacts, and what kind (hydrophobic, H-bond, ionic, aromatic)? Which receptor residues are the anchors?

**Step 2: the mutagenesis handout.** Take the **mutagenesis data handout** (alanine scanning of GLP-1 and of the receptor). Use the lookup below to see what a residue does in 6X18: choose whether the residue belongs to the receptor (UniProt numbering) or to GLP-1 and type its number. For every residue in the handout, ask: does it make a contact or an interaction in 6X18? Does the effect of the mutation fit that picture?
""")
code("""
#@title Look up a residue { display-mode: "form" }
WHO    = "receptor"      #@param ["receptor", "GLP-1"]
NUMBER = 1               #@param {type:"integer"}
display(residue_lookup(ref, WHO, NUMBER))
""", form=True)
code("""
q1 = Form({"where": "Which part of GLP-1 carries most of the contacts, and which receptor region does it reach?",
           "kinds": "Which interaction types do you see, and which receptor residues look like the most important anchors?",
           "mut_fit": "Which mutations in the handout have a large effect and which have none? Do these fit the contacts and interactions you see in 6X18? Name two residues where they fit.",
           "mut_gap": "Is there a residue that matters in the mutagenesis data but makes no contact in 6X18 (or the reverse)? Suggest one reason (for example an indirect effect, folding or expression, another receptor state, the assay)."}, rows=3)
""")
md("""
**Cell 1.5.** CHOOSE hotspots. Start from a preset, then add or remove residues in the list. **To select several residues in the list, hold Cmd (Mac) or Ctrl (Windows) while you click** (Shift-click selects a range); this is how you build a custom set. You can also type residue numbers (for example `R:120, 125-127`). The three presets are built from the 6X18 contacts. Choose at least 3 and at most 8.

*Think about:* a binder that covers the whole GLP-1 footprint competes with GLP-1. A binder on one side only may be easier to design but touches less surface. Both are legitimate hypotheses.
""")
code("""
picker = HotspotPicker(ref)
why_hot = Form({"why": "Why these hotspots? (one or two sentences)"}, rows=2)
""")
md("**Cell 1.6.** Save your choice together with your reason and see it on the structure (magenta).")
code("""
if why_hot.check(15):
    print("Please write a reason first (at least one sentence).")
else:
    hs = S.set_hotspots(picker.value, why_hot.values()["why"])
    print("Saved hotspots:", ", ".join(hs))
    v = view_crystal(ref, hs)
    if v: v.show()
""")

# ------------------------------------------------------------------------------------------------------------------------
md("""
## Step 2. Calibrate OpenFold3 (about 25 minutes)

Before you trust OpenFold3 on your own designs, see what it says about peptides where we know something. The five test peptides are GLP-1 itself, exendin-4, oxyntomodulin, glucagon, and a **scrambled GLP-1** (same letters, shuffled with a fixed seed). From the literature we expect strong, strong, moderate, weak, and no binding in that order. That ranking is approximate and it is *not* something we measured.

OpenFold3 only sees the sequence. It does not get the 6X18 pose, so whether it recovers the pose is a real test. For exendin-4 there is also an experimental structure to compare with, **9BYO**. **Note: the peptide in 9BYO is exendin-D3**, a close variant of exendin-4 (cell 2.3b prints the differences).
""")
md("**Cell 2.1.** Run OpenFold3 on the five peptides together with the full receptor.")
code("""
ref_df = S.run_references()
cols = [c for c in ["id", "label", "expected", "iptm", "ptm", "binder_plddt", "iface_pae", "ipsae", "pose_rmsd", "site_overlap", "site_cover", "checks"] if c in ref_df]
display(ref_df[cols])
""")
md("""
**Cell 2.2.** Look at the full PAE matrices, in the colours of the AlphaFold database. PAE is the expected position error in Å: the residue on the horizontal axis (scored residue) is scored when the structure is aligned on the residue on the vertical axis (aligned residue). The top right and bottom left blocks are the receptor-peptide part. Dark green means confident, white means a large expected error.
""")
code("""
for rid in ["ref_glp1", "ctrl_scrambled"]:
    display(S.plots(rid)); plt.close("all")
""")
md("**Interpret the PAE.** Compare the receptor-peptide blocks of GLP-1 and of the scrambled peptide, then answer.")
code("""
q22 = Form({"pae": "For the scrambled peptide, do you also see a lower PAE (darker green) for one specific segment of the receptor? If yes: which segment (residue range), and argue why this could happen."}, rows=4)
""")
md("**Cell 2.3.** Does the predicted GLP-1 sit where GLP-1 sits in 6X18? Orange transparent cartoon is the crystal GLP-1, the colored one is the OpenFold3 prediction (blue = confident). The prediction is superposed on the receptor first.")
code("""
v = S.view("ref_glp1", with_crystal=True)
if v: v.show()
""")
md("""
**Cell 2.3b.** The same test for exendin-4, now against an experimental structure: **9BYO** (GLP-1R with exendin-D3). The prediction (colored by confidence), the 9BYO peptide (brown sticks) and GLP-1 from 6X18 (transparent orange) are superposed on the receptor. The table counts receptor residues in contact and how many are shared. The second table gives the Cα distance for each aligned residue pair.
""")
code("""
S.load_extra_reference("9BYO")
summ, pairs, note = S.compare_experimental("ref_exendin4", "9BYO")
display(summ)
print(note)
display(pairs.T)
v = S.view_experimental("ref_exendin4", "9BYO", label="exendin-D3")
if v: v.show()
""")
md("""
**Cell 2.4.** Compare all five on two metrics. Each star is a reference peptide; its colour is the **mean binder pLDDT** (colour bar), so you see three quantities at once. Stars that would overlap are nudged apart a little and the labels have a thin line to the true position. Your designs will be added to this plot in Step 4 (circles).
""")
code("""
plot_overview(None, ref_df); plt.show()
""")
md("""
**Cell 2.5.** Conclude, and decide if the teaching thresholds fit what you saw. The defaults are a starting point (ipTM at least 0.60, binder pLDDT at least 80, interface PAE at most 10 Å, backbone RMSD at most 2 Å, pose RMSD at most 3 Å, at least half of the hotspots touched). If the scrambled control passes a threshold, that threshold does not tell you much. You may change a threshold, but you must say why.
""")
code("""
q2 = Form({"ranking": "Does OpenFold3 rank the five peptides in the order you expected? Where not?",
           "exp": "How close is the predicted exendin-4 to the experimental structure 9BYO (exendin-D3)? Where does it differ?",
           "scrambled": "What does the scrambled control tell you about how far a high score can be trusted?",
           "limits": "What can these numbers not tell you about GLP-1R binding in the lab?"})
display(pd.DataFrame([THRESHOLDS], index=["default"]).T.join(pd.Series(S.thr, name="your group")))
""")
code("""
# OPTIONAL: change a threshold (remove the # and run). Example: ipTM must be at least 0.7
# S.set_thresholds(why="the scrambled peptide reached 0.5, so I want a margin", iptm=0.70)
""")

# ------------------------------------------------------------------------------------------------------------------------
md("""
## Step 3. Hypothesis and 15 candidates (about 20 minutes, then the break)

RFD4-Proteina designs the binder backbone and its sequence together, against the fixed receptor and your hotspots. You get the designs and the metrics of the design model first; in Step 4 you re-run the sequences with OpenFold3 as an independent check. The design runs on the server after you submit.

**Your slot is on the board.** If you submit well before your slot, wait. The break is rolling: **once your job is submitted, take your break.** The notebook does not need to stay open.
""")
md("**Cell 3.1.** Write your hypothesis *before* the results exist. The time is stamped.")
code("""
hyp_form = Form({"idea": "What kind of binder do you expect to work, and why? (where it sits, which hotspots)",
                 "expect": "Which metrics do you expect to look good, and which do you expect to be the weak point?",
                 "doubt": "What result would make you doubt your idea?"})
""")
md("""
**Cell 3.2.** The binder length is fixed to the length of GLP-1, so that all groups design binders of the same size and you can compare them with GLP-1 directly. (Longer binders can bury more surface but are harder to design and to predict; you will not vary this today.)
""")
code("""
LENGTH = len(ref["pep_seq"])
print("Binder length:", LENGTH, "residues (the length of GLP-1 in 6X18).")
""")
md("**Cell 3.3.** Save the hypothesis and submit. This returns at once.")
code("""
if hyp_form.check(20):
    print("Please answer all three hypothesis questions first (a sentence each).")
elif len(S.hotspots) < 3:
    print("Choose and save hotspots first (cell 1.6).")
else:
    S.note("gen_hypothesis", text=hyp_form.values()["idea"], expect=hyp_form.values()["expect"], doubt=hyp_form.values()["doubt"],
           length=LENGTH, hotspots=S.hotspots)
    try:
        S.submit("gen", "generate", dict(n_designs=N_DESIGNS, binder_length=LENGTH, hotspots=S.hotspots))
        print("Submitted. You can take your break now. Be back by 14:50 and continue with Step 4.")
    except RuntimeError as e:
        print("NOT submitted:", e)
""")
md("**Cell 3.4.** Check the status whenever you like (and when you are back).")
code("""
S.status()
""")

# ------------------------------------------------------------------------------------------------------------------------
md("""
## Step 4. Inspect the designs, re-run with OpenFold3, choose parents (about 30 minutes)

You have 15 candidates. The order is deliberate. **First** you only have what the design model reports (cells 4.1 to 4.4): its own metrics, the contacts of the design, and a look at all binders on top of each other. **Then** you send the sequences to OpenFold3 (cell 4.5), and **then** you compare the two views with each other and with the reference peptides (cells 4.6 and 4.7). Do not study all 15 in depth: look at a few from different ranks, including one you would not pick.
""")
md("**Cell 4.1.** Collect the RFD4-Proteina designs. If the job is still running this waits and shows the status.")
code("""
recs = S.collect("gen")
print(f"Collected {len(recs)} designs: {recs[0]['id']} ... {recs[-1]['id']}.")
""")
md("""
**Cell 4.2.** The RFD4-Proteina scorecard. These are the metrics the design model itself reports (columns starting with `rfd4_`; the server decides which ones exist) and the contacts of the designed complex (columns starting with `des_`: hotspots touched, overlap with the GLP-1 site, clashes, closest distance), plus sequence liabilities. There is no OpenFold3 number yet. Choose a column to sort by; leave it empty to keep the server's order.

**The 3D visualization of the designs is in Cell 4.3** (the next cell after the scorecard and the exercise below): tick the designs you want to look at there.

**Exercise: what do these scores mean?** Do not trust a number you cannot explain. Use the drop-down below to look at one metric at a time (how it varies over the 15 designs, which designs have the highest and the lowest values). Then switch on only those designs in **Cell 4.3** (the 3D viewer) and look at them: do the highest and the lowest designs look different? Choose three metrics and answer the questions after the drop-down. If a metric stays unclear after that, ask a staff member.
""")
code("""
SORT_RFD4  = ""       #@param {type:"string"}
HIGH_FIRST = True     #@param {type:"boolean"}
df = S.rfd4_scores()
tab = rfd4_table(df)
print("Columns:", ", ".join(tab.columns))
display(tab.sort_values(SORT_RFD4, ascending=not HIGH_FIRST) if SORT_RFD4 in tab else tab)
guide = MetricGuide(df)
""")
code("""
q42 = Form({"m1": "Metric 1 (name it): what do you think it measures, would you want a high or a low value, and what do the highest and lowest designs look like in 3D?",
            "m2": "Metric 2 (name it): the same questions.",
            "m3": "Metric 3 (name it): the same questions.",
            "unclear": "Which metric could you not interpret, and what would you need to know to do it?"}, rows=3)
""")
md("""
**Cell 4.3.** All 15 binders on top of each other, superposed on the receptor (grey), with GLP-1 from 6X18 in dark transparent cartoon. Every design has its own color. **Use the check boxes to switch each design and the GLP-1 reference on and off**, for example to look at one design alone, or at the highest and lowest design of a metric from cell 4.2 (*Show none*, then tick the ones you want, or click *only* next to a design). Hover over a bead to see which design and residue it is and its RFD4 value. Choose which RFD4 metric appears in the labels (empty: the first one) before you run the cell.
""")
code("""
RFD4_METRIC = ""      #@param {type:"string"}
overlay = S.overlay_widget(RFD4_METRIC or None)
""")
md("**Cell 4.4.** Diversity and scores. The bar charts show every RFD4 metric per design (the number is the design's number in the id). The two heat maps show how different the designs are: left, how far apart the binders sit on the receptor (Cα RMSD in Å), right, how similar the sequences are (% identical). Both are **hierarchically clustered** (average linkage): the dendrogram on the left of each map joins the most similar designs first, and the designs are ordered so that similar ones sit next to each other. Look for blocks.")
code("""
fig = plot_rfd4_overview(df); plt.show()
fig = S.plot_diversity(); plt.show()
q4 = Form({"div": "Do the designs sit in one place or several? Which designs are clearly different from the others, and do they cover your hotspots?",
           "rfd4": "Which designs would you pick from the RFD4 metrics alone, and which RFD4 metric do you trust most (and why)?"})
""")
md("**Cell 4.5.** Re-run the 15 sequences with OpenFold3. OpenFold3 sees only the sequence and the receptor, not the design. This returns at once; collect in 4.6 after a few minutes (the status shows when it is done).")
code("""
try:
    S.rerun_openfold3()
    print("Submitted. Continue with 4.6 in a few minutes.")
except RuntimeError as e:
    print("NOT submitted:", e)
""")
md("""
**Cell 4.6.** Collect the OpenFold3 results and compare. For every design you now see the RFD4 numbers (`rfd4_*`), the contacts of the design (`des_*`) and the OpenFold3 numbers: ipTM, pTM, binder pLDDT, interface PAE, ipSAE, backbone RMSD (design against prediction), pose RMSD, hotspots touched, overlap with the GLP-1 site, clashes. The reference peptides (OpenFold3 only) are at the bottom for comparison. `checks` counts how many of the teaching thresholds are met out of those that could be evaluated; a metric that is missing is not counted as a pass or as a fail. Change `SORT_BY` to sort differently.
""")
code("""
S.collect("of3")
SORT_BY = "iptm"      #@param ["iptm", "iface_pae", "binder_plddt", "pose_rmsd", "backbone_rmsd", "hotspot_hits", "site_overlap"]
df = S.score()
ref_df = S.reference_scores()
asc = SORT_BY in ("iface_pae", "backbone_rmsd", "pose_rmsd", "n_clash")
order = df.sort_values(SORT_BY, ascending=asc, na_position="last")
display(compare_table(order, ref_df))
""")
md("""
**Cell 4.7.** Two interactive plots. **Use the drop-downs to choose the metrics; the plots are redrawn after every change.** Left: does an RFD4 metric (or a contact count of the design file) predict what OpenFold3 says? The rank correlation is in the title. Right: any two OpenFold3 metrics for your 15 designs (circles) and the five reference peptides (stars); the colour is the mean binder pLDDT and points that overlap are nudged apart. Is anything better than the scrambled control? Anything near GLP-1 or exendin-4? Where do the RFD4 metrics and OpenFold3 disagree?
""")
code("""
explorer = MetricExplorer(df, ref_df)
q47 = Form({"agree": "Do the RFD4 metrics and the OpenFold3 metrics agree? Name one design where they do not, and what that could mean.",
            "refs": "How do your best designs compare with the reference peptides, in particular GLP-1 and the scrambled control?"})
""")
md("**Cell 4.8.** CHOOSE a candidate to inspect. Look at three: the best by your main metric, one in the middle, one at the bottom.")
code("""
insp = Chooser(df, sort=SORT_BY)
""")
code("""
cid = insp.value
display(short_table(df[df["id"] == cid]))
display(S.plots(cid)); plt.close("all")
print("Sequence:", S.record(cid)["sequence"])
print("Liabilities:", "; ".join(liabilities(S.record(cid)["sequence"])) or "none flagged")
# colored by pLDDT (blue = confident); purple = the design of RFD4-Proteina; magenta sticks = your hotspots; both on the receptor
v = S.view(cid, with_design=True)
if v: v.show()
""")
md("""
**Cell 4.9.** Look at one binder residue and what it touches. The last column tells you whether GLP-1 touches the same receptor residue in 6X18. Try a few positions, especially in the middle of the interface.
""")
code("""
# binder position, 1-based
POS = 10     #@param {type:"integer"}
display(residue_contacts(Path(S.record(cid)["files"]["model"]).read_text(), POS, ref))
""")
md("**Cell 4.10.** CHOOSE one or two parents for redesign, and explain why. Use confidence, agreement with the design, contacts and obvious problems.")
code("""
parents = Chooser(df, multiple=True, sort=SORT_BY, description="Parents")
why_par = Form({"why": "Why these parents? What do the metrics say, what do they not say?",
                "vs_hyp": "Does the batch match your hypothesis from Step 3?"})
""")
code("""
if len(parents.value) not in (1, 2):
    print("Choose one or two parents.")
elif why_par.check(15):
    print("Please answer both questions.")
else:
    S.note("parents", ids=parents.value, **why_par.values())
    print("Saved parents:", parents.value)
""")

# ------------------------------------------------------------------------------------------------------------------------
md("""
## Step 5. Redesign rounds (about 60 minutes, three rounds at most)

ProteinMPNN writes new sequences for a **backbone that stays fixed**. You decide which residues stay and which may change. The receptor is not changed. After the sequences are written, OpenFold3 predicts each new complex, so you see whether the new sequence is still predicted to hold the same shape and pose.

**Each round has the same cells (5.1 to 5.8).** For round 2 and 3, change `ROUND` in cell 5.1, choose the new parent, and run 5.1 to 5.8 again. **Keep each round to about 20 minutes.**

The prompt for each round: *We preserve these residues because ___. We change these positions to test ___. We expect to observe ___.*
""")
md("**Cell 5.1.** CHOOSE the round number and the parent.")
code("""
ROUND = 1       #@param [1, 2, 3] {type:"raw"}
df = S.score()
pick_parent = Chooser(df, sort=SORT_BY, description="Parent")
""")
md("""
**Cell 5.2.** CHOOSE which binder residues stay fixed. Each residue is classed as **interface** (heavy atoms within 4.5 Å of the receptor), **core** (buried inside the binder) or **surface**. Use the buttons for a first selection, then adjust: the list (Ctrl/Cmd-click), the *Also fix* box, or the *Make free* box (for example `5-12, 40`). The sequence strip shows what is fixed (bold with underline). *Show in 3D* colors fixed residues orange.

More free positions mean more diversity but also a larger chance to lose the interface. A higher temperature gives more diverse sequences.
""")
code("""
PARENT = pick_parent.value
par_rec = S.record(PARENT)
cls = residue_classes(Path(par_rec["files"]["design"]).read_text())

def show_fixed(fixed):
    v = S.view(PARENT, color="fixed", fixed=fixed)
    if v: v.show()

fix = FixPicker(cls, par_rec["sequence"], view_cb=show_fixed)
""")
md("**Cell 5.2b.** 3D view of your current choice. The *Show in 3D* button does the same; if it shows nothing (this can happen in Google Colab), run this cell after every change. Fixed residues are orange.")
code("""
show_fixed(fix.fixed)
""")
md("**Cell 5.3.** Write the round hypothesis before you submit.")
code("""
rh = Form({"preserve": "We preserve these residues because ...",
           "change": "We change these positions to test ...",
           "expect": "We expect to observe ..."})
""")
md("""
**Cell 5.4.** OPTIONAL: write your own variants of the parent by hand as *old letter, position, new letter* (for example `A12K, L20D` is one variant with two changes). Separate variants with a semicolon: `A12K, L20D; E15Q`. At most 5 variants with at most 5 changes each. They are evaluated by OpenFold3 together with the 25 ProteinMPNN variants. (This needs the live server.)
""")
code("""
# example: A12K, L20D; E15Q
manual_text = ""      #@param {type:"string"}
""")
md("**Cell 5.5.** Submit the round. This returns at once; collect in 5.6 after a few minutes.")
code("""
if rh.check(15):
    print("Please finish the three sentences first.")
elif len(fix.fixed) >= len(par_rec["sequence"]) - 2:
    print("Almost everything is fixed. Free at least 3 positions.")
elif ROUND > MAX_ROUNDS:
    print("Three rounds at most.")
else:
    v = rh.values()
    hyp = f"Preserve: {v['preserve']} | Change: {v['change']} | Expect: {v['expect']}"
    try:
        S.submit(f"r{ROUND}", "redesign", dict(parent_id=PARENT, fixed_positions=fix.fixed, temperature=fix.temperature,
                                               n_sequences=N_VARIANTS, round=ROUND))
    except RuntimeError as e:
        print("NOT submitted:", e)
    else:
        S.record_round(ROUND, PARENT, fix.fixed, fix.temperature, hyp)
        if manual_text.strip():
            try:
                S.submit_manual(ROUND, PARENT, [x for x in manual_text.split(";") if x.strip()])
            except (ValueError, RuntimeError) as e:
                print("Your manual variants were NOT submitted:", e)
        print(f"Round {ROUND} submitted. Look at your last round's structures while you wait.")
""")
md("**Cell 5.6.** Collect the round and compare each variant with its parent. `n_changed` counts residues that differ from the parent; `d_` columns are changes relative to the parent (negative `d_iface_pae` is an improvement, positive `d_iptm` is an improvement).")
code("""
S.collect(f"r{ROUND}")
S.collect_manual(ROUND)
df = S.score()
this = df[(df["round"] == ROUND) & (df["parent"] == PARENT)]
display(pd.concat([short_table(this).set_index("id"), delta_table(df[df["id"].isin(list(this["id"]) + [PARENT])], PARENT).set_index("id")
                   .drop(columns="sequence")], axis=1).sort_values(SORT_BY, ascending=(SORT_BY in ("iface_pae", "pose_rmsd", "backbone_rmsd"))))
""")
md("**Cell 5.7.** Inspect: the best variant, one that got worse, and any manual variant. The variant is colored by confidence and its parent has a second color; both are superposed on the receptor. Is the interface kept? Which of the free positions changed?")
code("""
insp2 = Chooser(this, sort=SORT_BY, description="Variant")
""")
code("""
vid = insp2.value
display(short_table(df[df["id"] == vid]))
n_ch, pos = sequence_changes(S.record(PARENT)["sequence"], S.record(vid)["sequence"])
print(f"{n_ch} positions differ from the parent: {pos}")
display(S.plots(vid)); plt.close("all")
# the variant (colored by pLDDT) and its parent (second color), both superposed on the receptor
v = S.view(vid, compare=[PARENT])
if v: v.show()
""")
md("**Cell 5.8.** Decide and conclude. Retain the change, revise it, or reject it? Say what you learned, including when it did not work.")
code("""
dec = Form({"decision": "Retain, revise or reject this intervention? (one word, then why)", "learned": "What did this round show? Was your expectation right?"})
""")
code("""
if dec.check(8):
    print("Please answer both questions.")
else:
    d = dec.values()
    S.update_round(ROUND, decision=d["decision"], conclusion=d["learned"])
    print(f"Round {ROUND} saved. For the next round: set ROUND = {ROUND + 1} in cell 5.1 and run 5.1 to 5.8 again." if ROUND < MAX_ROUNDS else "That was the last round. Go to Step 6.")
""")

# ------------------------------------------------------------------------------------------------------------------------
md("""
## Step 6. Compare everything and nominate one candidate (about 20 minutes)

Look at the whole history: the references, the 15 first designs, and every redesign. The best candidate is not necessarily from the last round.
""")
md("**Cell 6.1.** The history. Lines join each design to its parent.")
code("""
df = S.score()
ref_df = S.reference_scores()
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
plot_lineage(df, ax[0], "iptm"); plot_lineage(df, ax[1], "iface_pae")
plt.tight_layout(); plt.show()
""")
md("**Cell 6.2.** CHOOSE the nominee. The list is sorted by ipTM, but ipTM alone is not the answer.")
code("""
nominee = Chooser(df, sort="iptm", description="Nominee")
""")
md("**Cell 6.3.** The nominee against the references and against the thresholds. A gray cell is a metric that is missing, not a failure.")
code("""
nid = nominee.value
cols = ["iptm", "ptm", "binder_plddt", "iface_pae", "ipsae", "backbone_rmsd", "pose_rmsd", "hotspot_frac", "site_overlap", "n_clash"]
cmp_ = pd.concat([df[df["id"] == nid][["id"] + cols], ref_df[["id"] + cols]]).set_index("id")
display(cmp_)
p, t, detail = evidence_checks(df[df["id"] == nid].iloc[0].to_dict(), S.thr)
print(f"{nid} meets {p} of {t} evaluable thresholds:", {k: ('pass' if v else 'fail' if v is not None else 'missing') for k, v in detail.items()})
""")
md("**Cell 6.4.** Four honest sentences: what is the best evidence, what is the biggest weakness, what stays uncertain, and which experiment would you do first?")
code("""
fin = Form({"evidence": "Strongest evidence for this candidate:",
            "weakness": "Biggest weakness or trade-off:",
            "uncertainty": "What the computation cannot tell you:",
            "next_experiment": "First experiment you would do (and what result would count against it):"})
""")
md("**Cell 6.5.** Export your hand-in: the scorecard (CSV), the candidate card (one HTML page) and your session file. In Colab the zip is downloaded by the browser; with `SAVE_TO` set to `drive` the folder `handin` is also in your Google Drive.")
code("""
if fin.check(15):
    print("Please fill all four fields.")
else:
    S.note("final", nominee=nid, **fin.values())
    files, folder = S.export(nid)
    print("Written to", folder)
    for f in files: print("  ", f)
    offer_download(folder, f"handin_group{S.group}")
    display(HTML(open(folder / f"candidate_card_group{S.group}.html").read()))
""")

# ------------------------------------------------------------------------------------------------------------------------
md("""
## Step 7. Report and discuss (25 minutes)

**Cell 7.1.** Find your cluster and prepare your three minutes. Every group says: (1) *your chosen candidate*, (2) *one intervention and what it did*, (3) *one uncertainty*. Then your cluster agrees on **one two-minute takeaway** for the class.
""")
code("""
c = cluster_of(S.group)
print(f"Group {S.group} reports in cluster {c} together with groups {[g for g in CLUSTERS[c] if g != int(S.group)]}.")
fn = S.get_note("final")
print("\\nYour nominee:", fn.get("nominee"))
print("Strongest evidence:", fn.get("evidence"))
print("Open uncertainty:", fn.get("uncertainty"))
""")
md("""
**Questions for the cluster discussion.** What did the scrambled control teach you about the metrics? Which intervention helped most and which one failed? Where did two metrics disagree? What would you have to measure in the lab, and what result would make you drop the candidate?
""")

# ------------------------------------------------------------------------------------------------------------------------
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                   "language_info": {"name": "python"},
                                   "colab": {"provenance": [], "name": "Workshop3_GLP1R_binder_design.ipynb"}}, "nbformat": 4, "nbformat_minor": 5}
out = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/nb2/Workshop3_GLP1R_binder_design.ipynb"
json.dump(nb, open(out, "w"), indent=1)
print("wrote", out, len(cells), "cells")
