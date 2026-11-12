import sys, os, types, tempfile, threading, zipfile, shutil, functools
sys.path.insert(0, "/home/claude/nb2")
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import ws3_helpers as H, synth as S, mock_server as M, precompute as P

logs = []
assert not H.in_colab()
assert H.workspace_root("drive", log=logs.append) == "ws3_data" and "Not running in Colab" in logs[-1]
assert H.workspace_root("local", log=logs.append) == "ws3_data"
tmp = tempfile.mkdtemp(); drive = os.path.join(tmp, "MyDrive")
gm, gcm = types.ModuleType("google"), types.ModuleType("google.colab")
gcm.drive = types.SimpleNamespace(mount=lambda p, **k: os.makedirs(os.path.join(p, "MyDrive"), exist_ok=True))
dl = []; gcm.files = types.SimpleNamespace(download=lambda p: dl.append(p))
gm.colab = gcm; sys.modules["google"], sys.modules["google.colab"] = gm, gcm
assert H.workspace_root("drive", drive_dir=drive, log=logs.append) == "ws3_data" and "not mounted" in logs[-1]   # cell 0.3 not run yet
gcm.drive.mount(os.path.dirname(drive))                                                                     # what cell 0.3 does
r = H.workspace_root("drive", drive_dir=drive, log=logs.append)
assert r == os.path.join(drive, "ws3_data") and os.path.isdir(r), r
assert H.workspace_root("local", drive_dir=drive, log=logs.append) == "ws3_data"
def bad(*a, **k): raise RuntimeError("auth refused")
d = tempfile.mkdtemp(); os.makedirs(d + "/handin"); open(d + "/handin/a.txt", "w").write("x")
z = H.offer_download(d + "/handin", "handin_g01", log=logs.append)
assert z.endswith("handin_g01.zip") and zipfile.ZipFile(z).namelist() == ["a.txt"] and dl == [z]
gcm.files = types.SimpleNamespace(download=bad)
H.offer_download(d + "/handin", "handin_g02", log=logs.append); assert "Automatic download failed" in logs[-1]
text, rs = S.fake_6x18()
mock = M.Mock(text, rs, delay=0.05, max_running=10); srv, url = M.serve(mock)
c = H.ApiClient(url, "tok-1", poll=0.05, log=lambda *a: None)
w = tempfile.mkdtemp(); os.chdir(w)
P.main(c, text, "build/pack", lengths=(30,), n_parents=1, log=lambda *a: None, work="build/tmp")
shutil.make_archive("serve/ws3_pack", "zip", "build", "pack")
os.chdir("serve")
handler = functools.partial(SimpleHTTPRequestHandler, directory=os.getcwd())
web = ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=web.serve_forever, daemon=True).start()
os.chdir(tempfile.mkdtemp())
s = H.Session("9", "", "", "stored", root="ws3_data", log=logs.append, pack_url=f"http://127.0.0.1:{web.server_address[1]}/ws3_pack.zip")
assert s.mode_used == "stored" and any("Downloading" in x for x in logs)
try: H.Session("9", "", "", "stored", root="other", log=logs.append, pack_url="http://127.0.0.1:9/none.zip"); raise SystemExit("should fail")
except RuntimeError as e: assert "No server and no stored results" in str(e) and any("Could not download" in x for x in logs)
print("COLAB HELPER TESTS PASSED")
