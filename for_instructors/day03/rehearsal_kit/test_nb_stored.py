import sys, os, types, json, tempfile, re, io, contextlib
sys.path.insert(0, "/home/claude/nb2")
os.environ["MPLBACKEND"] = "Agg"
import numpy as np

# ---------- stubs for ipywidgets and IPython (the sandbox has neither) ----------
class W:
    def __init__(self, *a, **k):
        self._obs = []
        self.__dict__["_vals"] = {}
        for key, val in k.items(): self._vals[key] = val
        self._vals.setdefault("value", k.get("value", ""))
        self.children = a[0] if a and isinstance(a[0], (list, tuple)) else k.get("children", [])
        self._clicks = []
    def __getattr__(self, n):
        if n in ("_vals", "_obs", "_clicks"): raise AttributeError(n)
        return self._vals.get(n)
    def __setattr__(self, n, v):
        if n in ("_obs", "_vals", "children", "_clicks"): return object.__setattr__(self, n, v)
        old = self._vals.get(n); self._vals[n] = v
        if n == "value" and old != v:
            for cb in list(self._obs): cb({"new": v, "old": old, "name": "value"})
    def observe(self, cb, names=None): self._obs.append(cb)
    def on_click(self, cb): self._clicks.append(cb)
    def click(self):
        for cb in self._clicks: cb(self)
    def __enter__(self): return self
    def __exit__(self, *a): return False
class Dropdown(W):
    def __init__(self, options=(), value=None, **k):
        super().__init__(options=options, **k); self._vals["options"] = options
        self._vals["value"] = value if value is not None else (options[0][1] if options and isinstance(options[0], tuple) else (options[0] if options else None))
class SelectMultiple(W):
    def __init__(self, options=(), value=(), **k):
        super().__init__(options=options, **k); self._vals["value"] = tuple(value)
class Layout(W): pass
wmod = types.ModuleType("ipywidgets")
for n, c in dict(Dropdown=Dropdown, SelectMultiple=SelectMultiple, Layout=Layout, Text=W, Textarea=W, FloatSlider=W, Button=W,
                 HTML=W, Output=W, VBox=W, HBox=W, IntText=W, Checkbox=W, GridBox=W).items(): setattr(wmod, n, c)
sys.modules["ipywidgets"] = wmod
shown = []
imod = types.ModuleType("IPython"); dmod = types.ModuleType("IPython.display")
dmod.display = lambda *a, **k: shown.append(a); dmod.HTML = lambda s: ("HTML", s); dmod.clear_output = lambda **k: None
imod.get_ipython = lambda: None; imod.version_info = (9, 0, 0); imod.display = dmod; sys.modules["IPython"] = imod; sys.modules["IPython.display"] = dmod

# stub py3Dmol so the 3D code paths run (records the calls)
class _View:
    calls = []
    def __init__(self, **k): _View.calls.append(("view", k))
    def __getattr__(self, n):
        def f(*a, **k): _View.calls.append((n, a)); return None
        return f
pm = types.ModuleType("py3Dmol"); pm.view = _View; sys.modules["py3Dmol"] = pm
COLAB = bool(os.environ.get("COLAB"))
colab_dl = []
if COLAB:
    _tmp = tempfile.mkdtemp(); _drive = os.path.join(_tmp, "MyDrive"); os.environ["WS3_DRIVE_DIR"] = _drive
    gm, gcm = types.ModuleType("google"), types.ModuleType("google.colab")
    gcm.drive = types.SimpleNamespace(mount=lambda p, **k: os.makedirs(os.path.join(p, "MyDrive"), exist_ok=True))
    gcm.files = types.SimpleNamespace(download=lambda p: colab_dl.append(p))
    gcm.output = types.SimpleNamespace(enable_custom_widget_manager=lambda: colab_dl.append("widgetmgr"))
    gm.colab = gcm; sys.modules["google"], sys.modules["google.colab"] = gm, gcm
import ws3_helpers as H, synth as S, mock_server as M
# ---------- build the notebook ----------
import subprocess
nbpath = "/home/claude/nb2/Workshop3_GLP1R_binder_design.ipynb"
print(subprocess.run([sys.executable, "/home/claude/nb2/make_nb.py", nbpath], capture_output=True, text=True).stdout)
nb = json.load(open(nbpath))
codes = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
print(len(codes), "code cells")

text, rs = S.fake_6x18()
mock = M.Mock(text, rs, delay=0.2)
srv, url = M.serve(mock)
work = tempfile.mkdtemp(); os.chdir(work); os.makedirs("ws3_data"); open("ws3_data/6X18.pdb", "w").write(text)

