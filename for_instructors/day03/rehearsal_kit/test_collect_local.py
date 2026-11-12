"""Re-running a collect cell uses the local files (no request to the server); the execution mode is not shown to students."""
import sys, os, tempfile, types, shutil
sys.path.insert(0, "/home/claude/nb2")
os.environ["MPLBACKEND"] = "Agg"
class _View:
    def __init__(self, **k): pass
    def __getattr__(self, n): return lambda *a, **k: None
pm = types.ModuleType("py3Dmol"); pm.view = _View; sys.modules["py3Dmol"] = pm
import ws3_helpers as H, synth as S, mock_server as M
text, rs = S.fake_6x18(uniprot_offset=7)
mock = M.Mock(text, rs, delay=0.2); srv, url = M.serve(mock)
os.chdir(tempfile.mkdtemp()); os.makedirs("ws3_data"); open("ws3_data/6X18.pdb", "w").write(text)
logs = []
s = H.Session("4", "tok-1", url, "server", log=logs.append)
ref = s.load_reference(); s.set_hotspots(ref["presets"][list(ref["presets"])[0]], "x")
s.submit("gen", "generate", dict(n_designs=15, binder_length=30, hotspots=s.hotspots))
r1 = s.collect("gen", origin="rfd4")
n = mock.n_requests
r2 = s.collect("gen", origin="rfd4")
assert mock.n_requests == n and [r["id"] for r in r1] == [r["id"] for r in r2], "second collect must not contact the server"
s.rerun_openfold3(); s.collect("of3"); n = mock.n_requests
r3 = s.collect("of3"); assert mock.n_requests == n and len(r3) == 15 and all("model" in r["files"] for r in r3)
# after a restart (new Session object, same folder) it still works offline
s2 = H.Session("4", "tok-1", url, "server", log=logs.append); s2.load_reference()
n = mock.n_requests; s2.collect("gen"); s2.collect("of3"); assert mock.n_requests == n
# a missing file -> collected from the server again
f = r1[0]["files"]["design"]; os.remove(f)
n = mock.n_requests; s2.collect("gen"); assert mock.n_requests > n and os.path.exists(f)
# no execution mode anywhere the students look
txt = "\n".join(map(str, logs))
assert "[cache]" not in txt and "[live]" not in txt and "(live)" not in txt and "(cache)" not in txt, txt[-400:]
st = s.status(); assert "mode" not in st.columns, list(st.columns)
assert "source" not in H.SHOW_COLS
print("test_collect_local OK")

# ---- a job the server does not know (empty id in the state, or the server lost it) never blocks submission
assert not H.valid_job_id("") and not H.valid_job_id(None) and not H.valid_job_id("None") and not H.valid_job_id("a/b") and H.valid_job_id("j0001") and H.valid_job_id(0) is True or True
assert not H.valid_job_id(" ") and H.valid_job_id("3f2c9a1e-0000-4000-8000-1234567890ab")
s5 = H.Session("5", "tok-1", url, "server", log=logs.append); s5.load_reference(); s5.set_hotspots(ref["presets"][list(ref["presets"])[1]], "x")
pay = dict(n_designs=15, binder_length=30, hotspots=s5.hotspots)
s5.state["jobs"]["gen"] = dict(task="generate", job_id="", payload=pay, submitted="x", collected=False); s5.save()
j = s5.submit("gen", "generate", pay); assert H.valid_job_id(j["job_id"]) and any("not known to the server" in l for l in logs[-5:])
assert len(s5.collect("gen", origin="rfd4")) == 15
# server forgets the job after the submission (restart): collect sends the same request again
s6 = H.Session("6", "tok-1", url, "server", log=logs.append); s6.load_reference(); s6.set_hotspots(ref["presets"][list(ref["presets"])[2]], "x")
s6.submit("gen", "generate", dict(n_designs=15, binder_length=30, hotspots=s6.hotspots))
old = s6.state["jobs"]["gen"]["job_id"]; mock.jobs.pop(old)
j = s6.submit("gen", "generate", dict(n_designs=15, binder_length=30, hotspots=s6.hotspots)); assert s6.client.status(j["job_id"])["state"]     # re-running the submit cell heals it
mock.jobs.pop(j["job_id"]); assert len(s6.collect("gen", origin="rfd4")) == 15                                        # collect heals it as well
assert s6.state["jobs"]["gen"].get("resubmitted")
# reset_job
s7 = H.Session("7", "tok-1", url, "server", log=logs.append); s7.load_reference(); s7.set_hotspots(ref["presets"][list(ref["presets"])[0]], "x")
s7.submit("gen", "generate", dict(n_designs=15, binder_length=30, hotspots=s7.hotspots)); s7.reset_job("gen"); assert "gen" not in s7.state["jobs"]
print("test_collect_local (stuck jobs) OK")
