"""Fill the stored-results pack (ws3_data/pack) by running the real API once with the fixed seed.

    python precompute.py --server https://.../api --token TOKEN --pdb 6X18.pdb [--pdb2 9BYO.pdb] --out ws3_data/pack [--parents 3] [--lengths 30]

What is stored (everything the notebook can ask for in 'stored' mode):
  * the five reference peptides (one predict job)
  * for each hotspot preset: the RFD4-Proteina designs (design file + RFD4 metrics), then the OpenFold3 prediction of those
    sequences (the 'rerun' of cell 4.5). The binder length is the length of GLP-1 (30)
  * for each of those batches, the top PARENTS designs by ipTM x the four fix-presets of cell 5.2 (interface, core,
    interface+core, nothing) at temperature 0.20: round 1 redesign with 25 variants each
  * the PDB files 6X18 (and 9BYO, the exendin-D3 structure used in Step 2)
Round 2 and 3 are not stored. Re-running skips what is already in the pack, so it can be interrupted and continued.
"""
import argparse, sys, json, shutil, time
from pathlib import Path
import ws3_helpers as H

PRESETS = {"interface": ("interface",), "core": ("core",), "interface+core": ("interface", "core"), "nothing": ()}


def have(pack, task, payload):
    return (Path(pack) / "cache" / H.request_fingerprint(task, payload) / "result.json").exists()


def run_and_store(client, pack, task, payload, log=print):
    if have(pack, task, payload):
        res = LocalRead(pack, task, payload)
        return res, False
    t0 = time.time()
    res = client.run(task, payload)
    H.pack_result(client, task, payload, res, pack)
    log(f"  stored {task} {H.request_fingerprint(task, payload)} in {time.time() - t0:.0f} s")
    return LocalRead(pack, task, payload), True


def LocalRead(pack, task, payload):
    lp = H.LocalPack(pack)
    return lp.run(task, payload)


def score_batch(res, client_or_pack, ref, hotspots, work, predicted=None):
    """Score a stored/just-run result to rank parents. `predicted`: the OpenFold3 result for the same designs."""
    recs = H.save_result(client_or_pack, res, work)
    if predicted is not None:
        by = {r["id"]: r for r in H.save_result(client_or_pack, predicted, work)}
        for r in recs:
            if r["id"] in by:
                r["files"].update(by[r["id"]]["files"])
    return recs, H.score_records(recs, ref, hotspots)


def main(client, pdb_text, pack, lengths=None, n_parents=3, temperature=0.2, log=print, work="ws3_data/precompute_tmp", pdb2_text=None, pdb2_id="9BYO"):
    pack = Path(pack); pack.mkdir(parents=True, exist_ok=True)
    (pack / "6X18.pdb").write_text(pdb_text)
    if pdb2_text:
        (pack / f"{pdb2_id}.pdb").write_text(pdb2_text)
    ref = H.build_reference(pdb_text)
    lengths = lengths or [len(ref["pep_seq"])]
    base = dict(target_id=H.TARGET_ID, seed=H.SEED)
    refs = H.reference_list(ref)
    log("references")
    run_and_store(client, pack, "predict", dict(base, designs=[dict(id=r["id"], sequence=r["seq"]) for r in refs]), log)
    n_jobs = 0
    for pname, hots in ref["presets"].items():
        for L in lengths:
            log(f"{pname} | length {L}")
            gp = dict(base, n_designs=H.N_DESIGNS, binder_length=L, hotspots=list(hots))
            res, _ = run_and_store(client, pack, "generate", gp, log)
            src = H.LocalPack(pack)
            recs0 = H.save_result(src, res, work)
            pp = dict(base, designs=[dict(id=r["id"], sequence=r["sequence"]) for r in recs0])
            pres, _ = run_and_store(client, pack, "predict", pp, log)
            recs, df = score_batch(res, src, ref, hots, work, predicted=pres)
            top = df.sort_values("iptm", ascending=False, na_position="last").head(n_parents)["id"].tolist()
            by_id = {r["id"]: r for r in recs}
            for pid in top:
                design = Path(by_id[pid]["files"]["design"]).read_text()
                cls = H.residue_classes(design)
                for fname, kinds in PRESETS.items():
                    fixed = sorted(c["pos"] for c in cls if c["cls"] in kinds)
                    rp = dict(base, parent_id=pid, fixed_positions=fixed, temperature=temperature, n_sequences=H.N_VARIANTS, round=1)
                    _, new = run_and_store(client, pack, "redesign", rp, log)
                    n_jobs += new
    log(f"done; {n_jobs} new redesign jobs")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", required=True); ap.add_argument("--token", default=""); ap.add_argument("--pdb", required=True)
    ap.add_argument("--pdb2", default="", help="PDB file of 9BYO (exendin-D3 with the receptor) for Step 2")
    ap.add_argument("--out", default="ws3_data/pack"); ap.add_argument("--parents", type=int, default=3)
    ap.add_argument("--lengths", type=int, nargs="+", default=None, help="binder lengths (default: the length of GLP-1 in 6X18)")
    a = ap.parse_args()
    main(H.ApiClient(a.server, a.token, poll=10, timeout=3600), Path(a.pdb).read_text(), a.out, a.lengths, a.parents,
         pdb2_text=Path(a.pdb2).read_text() if a.pdb2 else None)
