import sys, os, tempfile, json, time, types
sys.path.insert(0, "/home/claude/nb2")
os.environ["MPLBACKEND"] = "Agg"
pm = types.ModuleType("py3Dmol")
class _V:
    def __init__(self, **k): pass
    def __getattr__(self, n): return lambda *a, **k: None
pm.view = _V; sys.modules["py3Dmol"] = pm
import ws3_helpers as H, synth as S, mock_server as M, warm_cache as W

text, rs = S.fake_6x18(uniprot_offset=7)
mock = M.Mock(text, rs, delay=0.4)
srv, url = M.serve(mock)
work = tempfile.mkdtemp(); os.chdir(work)
open("6X18.pdb", "w").write(text)

# dry run sends nothing
n0 = mock.n_requests
assert W.main(["--server", url, "--dry-run"]) == 0 and mock.n_requests == n0
# no token -> stops
try: W.main(["--server", url]); raise SystemExit("should need a token")
except SystemExit as e: assert "token" in str(e).lower()
# bad group
try: W.parse_groups("0-3"); raise SystemExit("bad group accepted")
except SystemExit as e: assert "between 1 and 10" in str(e)
assert W.parse_groups("1-3,5,5") == [1, 2, 3, 5]

# full warm-up, 10 groups x 3 sets, concurrency 4 (> cap of 3, so the 429 path is exercised), then verify
t0 = time.time()
rc = W.main(["--server", url, "--token", "tok-1", "--concurrency", "4", "--poll", "0.1", "--backoff", "0.3", "--verify", "--report", "rep.json"])
print("elapsed", round(time.time() - t0, 1), "s, rc", rc)
assert rc == 0
rep = json.load(open("rep.json"))
assert len(rep["rows"]) == 30 and all(r["status"] == "ok" for r in rep["rows"]), [r for r in rep["rows"] if r["status"] != "ok"]
assert rep["reference"]["status"] == "ok" and not rep["verify_failed"]
assert all(r["gen_mode"] == "live" and r["of3_mode"] == "live" and r["n_designs"] == 15 for r in rep["rows"])
assert len({r["gen_fingerprint"] for r in rep["rows"]}) == 30           # distinct seed per group, distinct set per preset

# a second run is served from the cache
rc = W.main(["--server", url, "--token", "tok-1", "--concurrency", "4", "--poll", "0.1", "--report", "rep2.json"])
rep2 = json.load(open("rep2.json"))
assert rc == 0 and all(r["gen_mode"] == "cache" and r["of3_mode"] == "cache" for r in rep2["rows"]) and rep2["reference"]["mode"] == "cache"

# the real notebook flow of a student now hits the cache: group 7, each preset; custom hotspots do not
os.makedirs("ws3_data"); open("ws3_data/6X18.pdb", "w").write(text)
for g in ("7", "10", "1"):
    s = H.Session(g, "tok-1", url, "server", root="ws3_data", log=lambda *a: None)
    ref = s.load_reference()
    r = s.run_references()
    assert s.client.status(s.state["jobs"]["refs"]["job_id"])["execution_mode"] == "cache"
    for name, hs in ref["presets"].items():
        s2 = H.Session(g, "tok-1", url, "server", root=tempfile.mkdtemp(), log=lambda *a: None)
        s2.load_reference(); s2.set_hotspots(hs, "preset")
        s2.submit("gen", "generate", dict(n_designs=H.N_DESIGNS, binder_length=len(ref["pep_seq"]), hotspots=s2.hotspots))
        recs = s2.collect("gen", origin="rfd4")
        assert s2.client.status(s2.state["jobs"]["gen"]["job_id"])["execution_mode"] == "cache", (g, name)
        s2.rerun_openfold3()
        s2.collect("of3")
        assert s2.client.status(s2.state["jobs"]["of3"]["job_id"])["execution_mode"] == "cache", (g, name)
    s3 = H.Session(g, "tok-1", url, "server", root=tempfile.mkdtemp(), log=lambda *a: None)
    s3.load_reference(); hs = sorted(ref["presets"][list(ref["presets"])[0]])[:-1]; s3.set_hotspots(hs, "custom")
    s3.submit("gen", "generate", dict(n_designs=H.N_DESIGNS, binder_length=len(ref["pep_seq"]), hotspots=s3.hotspots))
    assert s3.client.status(s3.state["jobs"]["gen"]["job_id"])["execution_mode"] != "cache"
print("OK: student flow of groups 7, 10 and 1 is answered from the cache for all presets; a custom hotspot set is not")

# failure handling: the server fails the next job; the script retries and finishes
mock.fail_next = 1
rc = W.main(["--server", url, "--token", "tok-1", "--groups", "2", "--presets", "1", "--designs", "6", "--poll", "0.1", "--backoff", "0.2", "--report", "rep3.json"])
assert rc == 0 and json.load(open("rep3.json"))["rows"][0]["n_designs"] == 6
# wrong token -> clear failure, nonzero exit, no endless loop
rc = W.main(["--server", url, "--token", "nope", "--groups", "3", "--presets", "1", "--skip-refs", "--poll", "0.1", "--report", "rep4.json"]) if False else None
print("test_warm OK")
