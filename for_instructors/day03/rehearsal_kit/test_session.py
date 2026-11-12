import sys, os, tempfile, json, time
sys.path.insert(0, "/home/claude/nb2")
os.environ["WS3_IGNORE_DEADLINE"] = "1"
import numpy as np
import types
class _View:
    calls = []
    def __init__(self, **k): _View.calls.append(("view", k))
    def __getattr__(self, n):
        def f(*a, **k): _View.calls.append((n, a, k)); return None
        return f
pm = types.ModuleType("py3Dmol"); pm.view = _View; sys.modules["py3Dmol"] = pm
os.environ["MPLBACKEND"] = "Agg"
import ws3_helpers as H, synth as S, mock_server as M

text, rs = S.fake_6x18(uniprot_offset=7)
mock = M.Mock(text, rs, delay=0.3)
srv, url = M.serve(mock)
work = tempfile.mkdtemp(); os.chdir(work)
os.makedirs("ws3_data"); open("ws3_data/6X18.pdb", "w").write(text); open("ws3_data/9BYO.pdb", "w").write(S.fake_9byo(rs))

for bad in ("", "0", "11", "x"):
    try: H.Session(bad, "tok-1", url, "auto", log=print); raise SystemExit("should fail for group " + repr(bad))
    except ValueError as e: msg = str(e)
print("group check ->", msg)
s = H.Session("3", "tok-1", url, "auto", log=print)
assert s.mode_used == "server"
ref = s.load_reference()
# UniProt numbering from DBREF, in labels and heat maps
assert ref["uniprot"][ref["rec_nums"][0]] == ref["rec_nums"][0] + 7, ref["uniprot_source"]
assert "DBREF" in ref["uniprot_source"]
assert "uniprot_number" in ref["table"] and (ref["table"]["uniprot_number"] - ref["table"]["receptor_residue"].str[2:].astype(int) == 7).all()
assert ref["heat_pep"].shape == (4, 30) and ref["heat_rec"].shape[0] == 4 and ref["heat_rec"].shape[1] == len(ref["footprint"])
assert ref["heat_pep"][0].sum() == ref["heat_rec"][0].sum() == ref["table"]["atom_pairs"].sum()
import matplotlib; matplotlib.use("Agg")
fig = H.plot_interaction_heatmaps(ref); assert len(fig.axes) >= 2
labs = [t.get_text() for t in fig.axes[1].get_xticklabels()]
assert labs[0].endswith(str(sorted(ref["footprint"])[0] + 7)), labs[:3]
assert H.view_crystal(ref) is not None
hs = s.set_hotspots(ref["presets"]["Whole footprint (strongest contacts overall)"], "centre of the groove")
rdf = s.run_references()
print(rdf[["id", "label", "iptm", "binder_plddt", "iface_pae", "site_overlap", "checks"]] if "label" in rdf else rdf[["id", "iptm"]])
s.note("gen_hypothesis", text="A 60-residue helical hairpin on R:104-122 should reach ipTM > 0.6")
L = len(ref["pep_seq"])
assert L == 30 and H.N_DESIGNS == 15
s.submit("gen", "generate", dict(n_designs=H.N_DESIGNS, binder_length=L, hotspots=hs))
s.submit("gen", "generate", dict(n_designs=H.N_DESIGNS, binder_length=L, hotspots=hs))   # no double send
print(s.status())
recs = s.collect("gen")
# first only the RFD4-Proteina output: design files and the metrics of the design server, no OpenFold3 yet
assert len(recs) == 15 and all("design" in r["files"] and "model" not in r["files"] and r["metrics"] for r in recs)
d0 = s.rfd4_scores()
rt = H.rfd4_table(d0)
print(rt.head(3).to_string())
assert len(d0) == 15 and "iptm" not in d0 and any(c.startswith("rfd4all_") for c in d0) and len(H.rfd4_details(d0, d0.iloc[0]["id"])) >= 12 and len(H.rfd4_columns(d0)) == 11 and "des_hotspot_hits" in d0 and d0["note"].eq("OpenFold3 not run yet").all()
assert d0["des_n_clash"].notna().all() and set(rt.columns) >= {"id", "rfd4_clash_frac", "des_hotspot_hits"}
fig = H.plot_rfd4_overview(d0); assert len(fig.axes) >= 4
v, legend = s.overlay_designs()
assert v is not None and legend.count("<tr>") == 15 + 1 + 1 and "rfd4_" not in legend and "GLP-1 (6X18)" in legend
fig = s.plot_diversity(); assert len(fig.axes) >= 2
# the overlay is on the 6X18 receptor: a design moved elsewhere comes back
d1 = s.record(recs[0]["id"])["files"]["design"]
R = np.array([[0.8, -0.6, 0], [0.6, 0.8, 0], [0, 0, 1.0]])
moved = H.atoms_to_pdb(H.parse_pdb(open(d1).read()), R, np.array([5.0, -3.0, 9.0]))
back, fit, n = H.superpose_text(moved, ref)
assert fit < 0.01 and n >= 6, (fit, n)
a0 = H.get_chain(H.parse_pdb(open(d1).read()), "B"); a1 = H.get_chain(H.parse_pdb(back), "B")
assert H.rmsd(H.ca_coords(a0), H.ca_coords(a1)) < 0.05
# then the OpenFold3 re-run of the same sequences
s.rerun_openfold3()
s.rerun_openfold3()                                   # no double send
s.collect("of3")
assert len(s.state["records"]) == 5 + 15
df = s.score()
print(df[["id", "origin", "iptm", "binder_plddt", "iface_pae", "pose_rmsd", "hotspot_hits", "des_hotspot_hits", "checks"]].sort_values("iptm", ascending=False).head(5))
assert len(df) == 15 and df["iptm"].notna().all() and len(H.rfd4_columns(df)) == 11 and df["des_site_cover"].notna().all()
fig = H.plot_rfd4_vs_of3(df); assert len(fig.axes) == 2 and "rank correlation" in fig.axes[0].get_title()
fig = H.plot_rfd4_vs_of3(df, "rfd4_hotspot_obedience")
rdf = s.reference_scores(); plt = H._plt(); ax = H.plot_overview(df, rdf)
for view in (s.view(df.iloc[0]["id"], with_crystal=True, with_design=True), s.view(df.iloc[0]["id"], compare=[df.iloc[1]["id"]])):
    assert view is not None