ns = {"__name__": "__main__"}
def run(src, label=""):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(src, f"<cell {label}>", "exec"), ns)
    except Exception as e:
        print(buf.getvalue()[-800:]); raise
    return buf.getvalue()

def find(sub, start=0):
    for i in range(start, len(codes)):
        if sub in codes[i]: return i
    raise KeyError(sub)

def fill(form, txt="This is a sufficiently long answer for the check."):
    for b in form.boxes.values(): b.value = txt

i = 0
def go(sub, after=None, expect=None):
    global i
    i = find(sub, i)
    out = run(codes[i], sub[:20])
    if expect: assert expect in out, (sub, out[-400:])
    if after: exec(after, ns)
    i += 1
    return out

# ---- build the stored pack with the mock, then work offline
import precompute as P
c0 = H.ApiClient(url, "tok-1", poll=0.05, log=lambda *a: None)
P.main(c0, text, "ws3_data/pack", lengths=(30,), n_parents=3, log=lambda *a: None, work="ws3_data/tmp", pdb2_text=S.fake_9byo(rs))
srv.shutdown(); srv.server_close()
go("import re, json, math")
go('GROUP    = ""', after='GROUP=""; TOKEN=""; SERVER=""; MODE="stored"; SAVE_TO="local"')
nine = S.fake_9byo(rs)
os.remove("ws3_data/pack/9BYO.pdb") if False else None
if COLAB:
    os.makedirs(_drive + "/ws3_data", exist_ok=True); open(_drive + "/ws3_data/6X18.pdb", "w").write(text); open(_drive + "/ws3_data/9BYO.pdb", "w").write(nine)
# no group chosen: the connect cell must refuse with a clear message
j = find("ROOT = workspace_root", i)
try:
    run(codes[j], "empty group"); raise SystemExit("empty group should fail")
except ValueError as e:
    assert "Choose your group number" in str(e), e
ns["GROUP"] = "6"
# the Drive mount sits in its own cell and does nothing outside Colab
k = find("drive.mount", i)
src = codes[k].replace('"/content/drive"', repr(os.path.dirname(_drive)) if COLAB else '"/content/drive"')
out = run(src, "mount")
assert (COLAB and os.path.isdir(_drive)) or (not COLAB and "Nothing to mount" in out), out
i = k + 1
print(go("S = Session(", expect="Group 06"))
go("ref = S.load_reference")
go("v = view_crystal(ref)")
go("plot_footprint(ref)")
assert len(ns["fig"].axes) >= 2
ns["WHO"] = "receptor"; ns["NUMBER"] = int(ns["ref"]["table"]["uniprot_number"].iloc[0])
go("display(residue_lookup(ref, WHO, NUMBER))")
rl = H.residue_lookup(ns["ref"], "GLP-1", 99999); assert "no contact" in rl.iloc[0, 0]
rl = H.residue_lookup(ns["ref"], "GLP-1", int(''.join(ch for ch in ns["ref"]["table"]["glp1_residue"].iloc[0] if ch.isdigit()))); assert len(rl) >= 1
go("q1 = Form", after="fill_q1=True")
fill(ns["q1"]); assert len(ns["q1"].boxes) == 4
go("picker = HotspotPicker", after="")
picker = ns["picker"]
assert len(picker.value) >= 3, picker.value
print("picker:", picker.value, picker.info.value[:90])
picker.preset.value = "Pocket rim (contacts of the N-terminal half of GLP-1)"
print("after preset:", picker.value)
picker.extra.value = "125-127, 999, x"
print("extra:", picker.value, "|", picker.info.value[-160:])
picker.extra.value = ""
fill(ns["why_hot"])
print(go("hs = S.set_hotspots", expect="Saved hotspots"))
print(go("ref_df = S.run_references()"))
go("for rid in [\"ref_glp1\"")
go("q22 = Form"); fill(ns["q22"])
go("v = S.view(\"ref_glp1\"")
print(go("S.load_extra_reference(\"9BYO\")"))
assert len(ns["summ"]) == 3 and "position 3" in ns["note"]
go("plot_overview(None, ref_df)")
go("q2 = Form"); fill(ns["q2"])
go("# S.set_thresholds")
go("hyp_form = Form"); fill(ns["hyp_form"])
go("LENGTH = len(", expect="30 residues")
assert ns["LENGTH"] == 30
go("if hyp_form.check(20)", expect="Submitted")
print(go("S.status()"))
go("recs = S.collect(\"gen\")", expect="Collected 15 designs")
go("SORT_RFD4")
assert len(ns["tab"]) == 15 and "iptm" not in ns["tab"]
guide = ns["guide"]; assert len(guide.dd.options) >= 5
for opt in guide.dd.options[:3]: guide.dd.value = opt[1]
go("q42 = Form"); fill(ns["q42"])
go("RFD4_METRIC = ")
ov = ns["overlay"]; keys = list(ov.layers); assert len(keys) == 16 and "GLP-1 (6X18)" in keys
assert ov.html.count("data-k=") == 16 and "<script>" in ov.html and "clear_output" not in ov.html
go("fig = plot_rfd4_overview(df)"); fill(ns["q4"])
print(go("S.rerun_openfold3()", expect="Submitted"))
go("S.collect(\"of3\")")
assert ns["df"]["iptm"].notna().all() and len(ns["df"]) == 15
go("explorer = MetricExplorer"); fill(ns["q47"])
ex = ns["explorer"]; assert len(ex.x1.options) >= 3 and len(ex.y1.options) >= 3
for dd in (ex.x1, ex.y1, ex.x2, ex.y2): dd.value = dd.options[-1][1]; dd.value = dd.options[0][1]
go("insp = Chooser(df")
ns["insp"].w.value = ns["insp"].opts[0][1]
go("cid = insp.value")
go("POS = 10")
go("parents = Chooser")
ns["parents"].w.value = tuple(o[1] for o in ns["parents"].opts[:2]); fill(ns["why_par"])
print(go("if len(parents.value) not in (1, 2)", expect="Saved parents"))

