"""Mock of the assumed workshop API (RFD4-Proteina generate, ProteinMPNN redesign, OpenFold3 predict). For tests and rehearsal."""
import json, threading, time, hashlib, re, io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import numpy as np
import ws3_helpers as H
import synth as S

EXPECT_Q = {"strong": 0.85, "moderate": 0.6, "weak": 0.38, "none": 0.08}


class Mock:
    def __init__(self, ref_text, ref_seq, delay=0.4, tokens=None, max_running=3):
        self.text, self.rs = ref_text, ref_seq
        self.ref = H.build_reference(ref_text)
        self.delay, self.tokens, self.max_running = delay, tokens or {"tok-1": "g1", "tok-2": "g2"}, max_running
        self.jobs, self.results, self.cache, self.reg = {}, {}, {}, {}
        self.files = {}
        self.lock = threading.Lock()
        self.fail_next = 0           # >0: the next job fails
        self.n_requests = 0
        self.refs = {r["id"]: r for r in H.reference_list(self.ref)}

    # ---- science stand-ins
    def _hot_x(self, hotspots):
        nums = [int(h.split(":")[1]) for h in hotspots] or [100]
        return 1.5 * (np.mean(nums) - S.REC_NUM0) - 8 + 8

    def _record(self, did, seq, q, hot_x, origin, rnd, parent):
        des = S.make_design(self.rs, seq, q, hot_x=hot_x, seed=int(hashlib.md5(did.encode()).hexdigest()[:6], 16))
        self.reg[did] = dict(seq=seq, q=q, hot_x=hot_x, atoms=des, origin=origin, round=rnd, parent=parent)

    def generate(self, p, fp):
        rng = np.random.default_rng(int(fp[:8], 16))
        hx = self._hot_x(p["hotspots"]); L = int(p["binder_length"])
        out = {}
        for i in range(1, int(p["n_designs"]) + 1):
            did = f"d{fp[:6]}_{i:02d}"
            seq = "".join(rng.choice(list("AAEEEKKLLLIVFWYSTRDQNG"), L))
            q = float(np.clip(rng.beta(2.2, 2.4), 0.05, 0.95))
            self._record(did, seq, q, hx, "rfd4", 0, None)
            out[did] = dict(sequence=seq, origin="rfd4", round=0, parent=None, art=["design"], metrics=self._rfd4_metrics(did, q, rng))
        return out

    def _rfd4_metrics(self, did, q, rng):
        """Stand-in with the same shape as the real server's metrics: one flat dict with dotted names (values are made up)."""
        n = lambda x, k=4: round(float(x), k)
        return {"amino_acid_composition.n_standard_residues": 396, "amino_acid_composition.ala_fraction": n(0.06 + rng.normal(0, 0.01)),
                "bond_length_metrics.bond_length.frac_unreasonable": n(max(0, 0.002 * (1 - q) + rng.normal(0, 0.0003))),
                "clash_metrics.frac_atoms_clashing_1p5A": n(max(0, 0.003 * (1 - q) + rng.normal(0, 0.0004))),
                "hotspot_obedience.hotspot_obedience": n(np.clip(0.2 + 0.7 * q + rng.normal(0, 0.1), 0, 1), 3),
                "interchain_interactions.hbond_atom_pair_count_coi": int(max(0, round(8 * q + rng.normal(0, 3)))),
                "interchain_interactions.saltbridge_residue_pair_count_coi": int(max(0, round(2 * q + rng.normal(0, 1)))),
                "interchain_interactions.pistack_residue_pair_count_coi": int(max(0, round(q + rng.normal(0, 1)))),
                "interchain_interactions.pication_residue_pair_count_coi": int(max(0, round(q + rng.normal(0, 1)))),
                "interchain_interactions.hydrophobic_atom_pair_count_coi": int(max(0, round(20 * q + rng.normal(0, 5)))),
                "sequence_adherence.sequence_adherence": 1, "sse_distribution.helix_fraction_coi": n(np.clip(0.5 + rng.normal(0, 0.2), 0, 1), 3),
                "pre_oracle_pass": int(q > 0.3)}

    def redesign(self, p, fp):
        rng = np.random.default_rng(int(fp[:8], 16))
        par = self.reg[p["parent_id"]]
        fixed = set(p["fixed_positions"]); T = float(p["temperature"])
        out = {}
        for i in range(1, int(p["n_sequences"]) + 1):
            did = f"m{fp[:6]}_{i:02d}"
            seq = list(par["seq"])
            for k in range(len(seq)):
                if (k + 1) not in fixed and rng.random() < 0.35 + T:
                    seq[k] = str(rng.choice(list("AEKLIVFWYSTRDQ")))
            nfree = len(seq) - len(fixed)
            q = float(np.clip(par["q"] + rng.normal(0.02, 0.10) - 0.1 * (nfree / len(seq)) * 0, 0.03, 0.97))
            self._record(did, "".join(seq), q, par["hot_x"], "mpnn", int(p.get("round") or 1), p["parent_id"])
            out[did] = dict(sequence="".join(seq), origin="mpnn", round=int(p.get("round") or 1), parent=p["parent_id"], art=["design", "model", "confidence", "pae"])
            self._pred_files(fp, did)
        return out

    def predict(self, p, fp):
        out = {}
        for d in p["designs"]:
            did, seq = d["id"], d["sequence"]
            if did in self.refs:
                r = self.refs[did]
                q = EXPECT_Q[r["expected"]]
                if did not in self.reg or self.reg[did]["seq"] != seq:
                    self._record(did, seq, q, 100.0, "reference", 0, None)
            elif did not in self.reg and d.get("parent_id") in self.reg:
                par = self.reg[d["parent_id"]]
                nmut = sum(a != b for a, b in zip(par["seq"], seq))
                self._record(did, seq, float(np.clip(par["q"] - 0.04 * nmut + 0.02, 0.03, 0.97)), par["hot_x"], "manual", 0, d["parent_id"])
            elif did not in self.reg:
                raise KeyError(f"unknown design {did}")
            e = self.reg[did]
            self._pred_files(fp, did)
            out[did] = dict(sequence=e["seq"], origin=e["origin"], round=e["round"], parent=e["parent"], art=["model", "confidence", "pae"])
        return out

    def _pred_files(self, fp, did):
        e = self.reg[did]
        mod, conf, pae = S.make_prediction(e["atoms"], self.rs, e["seq"], e["q"], seed=int(hashlib.md5(did.encode()).hexdigest()[:6], 16))
        self.files[f"{fp}/{did}/model.pdb"] = H.atoms_to_pdb(mod).encode()
        self.files[f"{fp}/{did}/confidence.json"] = json.dumps(conf).encode()
        self.files[f"{fp}/{did}/pae.npz"] = S.npz_bytes(pae)

    # ---- job machinery
    def submit(self, task, p, token):
        with self.lock:
            group = self.tokens.get(token)
            if group is None:
                return 401, {"detail": "bad token"}
            running = [j for j in self.jobs.values() if j["group"] == group and time.time() < j["ready_at"]]
            if len(running) >= self.max_running:
                return 429, {"detail": "too many jobs"}
            fp = H.request_fingerprint(task, p)
            mode, dur = "live", self.delay
            if fp in self.cache:
                mode, dur = "cache", 0.0
            jid = f"j{len(self.jobs) + 1:04d}"
            fail = self.fail_next > 0
            if fail:
                self.fail_next -= 1
            self.jobs[jid] = dict(task=task, payload=p, fp=fp, group=group, mode=mode, ready_at=time.time() + (0 if fail else dur), fail=fail, t0=time.time())
            return 200, {"job_id": jid, "status": "queued"}

    def status(self, jid):
        j = self.jobs.get(jid)
        if not j:
            return 404, {"detail": "no such job"}
        if j["fail"]:
            return 200, {"job_id": jid, "status": "failed", "message": "GPU out of memory (mock)"}
        if time.time() < j["ready_at"]:
            st = "queued" if time.time() - j["t0"] < j["ready_at"] - j["t0"] / 2 else "running"
            return 200, {"job_id": jid, "status": st, "queue_position": 2 if st == "queued" else None, "execution_mode": j["mode"]}
        with self.lock:
            if j["fp"] not in self.cache:
                fn = getattr(self, j["task"])
                try:
                    self.cache[j["fp"]] = fn(j["payload"], j["fp"])
                except KeyError as e:
                    return 200, {"job_id": jid, "status": "failed", "message": str(e)}
                for did, d in self.cache[j["fp"]].items():
                    if "design" in d["art"]:
                        self.files[f"{j['fp']}/{did}/design.pdb"] = H.atoms_to_pdb(self.reg[did]["atoms"]).encode()
        return 200, {"job_id": jid, "status": "succeeded", "result_id": j["fp"], "execution_mode": j["mode"]}

    def result(self, rid, prefix):
        if rid not in self.cache:
            return 404, {"detail": "no such result"}
        j = next((x for x in self.jobs.values() if x["fp"] == rid), None)
        designs = {}
        for did, d in self.cache[rid].items():
            designs[did] = dict(sequence=d["sequence"], origin=d["origin"], round=d["round"], parent=d["parent"],
                                artifacts={k: f"{prefix}/files/{rid}/{did}/{ART_FILE[k]}" for k in d["art"]})
            if d.get("metrics"):
                designs[did]["metrics"] = d["metrics"]
        return 200, dict(result_id=rid, model_version="mock-0.1", designs=designs)


