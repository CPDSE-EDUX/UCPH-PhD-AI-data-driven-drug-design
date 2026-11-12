"""Warm the server cache for the workshop: send every request that does NOT depend on what the students choose.

    python warm_cache.py --token TOKEN [--server https://server/api] [--pdb 6X18.pdb] [--groups 1-10] [--concurrency 3]

What is sent (each request carries the seed that the notebook of that group will use, SEED 2026 + group number, so that the
students' own requests hit the cache):

  1. The five reference peptides (cell 2.x): ONE predict job, base seed 2026, shared by all groups.
  2. For every group and every default hotspot set (the three presets of cell 1.5, binder length = length of GLP-1, N_DESIGNS designs):
       a. RFD4-Proteina `generate`   (cell 4.1)
       b. OpenFold3 `predict` of exactly those sequences   (cell 4.5, "re-run in OpenFold3")
     = 3 x 10 generate jobs + 3 x 10 predict jobs + 1 reference job (with the default settings).

NOT sent (they depend on the students and cannot be cached in advance): ProteinMPNN redesign, the OpenFold3 evaluation of the
redesigns, manual variants, and generate jobs with hotspots other than the three presets.

Safe to run again: a request that is already cached comes back immediately with execution_mode 'cache'. `--verify` sends
every request a second time and checks that it is now answered from the cache. The token is read from --token or the
environment variable WS3_TOKEN and only ever sent to the --server host.
"""
import argparse, os, sys, json, time, threading, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ws3_helpers as H

DEFAULT_SERVER = "https://server/api"
LOCK = threading.Lock()


def say(msg):
    with LOCK:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


def parse_groups(text):
    out = []
    for part in str(text).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    bad = [g for g in out if not 1 <= g <= H.N_GROUPS]
    if bad:
        raise SystemExit(f"Groups must be between 1 and {H.N_GROUPS}: {bad}")
    return sorted(set(out))


def group_payload(group, payload):
    """Exactly what Session.submit adds in the notebook: target_id, the seed of the group and the group number."""
    return dict(payload, target_id=H.TARGET_ID, seed=H.SEED + int(group), group=str(int(group)).zfill(2))


def ref_payload(ref):
    """Session.run_references: the reference peptides use the base seed (shared by all groups)."""
    refs = H.reference_list(ref)
    return dict(designs=[dict(id=r["id"], sequence=r["seq"]) for r in refs], target_id=H.TARGET_ID, seed=H.SEED, group="01")


def hotspot_sets(ref, which):
    """The default hotspot sets (cell 1.5), sorted by residue number as Session.set_hotspots does."""
    names = list(ref["presets"])
    sel = names if which in (None, "all") else [names[int(i) - 1] for i in str(which).split(",")]
    return {n: sorted(set(ref["presets"][n]), key=lambda s: int(str(s).split(":")[1])) for n in sel}


class Runner:
    def __init__(self, client, poll=4.0, timeout=3600, backoff=30.0, retries=2):
        self.c, self.poll, self.timeout, self.backoff, self.retries = client, poll, timeout, backoff, retries

    def submit(self, task, payload, label):
        """POST with a wait-and-retry when the server says that the running-job limit is reached (HTTP 429)."""
        for attempt in range(1, 200):
            try:
                return self.c.submit(task, payload)["job_id"]
            except RuntimeError as e:
                if "limit of running jobs" in str(e):
                    say(f"  {label}: server busy (limit of running jobs), waiting {self.backoff:.0f} s")
                    time.sleep(self.backoff)
                    continue
                raise
        raise RuntimeError("the server stayed busy for too long")

    def wait(self, job_id, label):
        t0, last = time.time(), None
        while True:
            st = self.c.status(job_id)
            state = st["state"]
            if state != last:
                last = state
                if state not in H.DONE_STATES:
                    say(f"  {label}: job {job_id} {state}" + (f' (queue position {st["queue_position"]})' if st.get("queue_position") is not None else ""))
            if state in H.DONE_STATES:
                return st
            if state in H.FAIL_STATES:
                raise RuntimeError(f'job {job_id} {state}: {st.get("message", "no message")}')
            if time.time() - t0 > self.timeout:
                raise RuntimeError(f"job {job_id} not finished after {self.timeout:.0f} s")
            time.sleep(self.poll)

    def job(self, task, payload, label, need_result=False):
        """Submit, wait, and return a dict(job_id, mode, seconds, result?). One retry for a failed job."""
        err = None
        for attempt in range(self.retries + 1):
            t0 = time.time()
            try:
                jid = self.submit(task, payload, label)
                st = self.wait(jid, label)
                out = dict(job_id=jid, mode=st.get("execution_mode", ""), seconds=round(time.time() - t0, 1))
                if need_result:
                    rid = st.get("result_id") or jid
                    out["result"] = self.c._req("GET", self.c.ep["result"].format(id=rid))
                return out
            except RuntimeError as e:
                err = e
                say(f"  {label}: {str(e)[:150]}" + (" - trying again" if attempt < self.retries else " - giving up"))
                if "refused the request" in str(e) or "Server error 4" in str(e):
                    break                        # token or payload problem: a second try will not help
                time.sleep(min(self.backoff, 10))
        raise err


