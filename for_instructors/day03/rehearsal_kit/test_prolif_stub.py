"""Plumbing test for the ProLIF code path with stand-ins for rdkit and prolif (the real packages are not installed in the sandbox).
It checks the PDB block, the index to coordinate mapping and the merge into contact_detail. It does NOT test ProLIF itself."""
import sys, types, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

class Info:
    def __init__(s, rn, an, num): s.rn, s.an, s.num = rn, an, num
    def GetResidueName(s): return s.rn
    def GetName(s): return s.an
    def GetResidueNumber(s): return s.num
class Atom:
    def __init__(s, idx, mol, info, xyz): s.idx, s.mol, s.info, s.xyz, s.charge, s.parent = idx, mol, info, xyz, 0, 0
    def GetPDBResidueInfo(s): return s.info
    def SetFormalCharge(s, c): s.charge = c
    def GetBonds(s): return []
    def GetIdx(s): return s.idx
    def GetNeighbors(s): return [s.mol.atoms[s.parent]]
class Mol:
    def __init__(s): s.atoms = []
    def GetNumAtoms(s): return len(s.atoms)
    def GetAtoms(s): return iter(s.atoms)
    def GetAtomWithIdx(s, i): return s.atoms[i]
class BT: DOUBLE = "D"
chem = types.ModuleType("rdkit.Chem"); chem.BondType = BT
def MolFromPDBBlock(block, sanitize=True, removeHs=False):
    m = Mol()
    for ln in block.splitlines():
        if ln.startswith("ATOM"):
            m.atoms.append(Atom(len(m.atoms), m, Info(ln[17:20], ln[12:16], int(ln[22:26])), np.array([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])))
    return m
chem.MolFromPDBBlock = MolFromPDBBlock
chem.SanitizeMol = lambda m: None
def AddHs(m, addCoords=False, addResidueInfo=False):
    for k in range(3): m.atoms.append(Atom(len(m.atoms), m, Info("HOH", "H", 1), m.atoms[0].xyz))
    return m
chem.AddHs = AddHs
rd = types.ModuleType("rdkit"); rd.Chem = chem; sys.modules["rdkit"] = rd; sys.modules["rdkit.Chem"] = chem
class RID:
    def __init__(s, n): s.number = n
pl = types.ModuleType("prolif"); pl.__version__ = "0.0-stub"
pl.Molecule = lambda m: m
class FP:
    def __init__(s, names, count=True): s.names = names
    def generate(s, lig, prot, metadata=True):
        # report the closest heavy-atom pair as an H-bond (ligand donor with a hydrogen index at the end, protein acceptor)
        nl = sum(1 for a in lig.atoms if a.info.an.strip()[0] != "H") - 3
        nl = len(lig.atoms) - 3; npr = len(prot.atoms) - 3
        best = min(((np.linalg.norm(lig.atoms[i].xyz - prot.atoms[j].xyz), i, j) for i in range(nl) for j in range(npr)))
        d, i, j = best
        lig.atoms[nl + 1].parent = i
        return {(RID(lig.atoms[i].info.num), RID(prot.atoms[j].info.num)): {"HBDonor": [dict(parent_indices=dict(ligand=(i, nl + 1), protein=(j,)), distance=d)]}}
pl.Fingerprint = FP
sys.modules["prolif"] = pl

import ws3_helpers as H, synth as S
text, rs = S.fake_6x18()
ref = H.build_reference(text)
assert ref["interaction_engine"].startswith("ProLIF 0.0-stub"), ref["interaction_engine"]
# every residue pair has at most the one stub interaction, it is an H-bond, and the line ends sit on real heavy atoms
rec, pep = ref["rec"], ref["pep"]
cd = H.contact_detail(rec, pep, 4.5, interactions=True)
assert len(cd) >= 1
for key, e in cd.items():
    assert e["kinds"] <= {"H-bond"}, e["kinds"]
n_hb = sum(e["kc"].get("H-bond", 0) for e in cd.values())
assert n_hb == 1, n_hb
(k, e), = [(k, e) for k, e in cd.items() if e["kc"].get("H-bond")]
d, xa, xb = e["best"]["H-bond"]
assert any(np.allclose(xa, p) for p in rec["xyz"]) and any(np.allclose(xb, p) for p in pep["xyz"])
assert abs(d - np.linalg.norm(np.array(xa) - np.array(xb))) < 1e-6
# heat maps are filled from the stub result
assert ref["heat_pep"][KIND := H.KIND_ROWS.index("H-bond")].sum() == 1 and ref["heat_rec"][KIND].sum() == 1
# lines for the 3D view
ln = H.interaction_lines(rec, pep)
assert len(ln) == 1 and ln[0]["kind"] == "H-bond"
# the cache returns the same object, and a failing ProLIF falls back to the distance rules
assert H.prolif_pairs(rec, pep) is H.prolif_pairs(rec, pep)
H._PL_CACHE.clear(); pl.Fingerprint = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
cd2 = H.contact_detail(rec, pep, 4.5, interactions=True)
assert H.interaction_engine() == "simple distance rules" and H.PROLIF_STATE["error"].startswith("RuntimeError")
assert any(e["kinds"] for e in cd2.values())
print("PROLIF PLUMBING TEST PASSED")