ART_FILE = {"design": "design.pdb", "model": "model.pdb", "confidence": "confidence.json", "pae": "pae.npz"}


def serve(mock, prefix="/api", port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def _send(self, code, obj=None, raw=None):
            body = raw if raw is not None else json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/octet-stream" if raw is not None else "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body)

        def _tok(self):
            a = self.headers.get("Authorization", "")
            return a[7:] if a.startswith("Bearer ") else ""

        def do_GET(self):
            mock.n_requests += 1
            path = self.path
            if not path.startswith(prefix):
                return self._send(404, {"detail": "no"})
            path = path[len(prefix):]
            if path == "/health":
                return self._send(200, {"status": "ok", "models": {"rfd4_proteina": "mock", "proteinmpnn": "mock", "openfold3": "mock"}})
            if self._tok() not in mock.tokens:
                return self._send(401, {"detail": "bad token"})
            if path.startswith("/jobs/"):
                c, o = mock.status(path[6:]); return self._send(c, o)
            if path.startswith("/results/"):
                c, o = mock.result(path[9:], prefix); return self._send(c, o)
            if path.startswith("/files/"):
                k = path[7:]
                if k in mock.files: return self._send(200, raw=mock.files[k])
                return self._send(404, {"detail": "no file"})
            return self._send(404, {"detail": "no"})

        def do_POST(self):
            mock.n_requests += 1
            n = int(self.headers.get("Content-Length", 0))
            p = json.loads(self.rfile.read(n) or b"{}")
            m = re.fullmatch(prefix + r"/jobs/(generate|redesign|predict)", self.path)
            if not m:
                return self._send(404, {"detail": "no"})
            c, o = mock.submit(m.group(1), p, self._tok())
            return self._send(c, o)

    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}{prefix}"