def pipeline(run, group, name, hotspots, ref, n_designs, skip_of3):
    """One (group, hotspot set): generate, then OpenFold3 on the returned sequences. Returns a report row."""
    L = len(ref["pep_seq"])
    tag = f"g{int(group):02d} {name[:22]}"
    row = dict(group=int(group), hotspot_set=name, hotspots=hotspots, seed=H.SEED + int(group))
    gen = group_payload(group, dict(n_designs=n_designs, binder_length=L, hotspots=hotspots))
    row["gen_fingerprint"] = H.request_fingerprint("generate", gen)
    row["_gen"] = gen
    try:
        g = run.job("generate", gen, tag + " generate", need_result=True)
        designs = [dict(id=k, sequence=d.get("sequence", "")) for k, d in g["result"].get("designs", {}).items()]
        if len(designs) != n_designs:
            say(f"  {tag}: the server returned {len(designs)} designs, not {n_designs}")
        row.update(gen_job=g["job_id"], gen_mode=g["mode"], gen_seconds=g["seconds"], n_designs=len(designs))
        if skip_of3:
            row["status"] = "ok"
            return row
        pred = group_payload(group, dict(designs=designs))
        row["of3_fingerprint"] = H.request_fingerprint("predict", pred)
        o = run.job("predict", pred, tag + " openfold3")
        row.update(of3_job=o["job_id"], of3_mode=o["mode"], of3_seconds=o["seconds"], status="ok", _pred=pred)
    except RuntimeError as e:
        row.update(status="failed", error=str(e)[:300])
    say(f"{tag}: {row['status']}  gen {row.get('gen_mode', '-')} {row.get('gen_seconds', '-')} s, openfold3 {row.get('of3_mode', '-')} {row.get('of3_seconds', '-')} s")
    return row


