import sys, os, tempfile, io
sys.path.insert(0, "/home/claude/nb2")
import ws3_helpers as H, synth as S, mock_server as M, precompute as P
text, rs = S.fake_6x18()
mock = M.Mock(text, rs, delay=0.05, max_running=10)
srv, url = M.serve(mock)
c = H.ApiClient(url, "tok-1", poll=0.05, log=lambda *a: None)
d = tempfile.mkdtemp(); os.chdir(d)
pack = os.path.join(d, "pack")
logs = []
P.main(c, text, pack, lengths=(30,), n_parents=2, log=logs.append, work=os.path.join(d, "tmp"))
print("\n".join(logs[-4:]))
n_before = mock.n_requests
P.main(c, text, pack, lengths=(30,), n_parents=2, log=lambda *a: None, work=os.path.join(d, "tmp"))
print("second run extra requests:", mock.n_requests - n_before)
import glob
print("cache entries:", len(glob.glob(pack + "/cache/*/result.json")))