# 9BYO: exendin-D3 for comparison with the predicted exendin-4
r2 = s.load_extra_reference("9BYO")
summ, rows, extra = s.compare_experimental("ref_exendin4")
print(summ.to_string()); print(extra)
assert len(summ) == 3 and "position 3" in extra and len(rows) == 39 and summ["peptide_CA_rmsd_to_exp_A"].iloc[0] == summ["peptide_CA_rmsd_to_exp_A"].iloc[0]
assert summ["receptor_residues_in_contact"].iloc[1] > 3 and s.view_experimental("ref_exendin4") is not None
# classes + redesign round 1
parent = df.sort_values("iptm", ascending=False).iloc[0]["id"]
r = s.record(parent)
cls = H.residue_classes(open(r["files"]["design"]).read())
fixed = [c["pos"] for c in cls if c["cls"] == "interface"]
s.state["rounds"].append(dict(round=1, parent=parent, fixed=fixed, temperature=0.2, hypothesis="keep the interface, change the core"))
s.submit("r1", "redesign", dict(parent_id=parent, fixed_positions=fixed, temperature=0.2, n_sequences=25, round=1))
rr = s.collect("r1")
df2 = s.score()
assert len(df2) == 40
d = H.delta_table(df2[df2["round"] == 1], parent) if False else H.delta_table(df2, parent)
print(d.head(4))
s.state["rounds"][0].update(decision="keep", conclusion="ipTM unchanged")
nom = df2.sort_values("iptm", ascending=False).iloc[0]["id"]
s.note("final", evidence="highest ipTM and interface PAE below threshold", weakness="n/a", uncertainty="no affinity", next_experiment="BLI")
files, folder = s.export(nom)
print(files, folder)
assert any(f.endswith(".html") for f in files) and any(f.startswith("scorecard") for f in files)
card = open(os.path.join(folder, f"candidate_card_group03.html")).read()
assert nom in card and "experimental" not in card.split("Metrics")[0].lower().replace("not measurements", "")
csv = open(os.path.join(folder, "scorecard_group03.csv")).read().splitlines()
print(len(csv), csv[0][:200])
# residue contacts
print(H.residue_contacts(open(s.record(nom)["files"]["model"]).read(), 10, ref).head(3))
# seed = 2026 + group number (reference peptides keep the base seed)
assert s.seed == H.SEED + 3 and s.state["jobs"]["gen"]["payload"]["seed"] == H.SEED + 3, s.state["jobs"]["gen"]["payload"]["seed"]
assert s.state["jobs"].get("refs", {"payload": {"seed": H.SEED}})["payload"]["seed"] == H.SEED
assert H.Session("10", "t", url, "auto", log=lambda *a: None).seed == H.SEED + 10
# restart: state restored, nothing resubmitted
s2 = H.Session("3", "tok-1", url, "auto", log=lambda *a: None)
assert len(s2.records()) == len(s.records()) and s2.hotspots == hs and s2.state["jobs"]["gen"]["collected"]
# auto fallback to stored pack when server dead
pack = os.path.join("ws3_data", "pack")
c = H.ApiClient(url, "tok-1", poll=0.1, log=lambda *a: None)
gp = dict(target_id=H.TARGET_ID, seed=H.SEED, n_designs=15, binder_length=L, hotspots=hs, group="03")
res = c.run("generate", gp); H.pack_result(c, "generate", gp, res, pack)
pp = dict(target_id=H.TARGET_ID, seed=H.SEED, designs=[dict(id=k, sequence=v["sequence"]) for k, v in res["designs"].items()])
H.pack_result(c, "predict", pp, c.run("predict", pp), pack)
s3 = H.Session("4", "tok", "http://127.0.0.1:9/api", "auto", log=print)
assert s3.mode_used == "stored"
s3.load_reference(); s3.set_hotspots(hs)
s3.submit("gen", "generate", dict(n_designs=15, binder_length=L, hotspots=hs))
r3 = s3.collect("gen"); assert len(r3) == 15 and r3[0]["mode"] == "precomputed" and r3[0]["metrics"]
s3.rerun_openfold3(); s3.collect("of3")
print(s3.score()[["id", "iptm", "source"]].head(2))
assert s3.score()["iptm"].notna().all()
try: s3.submit("x", "generate", dict(n_designs=15, binder_length=77, hotspots=hs)); raise SystemExit("should fail")
except RuntimeError as e: print("stored miss ->", str(e)[:70])
# invalid hotspots
try: s3.set_hotspots(["R:100"]); raise SystemExit("should fail")
except ValueError as e: print("hotspot check ->", e)
# switch server -> stored after submitting (server 'died' with the job pending)
s5 = H.Session("5", "tok-1", url, "server", log=lambda *a: None)
s5.load_reference(); s5.set_hotspots(hs)
mock.delay = 30
s5.submit("gen", "generate", dict(n_designs=15, binder_length=L, hotspots=hs))
s6 = H.Session("5", "tok", "http://127.0.0.1:9/api", "auto", log=print)
assert s6.mode_used == "stored" and s6.state["jobs"]["gen"]["job_id"].startswith("j")
s6.load_reference(); r6 = s6.collect("gen"); assert len(r6) == 15 and s6.state["jobs"]["gen"]["job_id"].startswith("pack-")
# a failed job can be sent again with the same key
s7 = H.Session("7", "tok-1", url, "server", log=print)
s7.load_reference(); s7.set_hotspots(hs); mock.delay = 0.1
mock.fail_next = 1
s7.submit("gen", "generate", dict(n_designs=5, binder_length=47, hotspots=hs))
try: s7.collect("gen"); raise SystemExit("should fail")
except RuntimeError as e: print("failed ->", str(e)[:50])
s7.submit("gen", "generate", dict(n_designs=5, binder_length=47, hotspots=hs))
assert len(s7.collect("gen")) == 5
print("slots", H.slot_for(1), H.slot_for(10), "cluster", [H.cluster_of(g) for g in range(1, 11)])
assert H.slot_for(10) == "14:23:30" and [H.cluster_of(g) for g in range(1, 11)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
print("SESSION TESTS PASSED")