def verify(run, rows, reference):
    """Send every request again: it must now come back from the cache."""
    bad = []
    checks = [("references", "predict", reference)] if reference else []
    for r in rows:
        if r["status"] != "ok":
            continue
        checks.append((f"g{r['group']:02d} {r['hotspot_set'][:22]} generate", "generate", r["_gen"]))
        if r.get("_pred"):
            checks.append((f"g{r['group']:02d} {r['hotspot_set'][:22]} openfold3", "predict", r["_pred"]))
    say(f"Verifying {len(checks)} requests ...")
    for label, task, payload in checks:
        try:
            j = run.job(task, payload, label)
            if j["mode"] != "cache":
                bad.append(label + f" (answered by '{j['mode']}')")
        except RuntimeError as e:
            bad.append(label + f" ({str(e)[:60]})")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description="Warm the server cache with every request that does not depend on the students.")
    ap.add_argument("--server", default=os.environ.get("WS3_SERVER", DEFAULT_SERVER))
    ap.add_argument("--token", default=os.environ.get("WS3_TOKEN", ""), help="or set the environment variable WS3_TOKEN")
    ap.add_argument("--pdb", default="", help="path to 6X18.pdb (default: look in ./, ./ws3_data/, then download from RCSB)")
    ap.add_argument("--groups", default=f"1-{H.N_GROUPS}", help="e.g. 1-10 or 3,5,7 (default: all)")
    ap.add_argument("--presets", default="all", help="'all' or numbers of the default hotspot sets, e.g. 1,3 (default: all three)")
    ap.add_argument("--designs", type=int, default=H.N_DESIGNS, help=f"designs per request (the notebook uses {H.N_DESIGNS})")
    ap.add_argument("--concurrency", type=int, default=3, help="requests in flight at the same time (default 3 = the per-group limit)")
    ap.add_argument("--skip-of3", action="store_true", help="only RFD4 (generate), not the OpenFold3 re-run")
    ap.add_argument("--skip-refs", action="store_true", help="do not send the reference peptides")
    ap.add_argument("--verify", action="store_true", help="afterwards send everything again and check that it is answered from the cache")
    ap.add_argument("--dry-run", action="store_true", help="print the plan and the estimated time, send nothing")
    ap.add_argument("--report", default="warm_cache_report.json")
    ap.add_argument("--poll", type=float, default=4.0, help="seconds between status checks")
    ap.add_argument("--backoff", type=float, default=30.0, help="seconds to wait after HTTP 429 (running-job limit)")
    ap.add_argument("--est-gen", type=float, default=60.0, help="seconds per generate job, for the estimate only (a guess: measure and set)")
    ap.add_argument("--est-of3", type=float, default=130.0, help="seconds per 15-design OpenFold3 job, for the estimate only (a guess)")
    a = ap.parse_args(argv)

    groups = parse_groups(a.groups)
    pdb = None
    for p in ([a.pdb] if a.pdb else []) + ["6X18.pdb", "ws3_data/6X18.pdb"]:
        if p and Path(p).exists():
            pdb = Path(p).read_text(); break
    if pdb is None:
        if a.pdb:
            raise SystemExit(f"{a.pdb} not found")
        say("Downloading 6X18 from RCSB ...")
        pdb = H.fetch_rcsb("6X18", "ws3_data")
    ref = H.build_reference(pdb)
    sets = hotspot_sets(ref, a.presets)
    L = len(ref["pep_seq"])

    n_gen = len(groups) * len(sets)
    n_of3 = 0 if a.skip_of3 else n_gen
    n_ref = 0 if a.skip_refs else 1
    est = (n_gen * a.est_gen + n_of3 * a.est_of3 + n_ref * 40) / max(1, a.concurrency)
    say(f"Server {a.server}; target {H.TARGET_ID}; binder length {L}; {a.designs} designs per request")
    say(f"Groups {groups[0]}..{groups[-1]} ({len(groups)}), seeds {H.SEED + groups[0]}..{H.SEED + groups[-1]}; {len(sets)} hotspot set(s):")
    for n, hs in sets.items():
        say(f"   {n}: {', '.join(hs)}")
    say(f"Requests: {n_ref} reference predict + {n_gen} generate + {n_of3} OpenFold3 predict = {n_ref + n_gen + n_of3} jobs "
        f"(about {est / 60:.0f} min with {a.concurrency} at a time, if the server runs them in parallel; on one GPU, closer to {(n_gen * a.est_gen + n_of3 * a.est_of3) / 60:.0f} min)")
    say("Not sent (depends on the students): ProteinMPNN redesign, OpenFold3 of the redesigns, manual variants, other hotspot sets.")
    if a.dry_run:
        return 0
    if not a.token:
        raise SystemExit("No token: use --token or set WS3_TOKEN.")

    client = H.ApiClient(a.server, a.token, poll=a.poll, retries=3, log=lambda *x: None)
    h = client.health()
    say(f"Server health: {json.dumps(h)[:160]}")
    run = Runner(client, poll=a.poll, backoff=a.backoff)
    t0 = time.time()
    report = dict(server=a.server, started=H.now_stamp(), seed_base=H.SEED, groups=groups, rows=[], reference=None)

    ref_pl = None
    if not a.skip_refs:
        ref_pl = ref_payload(ref)
        try:
            j = run.job("predict", ref_pl, "references")
            report["reference"] = dict(status="ok", fingerprint=H.request_fingerprint("predict", ref_pl), **j)
            say(f"references: ok, {j['mode']}, {j['seconds']} s")
        except RuntimeError as e:
            report["reference"] = dict(status="failed", error=str(e)[:300])
            say(f"references: FAILED {e}")

    items = [(g, n, hs) for g in groups for n, hs in sets.items()]
    rows = []
    with ThreadPoolExecutor(max_workers=max(1, a.concurrency)) as ex:
        futs = [ex.submit(pipeline, run, g, n, hs, ref, a.designs, a.skip_of3) for g, n, hs in items]
        for f in as_completed(futs):
            rows.append(f.result())
    rows.sort(key=lambda r: (r["group"], r["hotspot_set"]))

    bad = verify(run, rows, ref_pl) if a.verify else []
    failed = [r for r in rows if r["status"] != "ok"] + ([report["reference"]] if report["reference"] and report["reference"]["status"] != "ok" else [])

    report["finished"] = H.now_stamp()
    report["minutes"] = round((time.time() - t0) / 60, 1)
    report["rows"] = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    report["verify_failed"] = bad
    Path(a.report).write_text(json.dumps(report, indent=1))

    live = sum(1 for r in rows for k in ("gen_mode", "of3_mode") if r.get(k) == "live")
    cached = sum(1 for r in rows for k in ("gen_mode", "of3_mode") if r.get(k) == "cache")
    say(f"Done in {report['minutes']} min: {len(rows) - len([r for r in rows if r['status'] != 'ok'])}/{len(rows)} pipelines ok; "
        f"{live} jobs computed now, {cached} were already cached. Report: {a.report}")
    if a.verify:
        say("Verification: all requests are answered from the cache." if not bad else "Verification FAILED for: " + "; ".join(bad))
    if failed:
        say(f"{len(failed)} failed (group / set): " + "; ".join(f"g{r.get('group', '-')} {r.get('hotspot_set', 'references')[:22]}: {r.get('error', '')[:60]}" for r in failed)
            + "  -> run the script again; finished requests come back from the cache.")
    return 1 if (failed or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