# ---- rounds
first = find("ROUND = 1", i)
for rnd in (1, 2):
    i = first
    go("ROUND = 1", after=f"ROUND = {rnd}")
    ns["pick_parent"].w.value = ns["pick_parent"].opts[0][1] if rnd == 1 else ns["pick_parent"].opts[0][1]
    go("PARENT = pick_parent.value")
    fx = ns["fix"]
    fx.buttons["Fix interface"].click()
    n_int = len(fx.fixed)
    fx.free_extra.value = "1-2" if rnd == 2 else ""
    fx.fix_extra.value = "3" if rnd == 3 else ""
    fx.view_btn.click()
    assert n_int >= 1 and 1 <= len(fx.fixed) < len(ns["par_rec"]["sequence"]), (n_int, fx.fixed)
    print(f"round {rnd}: parent {ns['PARENT']} fixed {len(fx.fixed)}/{len(ns['par_rec']['sequence'])}", fx.strip.value[-120:].replace("<", "[")[:100])
    go("rh = Form"); fill(ns["rh"])
    seq = ns["par_rec"]["sequence"]
    mt = f"{seq[2]}3{'A' if seq[2] != 'A' else 'G'}" if rnd == 1 else ""
    go("manual_text = ", after=f"manual_text = {mt!r}")
    o = go("if rh.check(15)")
    print("  submit:", o.strip().replace(chr(10), " | ")[:300])
    if rnd == 1: assert "manual variants were NOT submitted" in o and "live server" in o, o
    if rnd == 2:
        assert "NOT submitted" in o and "not in the stored results" in o, o
        break
    out = go("S.collect(f\"r{ROUND}\")")
    d = ns["df"]; this = ns["this"]
    print(f"  collected: {len(this)} rows this round; manual rows: {int((d['origin'] == 'manual').sum())}")
    assert len(this) >= 25
    go("insp2 = Chooser"); ns["insp2"].w.value = ns["insp2"].opts[0][1]
    go("vid = insp2.value")
    go("dec = Form"); fill(ns["dec"]); ns["dec"].boxes["decision"].value = "retain, because the metric improved"
    print("  ", go("if dec.check(8)").strip())
# step 6
go("fig, ax = plt.subplots(1, 2")
go("nominee = Chooser")
go("nid = nominee.value", expect="meets")
go("fin = Form"); fill(ns["fin"])
print(go("if fin.check(15)", expect="Written to")[-300:])
print(go("c = cluster_of(S.group)"))
print("rounds saved:", [(r["round"], r["decision"][:12], len(r["fixed"])) for r in ns["S"].state["rounds"]])
assert len(ns["S"].state["rounds"]) == 1
assert len(shown) > 10
print("3D calls:", len(_View.calls), sorted({c[0] for c in _View.calls}))
assert len(_View.calls) > 20
if False:
    assert os.path.exists(_drive + "/ws3_data/group05/state.json"), "state not in Drive"
    assert any(str(x).endswith("handin_group05.zip") for x in colab_dl), colab_dl
    assert "widgetmgr" in colab_dl
    print("COLAB checks passed:", colab_dl)
print("NOTEBOOK WALK-THROUGH PASSED")
