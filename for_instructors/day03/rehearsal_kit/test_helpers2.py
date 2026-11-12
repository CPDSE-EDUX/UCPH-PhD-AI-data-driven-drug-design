import sys, tempfile, json, os
import numpy as np
sys.path.insert(0, "/home/claude/nb2")
import ws3_helpers as H
import synth as S

text, rs = S.fake_6x18()
ref = H.build_reference(text)
print("chains", ref["rec_chain"], ref["pep_chain"], "other", ref["other_chains"], "pep", ref["pep_seq"], "rec len", len(ref["rec"]["res"]))
assert (ref["rec_chain"], ref["pep_chain"]) == ("R", "P")
print(ref["table"].head(8).to_string())
print("footprint", sorted(ref["footprint"]))
for k, v in ref["presets"].items(): print(k, v)
assert len(ref["footprint"]) > 5
assert ref["table"]["interactions"].str.len().gt(0).any(), "no interaction kinds found"

# crystal as design
cd = H.crystal_as_design(ref)
a = H.parse_pdb(cd)
assert {x[0] for x in a} == {"R", "B"}, {x[0] for x in a}
print("crystal as design residues", len(H.get_chain(a, "B")["res"]))

# scoring a good, mid and bad design through the pipeline
hot = ref["presets"]["Whole footprint (strongest contacts overall)"]
rows = []
for name, q, seq in (("good", 1.0, H.GLP1_SEQ), ("mid", 0.6, H.GLP1_SEQ), ("bad", 0.1, H.GLP1_SEQ)):
    des = S.make_design(rs, seq, q, hot_x=100, seed=1)
    mod, conf, pae = S.make_prediction(des, rs, seq, q, seed=2)
    r = H.score_prediction(H.atoms_to_pdb(mod), conf, pae, ref, hot, H.atoms_to_pdb(des))
    rows.append((name, r)); print(name, {k: r[k] for k in ("iptm", "binder_plddt", "iface_pae", "ipsae", "backbone_rmsd", "pose_rmsd", "hotspot_hits", "hotspot_frac", "site_overlap", "site_cover", "n_clash", "min_dist")})
    print("   checks", H.evidence_checks(r))
g, m, b = (r for _, r in rows)
assert g["iface_pae"] < b["iface_pae"] and g["ipsae"] > b["ipsae"]
assert g["hotspot_hits"] >= b["hotspot_hits"]

# missing files stay NaN, not zero
r = H.score_prediction(H.atoms_to_pdb(mod), {}, None, ref, hot, None)
assert np.isnan(r["iptm"]) and np.isnan(r["iface_pae"]) and np.isnan(r["backbone_rmsd"]), r
p, t, d = H.evidence_checks(r); print("missing metrics evaluate:", p, t, d)

# fingerprint stability
pl = dict(target_id=H.TARGET_ID, seed=H.SEED, n_designs=25, binder_length=60, hotspots=["R:100", "R:90"])
f1 = H.request_fingerprint("generate", pl)
pl2 = dict(pl, hotspots=["R:90", "R:100"], extra="x")
assert f1 == H.request_fingerprint("generate", pl2)
assert f1 != H.request_fingerprint("generate", dict(pl, binder_length=80))
print("fingerprint", f1)

# residue classes
cl = H.residue_classes(H.atoms_to_pdb(S.make_design(rs, "A" * 60, 1.0, 100, 1)))
from collections import Counter
print(Counter(c["cls"] for c in cl))

# parse_ranges
assert H.parse_ranges("5-8, 12") == [5, 6, 7, 8, 12]
assert H.parse_ranges("5-8, 12", 6, 10) == [6, 7, 8]
try: H.parse_ranges("a-b"); raise SystemExit("should fail")
except ValueError: pass

# cif reader on a tiny file
cif = """data_x
loop_
_atom_site.group_PDB
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.auth_asym_id
_atom_site.auth_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.B_iso_or_equiv
_atom_site.pdbx_PDB_model_num
ATOM C CA . ALA R 10 ? 1.0 2.0 3.0 50.0 1
ATOM C CB . ALA R 10 ? 1.0 2.0 4.0 50.0 1
HETATM O O . HOH R 99 ? 1.0 2.0 4.0 50.0 1
ATOM C CA . GLY R 11 ? 4.0 2.0 3.0 50.0 2
#
"""
ca = H.parse_cif(cif); assert len(ca) == 2 and ca[0][3] == "ALA", ca
assert len(H.load_structure(cif)) == 2

# scramble, props, liabilities, scrambled differs
sc = H.scramble(H.GLP1_SEQ); assert sc != H.GLP1_SEQ and sorted(sc) == sorted(H.GLP1_SEQ)
print(H.props(H.GLP1_SEQ), H.liabilities("MNGDGCAAAAAAAK"))
refs = H.reference_list(ref); print([(r["id"], len(r["seq"])) for r in refs])
print("ALL HELPER TESTS PASSED")
