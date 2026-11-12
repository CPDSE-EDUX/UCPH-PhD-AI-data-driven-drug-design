import sys, tempfile, json, time
sys.path.insert(0, "/home/claude/nb2")
import numpy as np
import ws3_helpers as H, synth as S, mock_server as M

text, rs = S.fake_6x18()
mock = M.Mock(text, rs, delay=0.3)
srv, url = M.serve(mock)
c = H.ApiClient(url, "tok-1", poll=0.1, log=lambda *a: None)
print("health", c.health())
ref = mock.ref
hot = ref["presets"]["Whole footprint (strongest contacts overall)"]
pl = dict(target_id=H.TARGET_ID, seed=H.SEED, n_designs=25, binder_length=60, hotspots=hot, group="g1")
t0 = time.time(); res = c.run("generate", pl); print("generate", len(res["designs"]), round(time.time() - t0, 2), res["execution_mode"])
assert len(res["designs"]) == 25
t0 = time.time(); res2 = c.run("generate", pl); print("again", round(time.time() - t0, 2), res2["execution_mode"])
assert res2["execution_mode"] == "cache" and res2["result_id"] == res["result_id"]
root = tempfile.mkdtemp()
recs = H.save_result(c, res, root)
assert recs[0]["files"]["design"].endswith("design.pdb")
# predict
pp = dict(target_id=H.TARGET_ID, seed=H.SEED, designs=[dict(id=r["id"], sequence=r["sequence"]) for r in recs])
pr = c.run("predict", pp); precs = H.save_result(c, pr, root)
for r, p in zip(recs, precs):
    r["files"].update(p["files"])
df = H.score_records(recs, ref, hot, extra=dict(group="g1"))
print(df[["id", "iptm", "binder_plddt", "iface_pae", "backbone_rmsd", "pose_rmsd", "hotspot_hits", "checks"]].head(6))
assert df["iptm"].notna().all()
# references
rl = H.reference_list(ref)
rp = c.run("predict", dict(target_id=H.TARGET_ID, seed=H.SEED, designs=[dict(id=r["id"], sequence=r["seq"]) for r in rl]))
rr = H.save_result(c, rp, root)
rdf = H.score_records([dict(r, origin="reference") for r in rr], ref, hot)
print(rdf[["id", "iptm", "binder_plddt", "iface_pae", "pose_rmsd", "site_overlap", "checks"]])
assert rdf.set_index("id").loc["ref_glp1", "iptm"] > rdf.set_index("id").loc["ctrl_scrambled", "iptm"]
# redesign
parent = df.sort_values("iptm", ascending=False).iloc[0]
cl = H.residue_classes(open(recs[0]["files"]["design"]).read())
rd = dict(target_id=H.TARGET_ID, seed=H.SEED, parent_id=parent["id"], fixed_positions=[1, 2, 3], temperature=0.2, n_sequences=25, round=1)
rres = c.run("redesign", rd); print("redesign", len(rres["designs"]))
# error paths
bad = H.ApiClient(url, "nope", poll=0.1, log=lambda *a: None)
try: bad.submit("generate", pl); raise SystemExit("should fail")
except RuntimeError as e: print("401 ->", str(e)[:60])
mock.fail_next = 1
try: c.run("generate", dict(pl, binder_length=40)); raise SystemExit("should fail")
except RuntimeError as e: print("failed job ->", str(e)[:70])
for k in range(3): c.submit("generate", dict(pl, binder_length=40 + k, n_designs=5))
try: c.submit("generate", dict(pl, binder_length=99)); raise SystemExit("should 429")
except RuntimeError as e: print("429 ->", str(e)[:60])
slow = H.ApiClient(url, "tok-2", poll=0.05, timeout=0.2, log=lambda *a: None)
mock.delay = 5
try: slow.run("generate", dict(pl, binder_length=50, n_designs=3)); raise SystemExit("should time out")
except RuntimeError as e: print("timeout ->", str(e)[:50])
dead = H.ApiClient("http://127.0.0.1:9/api", "t", retries=1, log=lambda *a: None)
try: dead.health(); raise SystemExit("should fail")
except RuntimeError as e: print("unreachable ->", str(e)[:50])

# pack + local pack
pack = tempfile.mkdtemp()
fp = H.pack_result(c, "generate", pl, res, pack)
lp = H.LocalPack(pack)
r3 = lp.run("generate", pl); recs3 = H.save_result(lp, r3, root + "_b")
assert len(recs3) == 25 and recs3[0]["mode"] == "precomputed" and recs3[0]["files"]["design"]
try: lp.submit("generate", dict(pl, binder_length=77)); raise SystemExit("should fail")
except RuntimeError as e: print("pack miss ->", str(e)[:50])
print("ALL CLIENT TESTS PASSED")
