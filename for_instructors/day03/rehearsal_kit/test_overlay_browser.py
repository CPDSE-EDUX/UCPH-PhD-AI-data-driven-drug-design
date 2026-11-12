"""Cell 4.3: the overlay is ONE html block; switching designs on and off is done by the page. Headless Chromium with a stand-in for 3Dmol
(the real 3Dmol cannot be downloaded in the sandbox): checks that the viewer is created once and that the styles per chain follow the check boxes."""
import sys, os, tempfile, types, json
sys.path.insert(0, "/home/claude/nb2")
os.environ["MPLBACKEND"] = "Agg"
class _View:
    def __init__(self, **k): pass
    def __getattr__(self, n): return lambda *a, **k: None
pm = types.ModuleType("py3Dmol"); pm.view = _View; sys.modules["py3Dmol"] = pm
shown = []
ip = types.ModuleType("IPython"); ipd = types.ModuleType("IPython.display")
ipd.display = lambda x: shown.append(x); ipd.HTML = lambda s: s
ip.display = ipd; sys.modules["IPython"] = ip; sys.modules["IPython.display"] = ipd
import ws3_helpers as H, synth as S, mock_server as M
from playwright.sync_api import sync_playwright

text, rs = S.fake_6x18(uniprot_offset=7)
mock = M.Mock(text, rs, delay=0.2); srv, url = M.serve(mock)
os.chdir(tempfile.mkdtemp()); os.makedirs("ws3_data"); open("ws3_data/6X18.pdb", "w").write(text)
s = H.Session("3", "tok-1", url, "server", log=lambda *a: None)
ref = s.load_reference(); s.set_hotspots(ref["presets"][list(ref["presets"])[0]], "x")
s.submit("gen", "generate", dict(n_designs=15, binder_length=30, hotspots=s.hotspots)); s.collect("gen", origin="rfd4")
ov = H.OverlayViewer(s)
assert len(shown) == 1 and "<script>" in shown[0] and shown[0].count("data-k=") == 16 and shown[0].count("data-only=") == 16
html = shown[0]
assert "clear_output" not in html and "py3Dmol" not in html

STUB = """
window.__calls = {create: 0, addModel: 0, render: 0};
window.__style = {};
window.$3Dmol = {createViewer: function(el, o){ window.__calls.create++;
  var viewer = {
    addModel: function(){ window.__calls.addModel++; },
    setStyle: function(sel, st){ if(sel.chain && !sel.resi && !sel.atom){ window.__style[sel.chain] = JSON.stringify(st); } },
    addStyle: function(sel, st){ },
    addCylinder: function(){}, addLabel: function(){}, zoomTo: function(){}, setHoverable: function(){},
    render: function(){ window.__calls.render++; }
  };
  return viewer; }};
window.$3Dmolpromise = Promise.resolve();
"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(STUB)
    page_html = "<!doctype html><html><body>" + html + "</body></html>"
    pg.route("http://t.local/**", lambda r: r.fulfill(body=page_html, content_type="text/html"))
    pg.goto("http://t.local/x"); pg.wait_for_timeout(300)
    on = lambda: sorted(k for k, v in pg.evaluate("window.__style").items() if v != "{}" and k != "R")
    allch = sorted(pg.evaluate("window.__style").keys()); assert len(allch) == 17 and "R" in allch, allch
    assert len(on()) == 16 and pg.evaluate("window.__calls.create") == 1 and pg.evaluate("window.__calls.addModel") == 1
    boxes = pg.query_selector_all("input[data-k]"); assert len(boxes) == 16
    boxes[2].click(); pg.wait_for_timeout(50)
    assert len(on()) == 15 and "D" not in on(), on()
    boxes[2].click(); assert len(on()) == 16
    pg.click("a[data-only='5']"); pg.wait_for_timeout(50)
    assert on() == ["G"], on()
    assert [bx.is_checked() for bx in pg.query_selector_all("input[data-k]")].count(True) == 1
    pg.click("button:has-text('Show none')"); assert on() == []
    pg.click("button:has-text('Show all')"); assert len(on()) == 16
    for _ in range(20): boxes[1].click(); boxes[3].click()
    assert pg.evaluate("window.__calls.create") == 1 and pg.evaluate("window.__calls.addModel") == 1      # never rebuilt
    assert not errs, errs
    # the loader: no 3Dmol present and the script cannot be downloaded -> readable message, no exception
    pg2 = b.new_page(); errs2 = []; pg2.on("pageerror", lambda e: errs2.append(str(e)))
    pg2.route("**/*", lambda r: r.fulfill(body=page_html, content_type="text/html") if r.request.url.startswith("http://t.local") else r.abort())
    pg2.goto("http://t.local/x"); pg2.wait_for_timeout(800)
    msg = pg2.inner_text("#" + html.split("id='")[1].split("'")[0] + "v")
    assert "could not be loaded" in msg, msg
    b.close()
print("test_overlay_browser OK")
