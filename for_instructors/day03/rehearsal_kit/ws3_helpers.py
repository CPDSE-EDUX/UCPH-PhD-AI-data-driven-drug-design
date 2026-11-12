import re, json, math, random, difflib, datetime, hashlib, io, base64, time, os, sys, shutil
import urllib.request, urllib.error, urllib.parse
import uuid
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd

# =====================================================================================
#  Constants
# =====================================================================================
TARGET_ID = "glp1r-6x18"
SEED = 2026                      # base seed. A group uses SEED + its group number (reproducible per group); the reference peptides and the stored-results pack use SEED itself
REC, BIND = "R", "B"             # chain ids in every file the server returns (receptor keeps the 6X18 residue numbers)
N_DESIGNS, N_VARIANTS, MAX_ROUNDS = 15, 25, 3
N_GROUPS = 10

AA = "ACDEFGHIKLMNPQRSTVWY"
THREE2ONE = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G",
             "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S",
             "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "MSE": "M"}
ONE2THREE = {v: k for k, v in THREE2ONE.items() if k != "MSE"}
RES_MASS = {"A": 71.0788, "R": 156.1875, "N": 114.1038, "D": 115.0886, "C": 103.1388, "E": 129.1155, "Q": 128.1307,
            "G": 57.0519, "H": 137.1411, "I": 113.1594, "L": 113.1594, "K": 128.1741, "M": 131.1926, "F": 147.1766,
            "P": 97.1167, "S": 87.0782, "T": 101.1051, "W": 186.2132, "Y": 163.1760, "V": 99.1326}

GLP1_SEQ = "HAEGTFTSDVSSYLEGQAAKEFIAWLVKGR"          # GLP-1(7-36)
REFERENCES = [   # expected class = what the literature says about binding to GLP-1R (approximate, not measured by us)
    dict(id="ref_glp1", label="GLP-1(7-36)", seq=None, expected="strong", note="the native ligand in 6X18"),
    dict(id="ref_exendin4", label="Exendin-4", seq="HGEGTFTSDLSKQMEEEAVRLFIEWLKNGGPSSGAPPPS", expected="strong", note="agonist from Gila monster"),
    dict(id="ref_oxm", label="Oxyntomodulin", seq="HSQGTFTSDYSKYLDSRRAQDFVQWLMNTKRNRNNIA", expected="moderate", note="weaker agonist"),
    dict(id="ref_glucagon", label="Glucagon", seq="HSQGTFTSDYSKYLDSRRAQDFVQWLMNT", expected="weak", note="mainly a glucagon-receptor ligand"),
    dict(id="ctrl_scrambled", label="GLP-1 scrambled", seq=None, expected="none", note="negative control: same letters, shuffled (fixed seed)"),
]
EXPECT_ORDER = {"strong": 0, "moderate": 1, "weak": 2, "none": 3}

THRESHOLDS = dict(   # teaching thresholds: a starting point, to be judged against the reference peptides
    iptm=0.60, binder_plddt=80.0, iface_pae=10.0, backbone_rmsd=2.0, pose_rmsd=3.0, hotspot_frac=0.5, min_dist=2.5)
CHECKS = [("iptm", "ipTM", ">="), ("binder_plddt", "binder pLDDT", ">="), ("iface_pae", "interface PAE", "<="),
          ("backbone_rmsd", "backbone RMSD", "<="), ("pose_rmsd", "pose RMSD", "<="), ("hotspot_frac", "hotspots touched", ">=")]


# =====================================================================================
#  Sequences
# =====================================================================================
def scramble(seq, seed=7):
    letters = list(seq)
    for k in range(200):
        random.Random(seed + k).shuffle(letters)
        if "".join(letters) != seq:
            break
    return "".join(letters)


def props(seq):
    mass = sum(RES_MASS.get(a, 0) for a in seq) + 18.0153
    charge = seq.count("K") + seq.count("R") - seq.count("D") - seq.count("E") + 0.1 * seq.count("H")
    return dict(length=len(seq), mass_Da=round(mass, 1), net_charge=round(charge, 1))


def liabilities(seq):
    """Simple sequence-liability scan for a miniprotein. Returns short flags."""
    f = []
    if "NG" in seq: f.append("Asn-Gly (deamidation)")
    if "DG" in seq: f.append("Asp-Gly (isomerisation)")
    if "C" in seq: f.append("Cys (check pairing)")
    if "M" in seq: f.append("Met (oxidation)")
    if re.search(r"N[^P][ST]", seq): f.append("N-glycosylation motif")
    if re.search(r"[VILMFWC]{6,}", seq): f.append("hydrophobic stretch of 6 or more")
    q = props(seq)["net_charge"]
    if abs(q) > 8: f.append(f"net charge {q:+.1f}")
    return f


def identity(a, b):
    n = min(len(a), len(b))
    return sum(x == y for x, y in zip(a, b)) / max(1, n)


def parse_ranges(text, lo=1, hi=10**6):
    """'5-12, 40' -> [5..12, 40] (values clipped to lo..hi). Raises ValueError on rubbish."""
    out = set()
    for tok in re.split(r"[,\s;]+", (text or "").strip()):
        if not tok:
            continue
        m = re.fullmatch(r"(?:[A-Za-z]:)?(\d+)(?:-(\d+))?", tok)
        if not m:
            raise ValueError(f"cannot read '{tok}'")
        a = int(m.group(1)); b = int(m.group(2) or a)
        out.update(range(min(a, b), max(a, b) + 1))
    return sorted(x for x in out if lo <= x <= hi)


# =====================================================================================
#  Structures (PDB and mmCIF readers, atoms are tuples: chain, resseq, icode, resname, atom, x, y, z, bfactor)
# =====================================================================================
def parse_pdb(text):
    atoms = []
    for line in text.splitlines():
        rec = line[:6]
        if rec == "ATOM  " or (rec == "HETATM" and line[17:20] in THREE2ONE):
            if line[16] not in " A":
                continue
            name = line[12:16].strip()
            elem = line[76:78].strip() if len(line) >= 78 else name[:1]
            if elem in ("H", "D"):
                continue
            try:
                bf = float(line[60:66])
            except ValueError:
                bf = 0.0
            atoms.append((line[21], int(line[22:26]), line[26].strip(), line[17:20].strip(), name,
                          float(line[30:38]), float(line[38:46]), float(line[46:54]), bf))
    return atoms


def parse_cif(text):
    lines = text.splitlines()
    cols, rows = [], []
    for i, l in enumerate(lines):
        if l.strip() == "loop_" and i + 1 < len(lines) and lines[i + 1].startswith("_atom_site."):
            j = i + 1
            while j < len(lines) and lines[j].startswith("_atom_site."):
                cols.append(lines[j].strip()[len("_atom_site."):]); j += 1
            while j < len(lines) and not lines[j].startswith(("#", "loop_", "_")):
                rows.append(lines[j].split()); j += 1
            break
    ix = {c: k for k, c in enumerate(cols)}
    need = ["group_PDB", "label_atom_id", "label_comp_id", "auth_asym_id", "auth_seq_id", "Cartn_x", "Cartn_y", "Cartn_z"]
    if any(n not in ix for n in need):
        raise ValueError("mmCIF file without the expected _atom_site columns")
    atoms = []
    for r in rows:
        if len(r) < len(cols):
            continue
        if "pdbx_PDB_model_num" in ix and r[ix["pdbx_PDB_model_num"]] != "1":
            continue
        alt = r[ix["label_alt_id"]] if "label_alt_id" in ix else "."
        if alt not in (".", "A", "?"):
            continue
        resn = r[ix["label_comp_id"]]
        if r[ix["group_PDB"]] == "HETATM" and resn not in THREE2ONE:
            continue
        elem = r[ix["type_symbol"]] if "type_symbol" in ix else r[ix["label_atom_id"]][:1]
        if elem in ("H", "D"):
            continue
        ic = r[ix["pdbx_PDB_ins_code"]] if "pdbx_PDB_ins_code" in ix else "?"
        bf = float(r[ix["B_iso_or_equiv"]]) if "B_iso_or_equiv" in ix else 0.0
        atoms.append((r[ix["auth_asym_id"]], int(r[ix["auth_seq_id"]]), "" if ic in "?." else ic, resn,
                      r[ix["label_atom_id"]].strip('"'), float(r[ix["Cartn_x"]]), float(r[ix["Cartn_y"]]),
                      float(r[ix["Cartn_z"]]), bf))
    return atoms


def load_structure(text):
    return parse_cif(text) if text.lstrip().startswith("data_") else parse_pdb(text)


def fetch_rcsb(pdb_id, cache_dir="ws3_data"):
    """Download an entry from RCSB (PDB format first, then mmCIF) and keep a copy. Returns the text."""
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    last = None
    for ext in ("pdb", "cif"):
        p = Path(cache_dir) / f"{pdb_id}.{ext}"
        if p.exists():
            return p.read_text()
        try:
            with urllib.request.urlopen(f"https://files.rcsb.org/download/{pdb_id}.{ext}", timeout=60) as r:
                txt = r.read().decode()
            p.write_text(txt)
            return txt
        except Exception as e:
            last = e
    raise RuntimeError(f"could not download {pdb_id} from RCSB ({last}). Put {pdb_id}.pdb into the folder {cache_dir}/ or ask an instructor.")


def get_chain(atoms, cid):
    res, ri, xyz, name, rname, bf, index = [], [], [], [], [], [], {}
    for a in atoms:
        if a[0] != cid:
            continue
        key = (a[1], a[2])
        if key not in index:
            index[key] = len(res)
            res.append(dict(num=a[1], icode=a[2], aa=THREE2ONE.get(a[3], "X"), resname=a[3]))
        ri.append(index[key]); xyz.append(a[5:8]); name.append(a[4]); rname.append(a[3]); bf.append(a[8])
    return dict(id=cid, res=res, ri=np.array(ri, int), xyz=np.array(xyz, float).reshape(-1, 3),
                name=np.array(name), resname=np.array(rname), bf=np.array(bf, float))


def chain_seq(ch):
    return "".join(r["aa"] for r in ch["res"])


def ca_coords(ch):
    out = np.full((len(ch["res"]), 3), np.nan)
    for k in range(len(ch["res"])):
        m = ch["ri"] == k
        ca = m & (ch["name"] == "CA")
        pts = ch["xyz"][ca] if ca.any() else ch["xyz"][m]
        out[k] = pts.mean(0)
    return out


def res_bfactor(ch):
    return np.array([ch["bf"][ch["ri"] == k].mean() for k in range(len(ch["res"]))])


def dist_matrix(a, b):
    return np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)


POS_ATOMS = {("LYS", "NZ"), ("ARG", "NH1"), ("ARG", "NH2"), ("ARG", "NE")}
NEG_ATOMS = {("ASP", "OD1"), ("ASP", "OD2"), ("GLU", "OE1"), ("GLU", "OE2")}
HYD_RES = {"ALA", "VAL", "ILE", "LEU", "MET", "PHE", "TRP", "TYR", "CYS"}
BACKBONE = {"N", "CA", "C", "O", "OXT"}


AROM_RING = {"PHE": {"CG", "CD1", "CD2", "CE1", "CE2", "CZ"}, "TYR": {"CG", "CD1", "CD2", "CE1", "CE2", "CZ"},
             "TRP": {"CG", "CD1", "CD2", "NE1", "CE2", "CE3", "CZ2", "CZ3", "CH2"}, "HIS": {"CG", "ND1", "CD2", "CE1", "NE2"}}
KIND_ROWS = ["any contact", "aromatic", "H-bond", "ionic"]      # rows of the interaction heat maps


def interaction_kinds(ra, aa, rb, ab, d):
    """Rough interaction labels for one heavy-atom pair (distance rules only, no angles): ionic (opposite charges, up to 4.0 A),
    H-bond (N or O to N or O, up to 3.5 A), hydrophobic (side-chain C to C, up to 4.0 A), aromatic (a ring atom of F, Y, W or H
    within 4.5 A of a side-chain carbon or a positive charge of the other residue)."""
    a, b = (ra, aa), (rb, ab)
    out = []
    if d <= 4.0 and ((a in POS_ATOMS and b in NEG_ATOMS) or (a in NEG_ATOMS and b in POS_ATOMS)):
        out.append("ionic")
    if d <= 3.5 and aa[0] in "NO" and ab[0] in "NO":
        out.append("H-bond")
    if d <= 4.0 and aa[0] == "C" and ab[0] == "C" and ra in HYD_RES and rb in HYD_RES and aa not in BACKBONE and ab not in BACKBONE:
        out.append("hydrophobic")
    ring_a, ring_b = aa in AROM_RING.get(ra, ()), ab in AROM_RING.get(rb, ())
    if d <= 4.5 and ((ring_a and (b in POS_ATOMS or (ab[0] == "C" and ab not in BACKBONE))) or
                     (ring_b and (a in POS_ATOMS or (aa[0] == "C" and aa not in BACKBONE)))):
        out.append("aromatic")
    return out


def interaction_kind(ra, aa, rb, ab, d):
    k = interaction_kinds(ra, aa, rb, ab, d)
    return k[0] if k else None


PROLIF_FAMILY = {"Hydrophobic": "hydrophobic", "HBDonor": "H-bond", "HBAcceptor": "H-bond", "Anionic": "ionic", "Cationic": "ionic",
                 "CationPi": "aromatic", "PiCation": "aromatic", "PiStacking": "aromatic", "FaceToFace": "aromatic", "EdgeToFace": "aromatic"}
PROLIF_INTERACTIONS = ["Hydrophobic", "HBDonor", "HBAcceptor", "Anionic", "Cationic", "CationPi", "PiCation", "PiStacking"]
_PL_CACHE = {}
PROLIF_STATE = {"engine": None, "warned": False, "error": ""}


def prolif_version():
    try:
        import prolif
        return getattr(prolif, "__version__", "?")
    except Exception:
        return None


def _elem(name):
    n = name.strip()
    return n[0] if n and n[0].isalpha() else (n[1] if len(n) > 1 else "C")


def _chain_pdb_block(ch, chain_letter):
    """PDB text of one chain (heavy atoms only, one residue number per residue) and the indices of the atoms that were written."""
    keep, lines = [], []
    for i, (xyz, name, rn, ri) in enumerate(zip(ch["xyz"], ch["name"], ch["resname"], ch["ri"])):
        e = _elem(str(name))
        if e in ("H", "D"):
            continue
        keep.append(i)
        an = (" " + str(name)) if len(str(name)) < 4 else str(name)[:4]
        lines.append("ATOM  %5d %-4s %3s %1s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s" % (len(keep) % 100000, an, rn, chain_letter, int(ri) % 9999 + 1,
                                                                                           xyz[0], xyz[1], xyz[2], e))
    return "\n".join(lines) + "\nEND\n", np.array(keep, int)


def _prolif_mol(ch, chain_letter):
    """RDKit molecule with hydrogens for one protein chain: bonds and bond orders from the standard residue templates, formal charges for the
    usual charged groups (Lys, Arg, Asp, Glu, termini), hydrogens placed by RDKit. Returns (mol, kept atom indices, number of heavy atoms)."""
    from rdkit import Chem
    block, keep = _chain_pdb_block(ch, chain_letter)
    mol = Chem.MolFromPDBBlock(block, sanitize=False, removeHs=False)
    if mol is None or mol.GetNumAtoms() != len(keep):
        raise RuntimeError("RDKit could not read the chain")
    first = min(int(a.GetPDBResidueInfo().GetResidueNumber()) for a in mol.GetAtoms())
    for a in mol.GetAtoms():
        info = a.GetPDBResidueInfo()
        rn, an = info.GetResidueName().strip(), info.GetName().strip()
        dbl = any(b.GetBondType() == Chem.BondType.DOUBLE for b in a.GetBonds())
        if (rn, an) == ("LYS", "NZ"):
            a.SetFormalCharge(1)
        elif rn == "ARG" and an in ("NH1", "NH2") and dbl:
            a.SetFormalCharge(1)
        elif (rn, an) in (("ASP", "OD1"), ("ASP", "OD2"), ("GLU", "OE1"), ("GLU", "OE2")) and not dbl:
            a.SetFormalCharge(-1)
        elif an == "OXT":
            a.SetFormalCharge(-1)
        elif an == "N" and int(info.GetResidueNumber()) == first and rn != "PRO":
            a.SetFormalCharge(1)
    Chem.SanitizeMol(mol)
    n_heavy = mol.GetNumAtoms()
    mol = Chem.AddHs(mol, addCoords=True, addResidueInfo=True)
    return mol, keep, n_heavy


def _side_xyz(mol, idx, n_heavy, keep, xyz_of):
    """Position of an interaction partner: mean of the heavy atoms involved (a hydrogen counts as its heavy atom)."""
    pts = []
    for i in idx:
        i = int(i)
        if i >= n_heavy:
            nb = mol.GetAtomWithIdx(i).GetNeighbors()
            i = nb[0].GetIdx() if nb else i
        if i < n_heavy:
            pts.append(xyz_of[keep[i]])
    if not pts:
        raise RuntimeError("no heavy atoms in interaction")
    return np.mean(pts, axis=0)


def prolif_pairs(rec, bind):
    """Interactions between receptor and binder from ProLIF (https://prolif.readthedocs.io): hydrophobic, H-bond, ionic, cation-pi and pi-stacking.
    Hydrogens are added with RDKit (the structure files have none). Returns a list of dict(kind, name, rec (residue index), bind (residue index),
    d, a (xyz on the receptor side), b (xyz on the binder side)) or None if ProLIF cannot be used (not installed or an error: then the simple
    distance rules are used instead)."""
    if PROLIF_STATE["engine"] == "off":
        return None
    key = hashlib.md5(np.round(np.vstack([rec["xyz"], bind["xyz"]]), 2).tobytes() + "".join(rec["name"][:50]).encode()).hexdigest()
    if key in _PL_CACHE:
        return _PL_CACHE[key]
    try:
        import prolif as plf
        mr, kr, nr = _prolif_mol(rec, "A")
        mb, kb, nb = _prolif_mol(bind, "B")
        fp = plf.Fingerprint(PROLIF_INTERACTIONS, count=True)
        ifp = fp.generate(plf.Molecule(mb), plf.Molecule(mr), metadata=True)
        out = []
        for (lres, pres), inter in ifp.items():
            ib, ir = int(getattr(lres, "number")) - 1, int(getattr(pres, "number")) - 1
            for name, mds in inter.items():
                fam = PROLIF_FAMILY.get(name)
                if fam is None:
                    continue
                for md in (mds if isinstance(mds, (list, tuple)) else [mds]):
                    pi = md.get("parent_indices") or md.get("indices")
                    xb = _side_xyz(mb, pi["ligand"], nb, kb, bind["xyz"])
                    xr = _side_xyz(mr, pi["protein"], nr, kr, rec["xyz"])
                    out.append(dict(kind=fam, name=name, rec=ir, bind=ib, d=float(np.linalg.norm(xb - xr)), a=xr.tolist(), b=xb.tolist()))
        PROLIF_STATE.update(engine="ProLIF " + str(prolif_version()), error="")
    except Exception as e:                                           # any problem: fall back to the distance rules
        PROLIF_STATE.update(engine=None, error=f"{type(e).__name__}: {str(e)[:160]}")
        if not PROLIF_STATE["warned"]:
            PROLIF_STATE["warned"] = True
            print("Note: ProLIF could not be used here (" + PROLIF_STATE["error"] + "). The interactions are found with simple distance rules instead.")
        out = None
    _PL_CACHE[key] = out
    return out


def interaction_engine():
    return PROLIF_STATE["engine"] or "simple distance rules"


def contact_detail(A, B, cutoff=4.5, interactions=False):
    """Residue pairs of chains A and B with heavy atoms closer than cutoff.
    Returns {(index in A, index in B): dict(n atom pairs, dmin, kinds, kc = interactions per kind, best = closest pair per kind as (d, xyz A, xyz B))}.
    The interaction kinds come from simple distance rules; with interactions=True they come from ProLIF if it is available (slower)."""
    d = dist_matrix(A["xyz"], B["xyz"])
    out = {}
    for i, j in zip(*np.nonzero(d < cutoff)):
        key = (int(A["ri"][i]), int(B["ri"][j]))
        e = out.setdefault(key, dict(n=0, dmin=99.0, kinds=set(), kc=Counter(), best={}))
        e["n"] += 1
        e["dmin"] = min(e["dmin"], float(d[i, j]))
        for k in interaction_kinds(A["resname"][i], A["name"][i], B["resname"][j], B["name"][j], d[i, j]):
            e["kinds"].add(k)
            e["kc"][k] += 1
            if k not in e["best"] or d[i, j] < e["best"][k][0]:
                e["best"][k] = (float(d[i, j]), A["xyz"][i].tolist(), B["xyz"][j].tolist())
    if interactions:
        pairs = prolif_pairs(A, B)
        if pairs is not None:
            for e in out.values():
                e["kinds"], e["kc"], e["best"] = set(), Counter(), {}
            for p in pairs:
                e = out.get((p["rec"], p["bind"]))
                if e is None:
                    continue
                k = p["kind"]
                e["kinds"].add(k); e["kc"][k] += 1
                if k not in e["best"] or p["d"] < e["best"][k][0]:
                    e["best"][k] = (p["d"], p["a"], p["b"])
    return out


def detect_chains(G, pep_len=(20, 45)):
    """Peptide = a short chain with the most contacts to another chain; receptor = that other chain."""
    best = (0, None, None)
    for p, pc in G.items():
        if not (pep_len[0] <= len(pc["res"]) <= pep_len[1]):
            continue
        for r, rc in G.items():
            if r == p:
                continue
            n = int((dist_matrix(pc["xyz"], rc["xyz"]) < 4.5).sum())
            if n > best[0]:
                best = (n, r, p)
    if best[1] is None:
        raise RuntimeError("could not find a peptide chain in contact with a receptor chain; set REC_CHAIN and PEP_CHAIN by hand")
    return best[1], best[2]


def kabsch(mobile, target):
    mc, tc = mobile.mean(0), target.mean(0)
    H = (mobile - mc).T @ (target - tc)
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, tc - R @ mc


def rmsd(a, b):
    return float(np.sqrt(((a - b) ** 2).sum(1).mean()))


def atoms_to_pdb(atoms, R=None, t=None, chain_map=None, bfac=None):
    """Write atom tuples as PDB text. bfac: optional {(chain, resseq, icode): value}."""
    lines = []
    for n, a in enumerate(atoms, 1):
        xyz = np.array(a[5:8])
        if R is not None:
            xyz = R @ xyz + t
        c = (chain_map or {}).get(a[0], a[0])
        b = a[8] if bfac is None else bfac.get((a[0], a[1], a[2]), a[8])
        lines.append("ATOM  %5d %-4s %3s %1s%4d    %8.3f%8.3f%8.3f  1.00%6.2f          %2s" % (
            n % 100000, a[4][:4], a[3], c[:1], a[1] % 10000, xyz[0], xyz[1], xyz[2], b, a[4][:1]))
    return "\n".join(lines) + "\nEND\n"


# =====================================================================================
#  UniProt numbering, residue mapping, superposition on the receptor
# =====================================================================================
def _cif_table(text, cat):
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.strip() == "loop_" and i + 1 < len(lines) and lines[i + 1].startswith(cat + "."):
            cols, j = [], i + 1
            while j < len(lines) and lines[j].startswith(cat + "."):
                cols.append(lines[j].strip()[len(cat) + 1:]); j += 1
            rows = []
            while j < len(lines) and not lines[j].startswith(("#", "loop_", "_")):
                tok = lines[j].split()
                if len(tok) == len(cols):
                    rows.append(dict(zip(cols, tok)))
                j += 1
            return rows
    single = {}
    for l in lines:
        if l.startswith(cat + "."):
            parts = l.split(None, 1)
            if len(parts) == 2:
                single[parts[0][len(cat) + 1:]] = parts[1].strip()
    return [single] if single else []


def uniprot_segments(text, chain):
    """[(first PDB number, last PDB number, UniProt number of the first)] for a chain, read from DBREF (PDB) or _struct_ref_seq (mmCIF)."""
    segs = []
    try:
        if text.lstrip().startswith("data_"):
            for r in _cif_table(text, "_struct_ref_seq"):
                if r.get("pdbx_strand_id") == chain and "db_align_beg" in r:
                    a = int(r.get("pdbx_auth_seq_align_beg", "x"))
                    b = int(r.get("pdbx_auth_seq_align_end", "x"))
                    segs.append((a, b, int(r["db_align_beg"])))
        else:
            for line in text.splitlines():
                if line.startswith("DBREF ") and len(line) >= 67 and line[12] == chain and line[26:32].strip() == "UNP":
                    segs.append((int(line[14:18]), int(line[20:24]), int(line[55:60])))
    except (ValueError, KeyError):
        return []
    return segs


def uniprot_numbers(text, rec):
    """{PDB residue number: UniProt residue number} for a receptor chain; identity if the file has no UniProt reference."""
    segs = uniprot_segments(text, rec["id"])
    out, src = {}, "assumed equal to the PDB numbering (the file has no UniProt reference)"
    for r in rec["res"]:
        n = r["num"]
        out[n] = n
        for a, b, u in segs:
            if a <= n <= b:
                out[n] = u + (n - a); src = "from the DBREF / struct_ref_seq record of the file"; break
    return out, src


def residue_map(a, b):
    """Pairs (i, j): residue i of chain a corresponds to residue j of chain b. Same residue number and letter when that holds for most
    residues, otherwise a sequence alignment."""
    nb = {r["num"]: j for j, r in enumerate(b["res"])}
    pairs = [(i, nb[r["num"]]) for i, r in enumerate(a["res"]) if r["num"] in nb and r["aa"] == b["res"][nb[r["num"]]]["aa"]]
    if len(pairs) >= 0.8 * min(len(a["res"]), len(b["res"])):
        return pairs
    return seq_pairs(chain_seq(a), chain_seq(b))


def seq_pairs(sa, sb):
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    pairs = []
    for blk in sm.get_matching_blocks():
        pairs += [(blk.a + k, blk.b + k) for k in range(blk.size)]
    return pairs


def site_numbers(ref, radius=15.0):
    """Receptor residue numbers whose CA is within `radius` A of the crystal GLP-1: the part of the receptor used for superposition."""
    d = dist_matrix(ca_coords(ref["rec"]), ca_coords(ref["pep"])).min(1)
    return {ref["rec"]["res"][i]["num"] for i in np.nonzero(d < radius)[0]}


def transform_atoms(atoms, R, t):
    return [a[:5] + tuple(float(x) for x in (R @ np.array(a[5:8]) + t)) + a[8:] for a in atoms]


def fit_to_reference(atoms, rec_chain, ref, region="site", radius=15.0):
    """Rotation and translation that put the receptor of `atoms` onto the 6X18 receptor (Kabsch on CA atoms).
    region 'site': residues within `radius` A of GLP-1 (the part that matters for comparing binders); 'all': the whole receptor.
    Returns (R, t, rmsd, n residues used), or (None, None, nan, 0)."""
    rec = get_chain(atoms, rec_chain)
    if not len(rec["res"]):
        return None, None, float("nan"), 0
    pairs = residue_map(rec, ref["rec"])
    if region == "site":
        site = site_numbers(ref, radius)
        sel = [(i, j) for i, j in pairs if ref["rec"]["res"][j]["num"] in site]
        pairs = sel if len(sel) >= 6 else pairs
    if len(pairs) < 6:
        return None, None, float("nan"), 0
    ca_m, ca_r = ca_coords(rec), ca_coords(ref["rec"])
    mob, tgt = ca_m[[i for i, _ in pairs]], ca_r[[j for _, j in pairs]]
    R, t = kabsch(mob, tgt)
    return R, t, rmsd(mob @ R.T + t, tgt), len(pairs)


def superpose_text(model_text, ref, region="site", rec_chain=None):
    """The model (PDB text) moved onto the 6X18 receptor. Returns (text, rmsd, n residues used)."""
    atoms = parse_pdb(model_text)
    R, t, fit, n = fit_to_reference(atoms, rec_chain or REC, ref, region)
    if R is None:
        return model_text, float("nan"), 0
    return atoms_to_pdb(atoms, R, t), fit, n


# =====================================================================================
#  The reference complex (6X18)
# =====================================================================================
def build_reference(text, rec_chain=None, pep_chain=None, cutoff=4.5, n_hot=5):
    atoms = load_structure(text)
    ids = list(dict.fromkeys(a[0] for a in atoms))
    G = {c: get_chain(atoms, c) for c in ids}
    if not (rec_chain and pep_chain):
        rec_chain, pep_chain = detect_chains(G)
    rec, pep = G[rec_chain], G[pep_chain]
    cd = contact_detail(rec, pep, cutoff, interactions=True)
    uni, uni_src = uniprot_numbers(text, rec)
    per_rec, rows = {}, []
    for (j, p), e in cd.items():
        rr, pr = rec["res"][j], pep["res"][p]
        x = per_rec.setdefault(j, dict(id=f"{REC}:{rr['num']}", num=rr["num"], aa=rr["aa"], aa3=rr["resname"].title(),
                                       n=0, pep_pos=set(), pep_nums=set(), kinds=set()))
        x["n"] += e["n"]; x["pep_pos"].add(p); x["pep_nums"].add(pr["num"]); x["kinds"] |= e["kinds"]
        rows.append(dict(glp1_pos=p + 1, glp1_residue=f"{pr['aa']}{pr['num']}", receptor_residue=f"{REC}:{rr['num']}",
                         receptor_aa=rr["aa"], uniprot_number=uni.get(rr["num"], rr["num"]), atom_pairs=e["n"], closest_A=round(e["dmin"], 2),
                         interactions=", ".join(sorted(e["kinds"]))))
    table = pd.DataFrame(rows).sort_values(["glp1_pos", "atom_pairs"], ascending=[True, False]).reset_index(drop=True)
    half = len(pep["res"]) // 2
    def top(filter_fn):
        c = Counter()
        for (j, p), e in cd.items():
            if filter_fn(p):
                c[j] += e["n"]
        return sorted((rec["res"][j]["num"] for j, _ in c.most_common(n_hot)))
    presets = {"ECD groove (contacts of the C-terminal half of GLP-1)": [f"{REC}:{n}" for n in top(lambda p: p >= half)],
               "Pocket rim (contacts of the N-terminal half of GLP-1)": [f"{REC}:{n}" for n in top(lambda p: p < half)],
               "Whole footprint (strongest contacts overall)": [f"{REC}:{n}" for n in top(lambda p: True)]}
    # contacts per interaction type, seen from the peptide side and from the receptor side (heat maps)
    heat_pep = np.zeros((len(KIND_ROWS), len(pep["res"])))
    heat_rec = {j: np.zeros(len(KIND_ROWS)) for j in per_rec}
    for (j, p), e in cd.items():
        for k, name in enumerate(KIND_ROWS):
            v = e["n"] if k == 0 else e["kc"].get(name, 0)
            heat_pep[k, p] += v
            heat_rec[j][k] += v
    rec_order = sorted(per_rec, key=lambda j: rec["res"][j]["num"])
    ref = dict(rec=rec, pep=pep, rec_chain=rec_chain, pep_chain=pep_chain, per_rec=per_rec, table=table, presets=presets,
               uniprot=uni, uniprot_source=uni_src, heat_pep=heat_pep, heat_rec=np.array([heat_rec[j] for j in rec_order]).T,
               heat_rec_idx=rec_order,
               footprint={rec["res"][j]["num"] for j in per_rec}, pep_seq=chain_seq(pep), rec_seq=chain_seq(rec),
               rec_nums=[r["num"] for r in rec["res"]], other_chains=[c for c in ids if c not in (rec_chain, pep_chain)],
               atoms=[a for a in atoms if a[0] in (rec_chain, pep_chain)], cutoff=cutoff, interaction_engine=interaction_engine())
    return ref


def residue_lookup(ref, who, number):
    """What does one residue do in 6X18? who = 'receptor' (UniProt numbering) or 'GLP-1' (numbering of the structure file).
    Returns the contact pairs of that residue with the interaction types, or a one-line note if it touches nothing within 4.5 A."""
    t = ref["table"]
    number = int(number)
    if str(who).lower().startswith("rec"):
        sub = t[t["uniprot_number"] == number]
        what = f"receptor residue {number} (UniProt numbering)"
    else:
        nums = t["glp1_residue"].str.extract(r"(\d+)")[0].astype(float)
        sub = t[nums == number]
        what = f"GLP-1 residue {number}"
    if sub.empty:
        return pd.DataFrame({"result": [f"{what}: no contact within {ref['cutoff']} Å in 6X18 (or the number is not in the structure)."]})
    return sub.reset_index(drop=True)


def crystal_as_design(ref):
    """The crystal complex written like a server file: receptor R, GLP-1 as binder B numbered from 1."""
    out, k = [], {}
    for a in ref["atoms"]:
        if a[0] == ref["rec_chain"]:
            out.append((REC,) + a[1:])
        elif a[0] == ref["pep_chain"]:
            key = (a[1], a[2])
            k.setdefault(key, len(k) + 1)
            out.append((BIND, k[key], "") + a[3:])
    return atoms_to_pdb(out)


def reference_list(ref, seed=7):
    """The reference peptides with their sequences filled in."""
    glp1 = ref["pep_seq"] if difflib.SequenceMatcher(None, ref["pep_seq"], GLP1_SEQ).ratio() > 0.85 else GLP1_SEQ
    out = []
    for r in REFERENCES:
        r = dict(r)
        if r["id"] == "ref_glp1":
            r["seq"] = glp1
        elif r["id"] == "ctrl_scrambled":
            r["seq"] = scramble(glp1, seed)
        out.append(r)
    return out


# =====================================================================================
#  Confidence files and scoring
# =====================================================================================
def load_confidence(path):
    return json.load(open(path)) if path and Path(path).exists() else {}


def load_pae(path):
    if not path or not Path(path).exists():
        return None
    z = np.load(path, allow_pickle=False)
    if isinstance(z, np.ndarray):
        return z.astype(float)
    for k in ("pae", "predicted_aligned_error", "PAE"):
        if k in z.files:
            return np.asarray(z[k], float)
    return np.asarray(z[z.files[0]], float)


def _first(d, names):
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return None


def residue_plddt(conf, rec, bind, model_atoms_order=None):
    """Per-residue pLDDT (receptor then binder). Uses the confidence file; if it holds one value per atom the values
    are averaged per residue; if nothing usable is there, the B-factors of the model are used (AlphaFold convention)."""
    n_res = len(rec["res"]) + len(bind["res"])
    p = _first(conf, ["plddt", "plddts", "per_residue_plddt", "atom_plddts"])
    if p is not None:
        p = np.asarray(p, float)
        if p.size == n_res:
            out = p
        elif p.size == len(rec["ri"]) + len(bind["ri"]):
            ri = np.concatenate([rec["ri"], bind["ri"] + len(rec["res"])])
            out = np.array([p[ri == k].mean() for k in range(n_res)])
        else:
            out = None
        if out is not None:
            return out * 100 if np.nanmax(out) <= 1.0 else out
    return np.concatenate([res_bfactor(rec), res_bfactor(bind)])


def interface_sets(rec, bind, cut=8.0):
    d = dist_matrix(rec["xyz"], bind["xyz"])
    close = d < cut
    ir = sorted({int(rec["ri"][i]) for i in np.nonzero(close.any(1))[0]})
    ib = sorted({int(bind["ri"][j]) for j in np.nonzero(close.any(0))[0]})
    return ir, ib


def calc_d0(L):
    L = max(27.0, float(L))
    return max(1.0, 1.24 * (L - 15) ** (1 / 3) - 1.8)


def _ipsae_dir(pae, ia, ib, cutoff):
    sub = pae[np.ix_(ia, ib)]
    best = 0.0
    for row in sub:
        ok = row < cutoff
        n = int(ok.sum())
        if n:
            best = max(best, float((1.0 / (1.0 + (row[ok] / calc_d0(n)) ** 2)).mean()))
    return best


def ipsae(pae, n_rec, n_bind, cutoff=10.0):
    """ipSAE (Dunbrack 2025) for a two-chain complex, own re-implementation for teaching."""
    ir, ib = np.arange(n_rec), np.arange(n_rec, n_rec + n_bind)
    return round(max(_ipsae_dir(pae, ir, ib, cutoff), _ipsae_dir(pae, ib, ir, cutoff)), 3)


def align_on_receptor(rec_from, rec_to, anchor_nums):
    """Rotation/translation that puts rec_from onto rec_to using the CA atoms of residues in anchor_nums (by residue number)."""
    ca_f, ca_t = ca_coords(rec_from), ca_coords(rec_to)
    nf = {r["num"]: i for i, r in enumerate(rec_from["res"])}
    nt = {r["num"]: i for i, r in enumerate(rec_to["res"])}
    common = [n for n in anchor_nums if n in nf and n in nt]
    if len(common) < 6:
        return None, None
    return kabsch(ca_f[[nf[n] for n in common]], ca_t[[nt[n] for n in common]])


def pose_and_backbone(model_rec, model_bind, des_rec, des_bind, radius=12.0):
    """Backbone RMSD: binder CA after fitting binder onto binder. Pose RMSD: binder CA after fitting the receptor residues
    within `radius` A of the design's binder (the part of the receptor the binder touches), without moving the binder."""
    nan = (float("nan"), float("nan"))
    if len(model_bind["res"]) != len(des_bind["res"]) or not len(des_bind["res"]):
        return nan
    cm, cd = ca_coords(model_bind), ca_coords(des_bind)
    if np.isnan(cm).any() or np.isnan(cd).any():
        return nan
    R, t = kabsch(cm, cd)
    bb = rmsd(cm @ R.T + t, cd)
    d = dist_matrix(ca_coords(des_rec), cd).min(1)
    order = np.argsort(d)
    near = [des_rec["res"][i]["num"] for i in order if d[i] < radius]
    if len(near) < 20:                       # binder far from the receptor: use the 20 closest receptor residues
        near = [des_rec["res"][i]["num"] for i in order[:20]]
    R2, t2 = align_on_receptor(model_rec, des_rec, near)
    if R2 is None:
        return bb, float("nan")
    return bb, rmsd(cm @ R2.T + t2, cd)


def contact_metrics(rec, bind, ref, hotspots=()):
    """Contacts of a binder with the receptor: residues touched, hotspots hit, overlap with the GLP-1 site, closest distance, clashes."""
    nan = float("nan")
    cd = contact_detail(rec, bind, 4.5)
    touched = {rec["res"][j]["num"] for (j, _) in cd}
    hs = [int(str(h).split(":")[-1]) for h in hotspots]
    fp = ref["footprint"]
    d = dist_matrix(rec["xyz"], bind["xyz"])
    hits = sum(h in touched for h in hs)
    return dict(n_contact_res=len({b for (_, b) in cd}), hotspot_n=len(hs), hotspot_hits=hits,
                hotspot_frac=round(hits / len(hs), 2) if hs else nan,
                site_overlap=round(len(touched & fp) / len(touched), 2) if touched else nan,    # share of binder contacts on the GLP-1 site
                site_cover=round(len(touched & fp) / len(fp), 2) if fp else nan,                  # share of the GLP-1 site covered
                min_dist=round(float(d.min()), 2), n_clash=int((d < 2.2).sum()))


def design_metrics(design_text, ref, hotspots=()):
    """The same contact numbers for the design file of the server (prefix des_), before any OpenFold3 prediction exists."""
    atoms = parse_pdb(design_text)
    rec, bind = get_chain(atoms, REC), get_chain(atoms, BIND)
    if not len(rec["res"]) or not len(bind["res"]):
        return {}
    m = contact_metrics(rec, bind, ref, hotspots)
    return {"des_" + k: v for k, v in m.items() if k in ("n_contact_res", "hotspot_hits", "hotspot_frac", "site_overlap", "site_cover", "min_dist", "n_clash")}


RFD4_CORE = [   # (key in the server's metrics, short name): the few that are shown by default; all others stay in the scorecard file
    ("hotspot_obedience.hotspot_obedience", "hotspot_obedience"),
    ("clash_metrics.frac_atoms_clashing_1p5A", "clash_frac"),
    ("bond_length_metrics.bond_length.frac_unreasonable", "bond_unreasonable"),
    ("sequence_adherence.sequence_adherence", "seq_adherence"),
    ("interchain_interactions.hbond_atom_pair_count_coi", "hbond_pairs"),
    ("interchain_interactions.saltbridge_residue_pair_count_coi", "saltbridge_pairs"),
    ("interchain_interactions.pistack_residue_pair_count_coi", "pistack_pairs"),
    ("interchain_interactions.pication_residue_pair_count_coi", "pication_pairs"),
    ("interchain_interactions.hydrophobic_atom_pair_count_coi", "hydrophobic_pairs"),
    ("sse_distribution.helix_fraction_coi", "helix_frac"),
    ("pre_oracle_pass", "pre_oracle_pass"),
]


def flat_metrics(d):
    """Numeric metrics from whatever the design server returned (nested dicts are joined with '.'). The core metrics get the prefix
    rfd4_ (shown in the tables); every metric is also kept with the prefix rfd4all_ (scorecard file, details of one design)."""
    full = {}
    def walk(x, key):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, key + "." + str(k) if key else str(k))
        elif isinstance(x, bool):
            full[key] = int(x)
        elif isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x)):
            full[key] = round(float(x), 4)
    walk(d or {}, "")
    out = {}
    core = [(k, short) for k, short in RFD4_CORE if k in full]
    if core:
        for k, short in core:
            out["rfd4_" + short] = full[k]
    else:                                   # another server: show the first few numeric metrics
        for k in list(full)[:8]:
            out["rfd4_" + re.sub(r"[^A-Za-z0-9_]+", "_", k)] = full[k]
    for k, v in full.items():
        out["rfd4all_" + k] = v
    return out


def rfd4_details(df, rid):
    """Every metric the design server reported for one design."""
    row = df[df["id"] == rid]
    if row.empty:
        raise KeyError(f"no design called {rid}")
    r = row.iloc[0]
    return pd.Series({c[len("rfd4all_"):]: r[c] for c in df.columns if c.startswith("rfd4all_") and r[c] == r[c]}, name=rid)


def score_prediction(model_text, conf, pae, ref, hotspots=(), design_text=None):
    """All computed metrics for one predicted complex (receptor chain R, binder chain B). Missing stays NaN."""
    nan = float("nan")
    atoms = parse_pdb(model_text)
    rec, bind = get_chain(atoms, REC), get_chain(atoms, BIND)
    n_rec, n_bind = len(rec["res"]), len(bind["res"])
    row = dict(binder_len=n_bind)
    if not n_rec or not n_bind:
        return dict(row, note="model file lacks chain R or B")
    pl = residue_plddt(conf, rec, bind)
    row["binder_plddt"] = round(float(np.nanmean(pl[n_rec:])), 1)
    for k, names in (("ptm", ["ptm", "pTM"]), ("iptm", ["iptm", "ipTM", "interface_ptm"])):
        v = _first(conf, names)
        row[k] = round(float(v), 3) if v is not None else nan
    # interface (8 A) and PAE summaries
    ir, ib = interface_sets(rec, bind)
    row["iface_pae"], row["ipsae"] = nan, nan
    if pae is not None and pae.shape == (n_rec + n_bind, n_rec + n_bind):
        if not (ir and ib):                  # nothing within 8 A: report the whole cross-chain PAE instead
            ir, ib = list(range(n_rec)), list(range(n_bind))
            row["note"] = "no residues within 8 A: interface PAE is the whole cross-chain PAE"
        a = pae[np.ix_(ir, [n_rec + j for j in ib])]
        b = pae[np.ix_([n_rec + j for j in ib], ir)]
        row["iface_pae"] = round(float((a.mean() + b.mean()) / 2), 2)
        row["ipsae"] = ipsae(pae, n_rec, n_bind)
    elif pae is not None:
        row["note"] = f"PAE shape {pae.shape} does not match {n_rec}+{n_bind} residues"
    row.update(contact_metrics(rec, bind, ref, hotspots))
    row["backbone_rmsd"] = row["pose_rmsd"] = nan
    if design_text:
        da = parse_pdb(design_text)
        bb, ps = pose_and_backbone(rec, bind, get_chain(da, REC), get_chain(da, BIND))
        row["backbone_rmsd"], row["pose_rmsd"] = round(bb, 2), round(ps, 2)
    row["_n_rec"] = n_rec
    return row


def evidence_checks(row, thr=None):
    """(passed, evaluable, detail dict). A missing metric is not counted as a fail."""
    thr = thr or THRESHOLDS
    detail, passed, total = {}, 0, 0
    for key, label, op in CHECKS:
        v = row.get(key)
        tk = key
        if v is None or (isinstance(v, float) and math.isnan(v)):
            detail[label] = None
            continue
        ok = v >= thr[tk] if op == ">=" else v <= thr[tk]
        detail[label] = bool(ok)
        passed += int(ok); total += 1
    return passed, total, detail


# =====================================================================================
#  Jobs: API client, local pack, request fingerprint
# =====================================================================================
DONE_STATES = {"succeeded", "done", "completed", "finished", "ready"}
FAIL_STATES = {"failed", "error", "cancelled", "canceled", "rejected"}
ENDPOINTS = {"health": "/health", "targets": "/targets", "predict": "/jobs/predict", "generate": "/jobs/generate",
             "redesign": "/jobs/redesign", "job": "/jobs/{id}", "result": "/results/{id}"}
FP_KEYS = {"predict": ["target_id", "seed", "designs"],
           "generate": ["target_id", "seed", "n_designs", "binder_length", "hotspots"],
           "redesign": ["target_id", "seed", "parent_id", "fixed_positions", "temperature", "n_sequences"]}


def request_fingerprint(task, payload):
    """Same request, same fingerprint: this is the key of the server cache and of the precomputed pack."""
    d = {"task": task}
    for k in FP_KEYS[task]:
        v = payload.get(k)
        if k in ("hotspots", "fixed_positions"):
            v = sorted(v)
        if k == "designs":
            v = sorted([x["id"], x["sequence"]] for x in v)
        if k == "temperature":
            v = round(float(v), 3)
        d[k] = v
    return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:16]


def valid_job_id(x):
    """A job id the server can look up: not empty, not None/null, no slashes or spaces (it goes into a URL path)."""
    t = str(x if x is not None else "").strip()
    return bool(t) and t.lower() not in ("none", "null", "undefined", "nan") and not re.search(r"[\s/?#]", t)


class ApiClient:
    """Client for the workshop REST API (standard library only). Endpoint paths sit in one dict (ENDPOINTS)."""
    def __init__(self, base_url, token="", endpoints=None, poll=5.0, timeout=1800, retries=3, log=print):
        self.base = base_url.rstrip("/")
        self.token, self.ep = token, endpoints or ENDPOINTS
        self.poll, self.timeout, self.retries, self.log = poll, timeout, retries, log
        self.kind = "api"

    def _req(self, method, url, payload=None, raw=False):
        if not url.startswith("http"):
            parts = urllib.parse.urlsplit(self.base)
            if url.startswith("/") and parts.path and url.startswith(parts.path.rstrip("/") + "/"):
                url = f"{parts.scheme}://{parts.netloc}{url}"
            else:
                url = self.base + "/" + url.lstrip("/")
        data = None if payload is None else json.dumps(payload).encode()
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if self.token and url.startswith(self.base):          # the token never goes to another host
            headers["Authorization"] = "Bearer " + self.token
        last = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), timeout=60) as r:
                    body = r.read()
                return body if raw else json.loads(body.decode() or "{}")
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")[:300]
                if e.code in (401, 403):
                    raise RuntimeError(f"The server refused the request ({e.code}). Check your token. {msg}")
                if e.code == 429:
                    raise RuntimeError("Your group has reached its limit of running jobs. Wait for one to finish, then try again.")
                if e.code < 500:
                    raise RuntimeError(f"Server error {e.code}: {msg}")
                last = f"HTTP {e.code} {msg}"
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                last = str(e)
            time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"The server is not reachable ({last}). Tell an instructor.")

    def health(self):
        return self._req("GET", self.ep["health"])

    def fetch(self, ref):
        return self._req("GET", ref, raw=True)

    def submit(self, task, payload):
        job = self._req("POST", self.ep[task], payload)
        if not valid_job_id(job.get("job_id")):
            raise RuntimeError("The server did not return a usable job id: " + json.dumps(job)[:200])
        job["job_id"] = str(job["job_id"]).strip()
        return job

    def status(self, job_id):
        if not valid_job_id(job_id):
            raise RuntimeError(f"Server error 404: this job has no valid job id ({job_id!r}).")
        st = self._req("GET", self.ep["job"].format(id=job_id))
        st["state"] = str(st.get("status", "")).lower()
        return st

    def collect(self, job_id):
        if not valid_job_id(job_id):
            raise RuntimeError(f"Server error 404: this job has no valid job id ({job_id!r}).")
        t0, last = time.time(), None
        while True:
            st = self._req("GET", self.ep["job"].format(id=job_id))
            state = str(st.get("status", "")).lower()
            line = state + (f' (queue position {st["queue_position"]})' if st.get("queue_position") is not None else "")
            if line != last:
                self.log(f"  job {job_id}: {line}")
                last = line
            if state in DONE_STATES:
                break
            if state in FAIL_STATES:
                raise RuntimeError(f'job {job_id} {state}: {st.get("message", "no message")}')
            if time.time() - t0 > self.timeout:
                raise RuntimeError(f"job {job_id} has not finished after {int(self.timeout)} s. It may still be running: run this cell again later, or ask an instructor.")
            time.sleep(self.poll)
        rid = st.get("result_id") or job_id
        res = self._req("GET", self.ep["result"].format(id=rid))
        res.setdefault("job_id", job_id); res.setdefault("result_id", rid)
        for k in ("execution_mode", "model_version"):
            res.setdefault(k, st.get(k, ""))
        return res

    def run(self, task, payload):
        return self.collect(self.submit(task, payload)["job_id"])


class LocalPack:
    """Serves requests from the precomputed pack (folder ws3_data/cache/<fingerprint>/). Same interface as ApiClient."""
    def __init__(self, root, log=print):
        self.root, self.log, self.kind = Path(root), log, "pack"

    def health(self):
        return {"status": "ok (stored results only)", "models": {}}

    def fetch(self, ref):
        return Path(ref).read_bytes()

    def submit(self, task, payload):
        fp = request_fingerprint(task, dict(payload, seed=SEED))   # stored results were made with the base seed and serve every group
        if not (self.root / "cache" / fp / "result.json").exists():
            raise RuntimeError("This exact request is not in the stored results. Pick one of the presets (and a menu length), or switch to the server.")
        return {"job_id": "pack-" + fp}

    def status(self, job_id):
        return {"state": "succeeded", "status": "succeeded", "execution_mode": "precomputed"}

    def collect(self, job_id):
        fp = job_id[5:]
        d = self.root / "cache" / fp
        res = json.load(open(d / "result.json"))
        for dd in res["designs"].values():
            dd["artifacts"] = {k: str(d / v) for k, v in dd.get("artifacts", {}).items()}
            dd["execution_mode"] = "precomputed"
        res.update(job_id=job_id, result_id=fp, execution_mode="precomputed")
        return res

    def run(self, task, payload):
        return self.collect(self.submit(task, payload)["job_id"])


ART = {"design": "design.pdb", "model": "model.pdb", "confidence": "confidence.json", "pae": "pae.npz"}


def save_result(client, result, root):
    """Download the files of a result into root/results/<result_id>/<design>/ and return one record per design."""
    rid = result.get("result_id") or result.get("job_id")
    recs = []
    for name, d in result.get("designs", {}).items():
        folder = Path(root) / "results" / rid / name
        folder.mkdir(parents=True, exist_ok=True)
        files = {}
        for key, fname in ART.items():
            ref = d.get("artifacts", {}).get(key)
            if ref:
                p = folder / fname
                if not p.exists():
                    p.write_bytes(client.fetch(ref))
                files[key] = str(p)
        mode = d.get("execution_mode") or result.get("execution_mode", "")
        ver = d.get("model_version") or result.get("model_version", "")
        (folder / "provenance.json").write_text(json.dumps(dict(
            execution_mode=mode, model_version=ver, job_id=result.get("job_id", ""), result_id=rid,
            fetched_at=datetime.datetime.now().isoformat(timespec="seconds")), indent=1))
        recs.append(dict(id=name, sequence=d.get("sequence", ""), origin=d.get("origin", ""), parent=d.get("parent"),
                         round=d.get("round"), files=files, mode=mode, version=ver, result_id=rid, metrics=d.get("metrics") or {}))
    return recs


def pack_result(client, task, payload, result, pack_root):
    """Used by the precompute script: store a result in the pack so that LocalPack can serve it."""
    fp = request_fingerprint(task, payload)
    d = Path(pack_root) / "cache" / fp
    out = json.loads(json.dumps(result))
    for name, dd in out["designs"].items():
        arts = {}
        for key, fname in ART.items():
            ref = dd.get("artifacts", {}).get(key)
            if ref:
                (d / "files" / name).mkdir(parents=True, exist_ok=True)
                (d / "files" / name / fname).write_bytes(client.fetch(ref))
                arts[key] = f"files/{name}/{fname}"
        dd["artifacts"] = arts
    d.mkdir(parents=True, exist_ok=True)
    out["request"] = dict(task=task, **{k: payload.get(k) for k in FP_KEYS[task]})
    (d / "result.json").write_text(json.dumps(out))
    return fp


def now_stamp():
    return datetime.datetime.now().isoformat(timespec="seconds")


# =====================================================================================
#  Scorecard
# =====================================================================================
def score_records(recs, ref, hotspots=(), extra=None, thr=None):
    """One scorecard row per design record. `extra` adds fixed columns (group, round, hypothesis id, ...)."""
    rows = []
    for r in recs:
        f = r["files"]
        base = dict(id=r["id"], parent=r.get("parent"), round=r.get("round"), origin=r.get("origin"),
                    sequence=r["sequence"], source=r.get("mode", ""), model_version=r.get("version", ""))
        if r.get("label"):
            base.update(label=r["label"], expected=r.get("expected", ""))
        base.update(extra or {})
        base.update(flat_metrics(r.get("metrics")))
        design_text = None
        if f.get("design"):
            design_text = Path(f["design"]).read_text()
        elif r.get("origin") == "reference" and r["id"] == "ref_glp1":
            design_text = crystal_as_design(ref)
        if "model" not in f:
            base.update(binder_len=len(r["sequence"]), note="OpenFold3 not run yet" if design_text else "no model returned")
            if design_text:
                base.update(design_metrics(design_text, ref, hotspots))
                base["liabilities"] = "; ".join(liabilities(r["sequence"]))
            rows.append(base)
            continue
        row = score_prediction(Path(f["model"]).read_text(), load_confidence(f.get("confidence")), load_pae(f.get("pae")),
                               ref, hotspots, design_text)
        row.pop("_n_rec", None)
        base.update(row)
        if design_text and r.get("origin") != "reference":
            base.update(design_metrics(design_text, ref, hotspots))
        base["liabilities"] = "; ".join(liabilities(r["sequence"])) if r.get("origin") in ("rfd4", "mpnn", "manual") else ""
        p, t, _ = evidence_checks(base, thr)
        base["checks"] = f"{p}/{t}" if t else ""
        base["checks_passed"], base["checks_total"] = p, t
        rows.append(base)
    return pd.DataFrame(rows)


SHOW_COLS = ["id", "parent", "round", "origin", "binder_len", "iptm", "ptm", "binder_plddt", "iface_pae", "ipsae",
             "backbone_rmsd", "pose_rmsd", "hotspot_hits", "site_overlap", "n_clash", "checks"]


def short_table(df, cols=None):
    cols = [c for c in (cols or SHOW_COLS) if c in df.columns]
    return df[cols]


def sequence_changes(parent_seq, seq):
    pos = [i + 1 for i, (a, b) in enumerate(zip(parent_seq, seq)) if a != b]
    return len(pos), pos


# =====================================================================================
#  Residue classes for the redesign step
# =====================================================================================
def residue_classes(design_text):
    """Binder residues of a design: interface (heavy atom within 4.5 A of the receptor), core (buried, many neighbours) or surface.
    Burial is a heuristic: the number of binder atoms within 9 A of the residue's side chain centre."""
    atoms = parse_pdb(design_text)
    rec, bind = get_chain(atoms, REC), get_chain(atoms, BIND)
    cd = contact_detail(rec, bind, 4.5)
    iface = {b for (_, b) in cd}
    n = len(bind["res"])
    bur = np.zeros(n)
    for k in range(n):
        m = bind["ri"] == k
        sc = m & ~np.isin(bind["name"], list(BACKBONE))
        pt = bind["xyz"][sc].mean(0) if sc.any() else bind["xyz"][m].mean(0)
        bur[k] = int((np.linalg.norm(bind["xyz"] - pt, axis=1) < 9.0).sum())
    cutoff = np.percentile(bur[[k for k in range(n) if k not in iface]] if len(iface) < n else bur, 60)
    out = []
    for k in range(n):
        cls = "interface" if k in iface else ("core" if bur[k] >= cutoff else "surface")
        out.append(dict(pos=k + 1, aa=bind["res"][k]["aa"], cls=cls, burial=int(bur[k])))
    return out


# =====================================================================================
#  Plots
# =====================================================================================
def _plt():
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 13, "xtick.labelsize": 12, "ytick.labelsize": 12,
                                "legend.fontsize": 11, "figure.titlesize": 14, "figure.dpi": 100, "axes.titlepad": 8})
    return plt


def plot_pae(pae, n_rec, ax=None, title=""):
    """PAE matrix in the colours of the AlphaFold Protein Structure Database: dark green = small expected error, white = large (0 to 30 A)."""
    plt = _plt()
    ax = ax or plt.subplots(figsize=(5.8, 5.0))[1]
    if pae is None:
        ax.text(0.5, 0.5, "no PAE file", ha="center"); ax.axis("off"); return ax
    im = ax.imshow(pae, cmap="Greens_r", vmin=0, vmax=30)
    ax.axhline(n_rec - 0.5, color="#555555", lw=1.0); ax.axvline(n_rec - 0.5, color="#555555", lw=1.0)
    ax.set_title(title or "Predicted aligned error (PAE)", fontsize=14)
    ax.set_xlabel("Scored residue", fontsize=13); ax.set_ylabel("Aligned residue", fontsize=13)
    ax.tick_params(labelsize=12)
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Expected position error (Å)", fontsize=12)
    cb.ax.tick_params(labelsize=11)
    return ax


def plot_plddt(pl, n_rec, ax=None):
    plt = _plt()
    ax = ax or plt.subplots(figsize=(6.0, 3.6))[1]
    pl = np.asarray(pl, float)
    ax.plot(range(1, len(pl) - n_rec + 1), pl[n_rec:], color="#1D9A78", lw=2)
    ax.axhline(70, color="grey", ls=":", lw=1.2); ax.axhline(90, color="grey", ls=":", lw=1.2)
    ax.set_ylim(0, 100); ax.set_xlabel("Binder residue", fontsize=13); ax.set_ylabel("pLDDT", fontsize=13)
    ax.set_title("Binder pLDDT per residue", fontsize=14)
    ax.tick_params(labelsize=12)
    return ax


def _spread(xy, min_d=0.04, max_shift=0.05, iters=100):
    """Push points apart that are closer than min_d (in axes units 0 to 1), never moving one further than max_shift from its true position."""
    P0 = np.asarray(xy, float).reshape(-1, 2)
    P = P0.copy()
    n = len(P)
    for _ in range(iters):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                dv = P[i] - P[j]
                dist = float(np.hypot(dv[0], dv[1]))
                if dist < min_d:
                    if dist < 1e-9:
                        ang = (i * 2.399963 + j * 0.7) % (2 * math.pi)
                        u = np.array([math.cos(ang), math.sin(ang)])
                    else:
                        u = dv / dist
                    push = (min_d - dist) / 2
                    P[i] += u * push; P[j] -= u * push; moved = True
        D = P - P0
        nrm = np.hypot(D[:, 0], D[:, 1])
        big = nrm > max_shift
        if big.any():
            P[big] = P0[big] + D[big] / nrm[big, None] * max_shift
        if not moved:
            break
    return P


OVERVIEW_MARKERS = {"rfd4": ("o", "RFD4 design"), "mpnn": ("s", "ProteinMPNN variant"), "manual": ("^", "manual variant")}


def plot_overview(df, ref_df=None, xcol="iface_pae", ycol="iptm", ax=None, color_col="binder_plddt"):
    """Two metrics plus a third dimension: the colour is the mean binder pLDDT (colour bar). Marker shape = kind: designs are circles (squares:
    ProteinMPNN, triangles: manual), the reference peptides are large stars with their name. Points that would overlap are nudged apart a little."""
    plt = _plt()
    from matplotlib.lines import Line2D
    ax = ax or plt.subplots(figsize=(7.6, 5.8))[1]
    ok = lambda t: t is not None and len(t) and xcol in t and ycol in t
    d = df.dropna(subset=[xcol, ycol]) if ok(df) else None
    r = ref_df.dropna(subset=[xcol, ycol]) if ok(ref_df) else None
    d = d if d is not None and len(d) else None
    r = r if r is not None and len(r) else None
    if d is None and r is None:
        ax.text(0.5, 0.5, "nothing to plot yet", ha="center"); return ax
    parts = [t for t in (d, r) if t is not None]
    xs = np.concatenate([t[xcol].to_numpy(float) for t in parts]); ys = np.concatenate([t[ycol].to_numpy(float) for t in parts])
    cv = np.concatenate([(t[color_col].to_numpy(float) if color_col in t else np.full(len(t), np.nan)) for t in parts])
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    px, py = max((x1 - x0) * 0.12, 1e-6 + 0.02 * abs(x1)), max((y1 - y0) * 0.12, 1e-6 + 0.02 * abs(y1))
    x0, x1, y0, y1 = x0 - px, x1 + px, y0 - py, y1 + py
    norm = lambda a, b: np.c_[(np.asarray(a, float) - x0) / (x1 - x0), (np.asarray(b, float) - y0) / (y1 - y0)]
    P0 = norm(xs, ys)
    P = _spread(P0, min_d=0.05, max_shift=0.06)
    back = lambda Q: (x0 + Q[:, 0] * (x1 - x0), y0 + Q[:, 1] * (y1 - y0))
    X, Y = back(P)
    have = np.isfinite(cv)
    vmin, vmax = (min(50.0, np.nanmin(cv)), 100.0) if have.any() else (0, 100)
    cmap = plt.get_cmap("viridis")
    nd = 0 if d is None else len(d)
    sc = None
    handles = []
    if d is not None:
        origins = d["origin"].to_numpy() if "origin" in d else np.array(["rfd4"] * nd)
        for o in dict.fromkeys(origins):
            idx = np.nonzero(origins == o)[0]
            mk, lab = OVERVIEW_MARKERS.get(o, ("o", str(o)))
            sc = ax.scatter(X[idx], Y[idx], s=95, marker=mk, c=np.where(have[idx], cv[idx], vmin), cmap=cmap, vmin=vmin, vmax=vmax,
                            edgecolors="black", linewidths=0.7, alpha=0.95, zorder=3)
            handles.append(Line2D([], [], marker=mk, ls="", color="#777777", markeredgecolor="black", markersize=9, label=lab))
    placed = []
    if r is not None:
        for m, (_, row) in enumerate(r.iterrows()):
            q = nd + m
            sc = ax.scatter([X[q]], [Y[q]], marker="*", s=330, c=[cv[q] if have[q] else vmin], cmap=cmap, vmin=vmin, vmax=vmax,
                            edgecolors="black", linewidths=1.0, zorder=5)
            if np.hypot(*(P[q] - P0[q])) > 0.008:
                ax.plot([row[xcol], X[q]], [row[ycol], Y[q]], color="#999999", lw=0.8, zorder=2)
            text = row["id"].replace("ref_", "").replace("ctrl_", "")
            w, h = 0.021 * len(text) + 0.03, 0.06
            for dx, dy in ((0.04, 0.03), (-0.04 - w, 0.03), (0.04, -0.08), (-0.04 - w, -0.08), (0.04, 0.11), (-0.04 - w, 0.11), (0.04, -0.15), (-0.04 - w, -0.15)):
                bx, by = P[q][0] + dx, P[q][1] + dy
                box = (bx, by, bx + w, by + h)
                clash = any(not (box[2] < o2[0] or box[0] > o2[2] or box[3] < o2[1] or box[1] > o2[3]) for o2 in placed)
                clash = clash or any(box[0] - 0.01 < pt[0] < box[2] + 0.01 and box[1] - 0.01 < pt[1] < box[3] + 0.01 for pt in P)
                clash = clash or box[0] < 0.0 or box[2] > 1.0 or box[1] < 0.0 or box[3] > 1.0
                if not clash:
                    break
            placed.append(box)
            lx, ly = back(np.array([[bx + (0 if dx > 0 else w), by + h / 2]]))
            ax.annotate(text, (X[q], Y[q]), xytext=(lx[0], ly[0]), fontsize=12, fontweight="bold", ha="left" if dx > 0 else "right", va="center",
                        arrowprops=dict(arrowstyle="-", color="#555555", lw=0.8), zorder=6)
        handles.append(Line2D([], [], marker="*", ls="", color="#777777", markeredgecolor="black", markersize=15, label="reference peptide"))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    pretty = lambda c: c.replace("_", " ") + (" (Å)" if "pae" in c or "rmsd" in c else "")
    ax.set_xlabel(pretty(xcol), fontsize=13); ax.set_ylabel(pretty(ycol), fontsize=13)
    ax.set_title("Candidates and reference peptides", fontsize=14)
    ax.tick_params(labelsize=12)
    if sc is not None and have.any():
        cb = ax.figure.colorbar(sc, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label("mean binder pLDDT", fontsize=12); cb.ax.tick_params(labelsize=11)
    if handles:
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=len(handles), frameon=False, fontsize=11,
                  handletextpad=0.3, columnspacing=1.2)
    return ax


def plot_interaction_heatmaps(ref):
    """Two heat maps of 6X18 contacts by interaction type (rows: any contact, aromatic, H-bond, ionic). 'Any contact' counts heavy-atom pairs
    within 4.5 A; the other rows count the interactions that the interaction engine (ProLIF, or simple distance rules if ProLIF is not
    available) finds. The colour is on a log scale so that small counts stay visible. First map: columns are the GLP-1 residues; second map:
    columns are the GLP-1R residues in contact (UniProt numbering)."""
    plt = _plt()
    pep_lab = [f"{r['aa']}{r['num']}" for r in ref["pep"]["res"]]
    rec_lab = []
    for j in ref["heat_rec_idx"]:
        r = ref["rec"]["res"][j]
        rec_lab.append(f"{r['aa']}{ref['uniprot'].get(r['num'], r['num'])}")
    fig, axs = plt.subplots(2, 1, figsize=(max(10.0, 0.5 * max(len(pep_lab), len(rec_lab)) + 3.0), 9.0))
    eng = ref.get("interaction_engine", "")
    for ax, M, labs, title in ((axs[0], ref["heat_pep"], pep_lab, "GLP-1 side: interactions per GLP-1 residue (letter + number in the structure)"),
                               (axs[1], ref["heat_rec"], rec_lab, "GLP-1R side: interactions per receptor residue (letter + UniProt number)")):
        L = np.log1p(M)
        ax.imshow(L, cmap="Oranges", aspect="auto", vmin=0, vmax=max(L.max(), 1e-6))
        ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, rotation=90, fontsize=12)
        ax.set_yticks(range(len(KIND_ROWS))); ax.set_yticklabels(KIND_ROWS, fontsize=13)
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                if M[i, j] > 0:
                    ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=11, color="white" if L[i, j] > 0.65 * L.max() else "black")
        ax.set_title(title + (f"  [{eng}]" if eng and ax is axs[0] else ""), fontsize=14)
    fig.tight_layout()
    return fig


def rfd4_columns(df):
    return [c for c in df.columns if c.startswith("rfd4_") and df[c].notna().any()]


def rfd4_table(df):
    """The columns that exist before any OpenFold3 run: the RFD4-Proteina metrics and the contacts of the design file itself."""
    cols = ["id", "binder_len"] + rfd4_columns(df) + [c for c in ("des_hotspot_hits", "des_site_overlap", "des_site_cover", "des_n_clash", "des_min_dist", "liabilities") if c in df]
    return df[[c for c in cols if c in df]]


def compare_table(df, ref_df=None):
    """RFD4-Proteina metrics and design contacts (des_*) next to the OpenFold3 metrics; reference peptides (OpenFold3 only) below."""
    first = ["id"] + rfd4_columns(df) + [c for c in ("des_hotspot_hits", "des_site_overlap", "des_n_clash") if c in df]
    of3 = [c for c in ("iptm", "ptm", "binder_plddt", "iface_pae", "ipsae", "backbone_rmsd", "pose_rmsd", "hotspot_hits", "site_overlap", "n_clash", "checks") if c in df]
    out = df[first + of3]
    if ref_df is not None and len(ref_df):
        r = ref_df[[c for c in ["id"] + of3 if c in ref_df]]
        out = pd.concat([out, r], ignore_index=True)
    return out


def plot_rfd4_overview(df, max_panels=6):
    """One bar chart per RFD4-Proteina metric (designs on the horizontal axis, in the order of the table)."""
    plt = _plt()
    cols = rfd4_columns(df)[:max_panels]
    if not cols:
        fig, ax = plt.subplots(figsize=(5, 1.5)); ax.text(0.5, 0.5, "the server returned no numeric design metrics", ha="center"); ax.axis("off"); return fig
    n = len(cols); nc = min(2, n); nr = (n + nc - 1) // nc
    fig, axs = plt.subplots(nr, nc, figsize=(7.2 * nc, 4.0 * nr), squeeze=False)
    labs = [str(i).split("_")[-1] for i in df["id"]]
    for ax, c in zip(axs.ravel(), cols):
        ax.bar(range(len(df)), df[c], color="#1D9A78")
        ax.set_xticks(range(len(df))); ax.set_xticklabels(labs, fontsize=12, rotation=90)
        ax.set_xlabel("design number", fontsize=12)
        ax.set_title(c.replace("rfd4_", ""), fontsize=14)
        ax.tick_params(axis="y", labelsize=12)
    for ax in axs.ravel()[n:]:
        ax.axis("off")
    fig.tight_layout()
    return fig


def plot_rfd4_vs_of3(df, rfd4_col=None, ycols=("iptm", "iface_pae")):
    """RFD4-Proteina metric (horizontal) against the OpenFold3 metrics (vertical). Rank correlation in the title."""
    plt = _plt()
    cols = rfd4_columns(df)
    rfd4_col = rfd4_col if rfd4_col in df else (cols[0] if cols else None)
    fig, axs = plt.subplots(1, len(ycols), figsize=(6.4 * len(ycols), 5.2), squeeze=False)
    for ax, y in zip(axs[0], ycols):
        plot_xy(ax, df, rfd4_col, y)
    fig.tight_layout()
    return fig


def plot_xy(ax, df, xcol, ycol, label_col="id"):
    """One panel: xcol against ycol for the designs, each dot labelled with the design number, rank correlation in the title."""
    if xcol is None or ycol is None or xcol not in df or ycol not in df or df[ycol].notna().sum() < 2:
        ax.text(0.5, 0.5, "needs the RFD4 metrics and the OpenFold3 run", ha="center"); ax.axis("off"); return ax
    d = df.dropna(subset=[xcol, ycol])
    ax.scatter(d[xcol], d[ycol], s=70, color="#1D9A78", edgecolors="black", linewidths=0.6, zorder=3)
    for _, r in d.iterrows():
        ax.annotate(str(r[label_col]).split("_")[-1], (r[xcol], r[ycol]), fontsize=11, xytext=(4, 4), textcoords="offset points")
    rho = d[xcol].corr(d[ycol], method="spearman") if len(d) >= 3 and d[xcol].nunique() > 1 and d[ycol].nunique() > 1 else float("nan")
    nice = lambda c: c.replace("rfd4_", "RFD4: ").replace("des_", "design: ").replace("_", " ")
    ax.set_xlabel(nice(xcol), fontsize=13); ax.set_ylabel("OpenFold3: " + ycol.replace("_", " ") if ycol in OF3_COLS else nice(ycol), fontsize=13)
    ax.set_title(f"rank correlation {rho:.2f}" if rho == rho else "too few points", fontsize=14)
    ax.tick_params(labelsize=12)
    return ax


OF3_COLS = ["iptm", "ptm", "binder_plddt", "iface_pae", "ipsae", "backbone_rmsd", "pose_rmsd", "hotspot_hits", "site_overlap", "site_cover", "n_clash"]


def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    return base64.b64encode(buf.getvalue()).decode()


# =====================================================================================
#  3D viewer
# =====================================================================================
LAYER_COLORS = ["#E6194B", "#3CB44B", "#4363D8", "#F58231", "#911EB4", "#17BECF", "#F032E6", "#9A6324", "#469990", "#808000",
                "#000075", "#E377C2", "#8C564B", "#7F7F7F", "#BCBD22", "#1F77B4", "#AEC7E8", "#FFBB78", "#98DF8A", "#C5B0D5"]
LINE_COL = {"H-bond": "#2B6FD6", "ionic": "#D62728", "aromatic": "#8E44AD"}
_LAYER_CHAINS = [c for c in "BCDEFGHIJKLMNOPQSTUVWXYZ"]


def interaction_lines(rec, bind, cutoff=4.5, kinds=("H-bond", "ionic", "aromatic"), max_lines=70):
    """Potential interactions between receptor and binder for the 3D view: per residue pair and kind the closest atom pair."""
    cd = contact_detail(rec, bind, cutoff, interactions=True)
    out = []
    for (j, b), e in cd.items():
        for k in kinds:
            if k in e["best"]:
                dd, xa, xb = e["best"][k]
                out.append(dict(kind=k, d=dd, a=xa, b=xb, res=(j, b)))
    out.sort(key=lambda x: x["d"])
    return out[:max_lines]


def hover_js(labels):
    """JavaScript for py3Dmol: show a label with the residue name and numbers while the mouse is over an atom."""
    show = ("function(atom,viewer,event,container){var L=" + json.dumps(labels) + ";var t=L[atom.chain+':'+atom.resi];"
            "if(t&&!atom.label){atom.label=viewer.addLabel(t,{position:atom,backgroundColor:'white',fontColor:'black',fontSize:12,"
            "borderColor:'#777',borderThickness:1,backgroundOpacity:0.92});}}")
    hide = "function(atom,viewer){if(atom.label){viewer.removeLabel(atom.label);delete atom.label;}}"
    return show, hide


def _style_binder(v, cid, color, opacity=1.0):
    sel = {"chain": cid}
    if color == "plddt":
        v.setStyle(sel, {"cartoon": {"colorscheme": {"prop": "b", "gradient": "roygb", "min": 50, "max": 90}, "opacity": opacity}})
    elif isinstance(color, dict) and color.get("kind") == "fixed":
        v.setStyle(sel, {"cartoon": {"color": "#8BC145"}})
        if color.get("fixed"):
            v.setStyle({"chain": cid, "resi": list(color["fixed"])}, {"cartoon": {"color": "#B74919"}, "stick": {"colorscheme": "orangeCarbon", "radius": 0.15}})
    elif isinstance(color, dict) and color.get("kind") == "class":
        v.setStyle(sel, {"cartoon": {"color": "#8BC145"}})
        for cls, col in (("interface", "#B74919"), ("core", "#1D6FA9"), ("surface", "#8BC145")):
            ids = [q for q, c in color["classes"].items() if c == cls]
            if ids:
                v.setStyle({"chain": cid, "resi": ids}, {"cartoon": {"color": col}})
    else:
        v.setStyle(sel, {"cartoon": {"color": color or "#1D9A78", "opacity": opacity}})


class _Rec:
    """Stand-in for a py3Dmol view that only records the calls (used to replay a scene in a page of our own, see layers_html)."""
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        def f(*a, **k):
            self.calls.append((name, a, k))
        return f


def view_layers(layers, ref, hotspots=(), height=520, width=720, receptor_radius=8.0, _view=None):
    """One py3Dmol view with the receptor of the first layer and the binder of every layer (each binder gets its own chain id).
    Every layer: text (PDB text with chains R and B, already moved onto the 6X18 receptor), name, color ('plddt', '#rrggbb' or a dict),
    opacity, lines (dashed potential interactions), sticks ('contacts' or 'all'), numbers (numbers to show instead of 1..n), tag (text in the label).
    Hover labels: receptor residues show the residue and its UniProt number, binder residues the residue and its position."""
    if _view is None:
        try:
            import py3Dmol
        except ImportError:
            print("py3Dmol is not installed: run  pip install py3Dmol  in a cell and restart the kernel.")
            return None
    merged, labels, binders = [], {}, []
    for k, L in enumerate(layers):
        atoms = parse_pdb(L["text"])
        rec, bind = get_chain(atoms, REC), get_chain(atoms, BIND)
        cid = _LAYER_CHAINS[k]
        if k == 0:
            merged += [a for a in atoms if a[0] == REC]
            rec0 = rec
        merged += [(cid,) + a[1:] for a in atoms if a[0] == BIND]
        binders.append((cid, rec, bind, L))
        for m, r in enumerate(bind["res"]):
            disp = L["numbers"][m] if L.get("numbers") and m < len(L["numbers"]) else r["num"]
            labels[f"{cid}:{r['num']}"] = f"{L.get('name', '')}: {r['resname'].title()}{disp}" + (f" · {L['tag']}" if L.get("tag") else "")
    v = _view if _view is not None else py3Dmol.view(width=width, height=height)
    v.addModel(atoms_to_pdb(merged), "pdb")
    v.setStyle({"chain": REC}, {"cartoon": {"color": "#C9CED6", "opacity": 0.85}})
    allb = np.vstack([b["xyz"] for _, _, b, _ in binders if len(b["xyz"])])
    dmin = dist_matrix(rec0["xyz"], allb).min(1)
    near, touch = set(), set()
    for i, dd in enumerate(dmin):
        n = rec0["res"][int(rec0["ri"][i])]["num"]
        if dd < receptor_radius:
            near.add(n)
        if dd < 4.5:
            touch.add(n)
    names = {r["num"]: r["resname"].title() for r in rec0["res"]}
    for n in near:
        u = ref["uniprot"].get(n, n)
        labels[f"{REC}:{n}"] = f"{names[n]}{u} · UniProt {u}" + (f" (PDB {n})" if u != n else "")
    if touch:
        v.addStyle({"chain": REC, "resi": sorted(touch)}, {"stick": {"colorscheme": "cyanCarbon", "radius": 0.14}})
    if near:
        v.addStyle({"chain": REC, "resi": sorted(near), "atom": "CA"}, {"sphere": {"color": "#7C8794", "radius": 0.45, "opacity": 0.75}})
    nums = [int(str(h).split(":")[-1]) for h in hotspots]
    if nums:
        v.addStyle({"chain": REC, "resi": nums}, {"stick": {"colorscheme": "magentaCarbon", "radius": 0.22}})
        v.addStyle({"chain": REC, "resi": nums}, {"sphere": {"color": "magenta", "opacity": 0.3, "radius": 1.6}})
    any_lines = False
    for cid, rec, bind, L in binders:
        col = L.get("color", "#1D9A78")
        _style_binder(v, cid, col, L.get("opacity", 1.0))
        bead = col if isinstance(col, str) and col.startswith("#") else "#1D9A78"
        v.addStyle({"chain": cid, "atom": "CA"}, {"sphere": {"color": bead, "radius": 0.42, "opacity": 0.9}})
        if L.get("sticks") == "all":
            v.addStyle({"chain": cid}, {"stick": {"radius": 0.12}})
        if L.get("lines"):
            lines = interaction_lines(rec, bind)
            for ln in lines:
                a, b = ln["a"], ln["b"]
                v.addCylinder({"start": {"x": a[0], "y": a[1], "z": a[2]}, "end": {"x": b[0], "y": b[1], "z": b[2]}, "radius": 0.07,
                               "color": LINE_COL[ln["kind"]], "dashed": True, "dashLength": 0.25, "gapLength": 0.18, "fromCap": 1, "toCap": 1})
            any_lines = any_lines or bool(lines)
            touched = sorted({bind["res"][b]["num"] for (_, b) in [x["res"] for x in lines]})
            if touched and L.get("sticks") != "all":
                v.addStyle({"chain": cid, "resi": touched}, {"stick": {"radius": 0.13}})
    show, hide = hover_js(labels)
    v.setHoverable({}, True, show, hide)
    legend = "Hover over a bead (Cα) or stick for the residue label."
    if any_lines:
        legend = "Dashed lines: blue = H-bond, red = ionic, purple = aromatic.  " + legend
    v.addLabel(legend, {"fontSize": 11, "fontColor": "black", "backgroundColor": "white", "backgroundOpacity": 0.75, "useScreen": True,
                        "alignment": "topLeft", "position": {"x": 4, "y": 4, "z": 0}})
    v.zoomTo({"chain": binders[0][0]})
    return v


def view_complex(model_text, ref, color="plddt", hotspots=(), fixed=None, crystal_text=None, height=480, extra_layers=(), name="model"):
    """A model (already on the 6X18 receptor) in 3D: receptor grey, binder coloured by pLDDT ('plddt'), by fixed residues ('fixed'),
    by class ('class') or one colour; optionally the crystal GLP-1 and more binders for comparison. Dashed lines show potential
    interactions of the first binder."""
    if color == "fixed" and fixed is not None:
        col = dict(kind="fixed", fixed=list(fixed))
    elif color == "class" and isinstance(fixed, dict):
        col = dict(kind="class", classes=fixed)
    else:
        col = color if color in ("plddt",) or str(color).startswith("#") else "#1D9A78"
    layers = [dict(text=model_text, name=name, color=col, lines=True)]
    if crystal_text:
        layers.append(dict(text=crystal_text, name="GLP-1 (6X18)", color="#F19D19", opacity=0.6,
                           numbers=[r["num"] for r in ref["pep"]["res"]]))
    layers += list(extra_layers)
    return view_layers(layers, ref, hotspots, height)


def model_text_with_plddt(model_path, conf):
    """Model text whose B-factors are the per-residue pLDDT, so that the viewer colours by confidence."""
    atoms = parse_pdb(Path(model_path).read_text())
    rec, bind = get_chain(atoms, REC), get_chain(atoms, BIND)
    pl = residue_plddt(conf, rec, bind)
    keys = [(REC, r["num"], r["icode"]) for r in rec["res"]] + [(BIND, r["num"], r["icode"]) for r in bind["res"]]
    return atoms_to_pdb(atoms, bfac=dict(zip(keys, map(float, pl)))), pl, len(rec["res"])


# =====================================================================================
#  Simple interfaces (ipywidgets)
# =====================================================================================
CLS_COLOR = {"interface": "#F3B792", "core": "#BCD6E8", "surface": "#E4E4E4"}


def _w():
    import ipywidgets as w
    from IPython.display import display, HTML, clear_output
    return w, display, HTML, clear_output


class HotspotPicker:
    """Choose hotspot residues on GLP-1R: a preset, a list of the residues GLP-1 touches in 6X18, and a box for your own."""
    def __init__(self, ref, default=None):
        w, display, HTML, clear_output = _w()
        self.ref = ref
        names = list(ref["presets"])
        default = default or names[0]
        opts = []
        for e in sorted(ref["per_rec"].values(), key=lambda e: -e["n"]):
            lab = f"{e['id']}  {e['aa3']}   {e['n']} atom contacts   GLP-1 position {', '.join(str(p + 1) for p in sorted(e['pep_pos']))}"
            opts.append((lab, e["id"]))
        self.preset = w.Dropdown(options=names + ["custom"], value=default, description="Preset", layout=w.Layout(width="760px"))
        self.sel = w.SelectMultiple(options=opts, value=tuple(ref["presets"][default]), rows=10, description="Residues",
                                    layout=w.Layout(width="760px"))
        self.extra = w.Text(value="", description="Add by hand", placeholder="e.g. R:120, 125-127", layout=w.Layout(width="760px"))
        self.info = w.HTML()
        self.hint = w.HTML("<i>To select several residues in the list (custom preset): hold <b>Cmd</b> (Mac) or <b>Ctrl</b> (Windows) while you click; "
                           "<b>Shift</b>-click selects a range.</i>")
        self._lock = False
        self.preset.observe(self._on_preset, names="value")
        self.sel.observe(self._update, names="value")
        self.extra.observe(self._update, names="value")
        display(w.VBox([self.preset, self.sel, self.hint, self.extra, self.info]))
        self._update()

    def _on_preset(self, change):
        if change["new"] in self.ref["presets"]:
            self.sel.value = tuple(self.ref["presets"][change["new"]])
        self._update()

    def _extra_ids(self):
        have = set(self.ref["rec_nums"])
        ok, bad = [], []
        try:
            for n in parse_ranges(self.extra.value):
                (ok if n in have else bad).append(n)
        except ValueError as e:
            return [], [str(e)]
        return ok, bad

    @property
    def value(self):
        ids = set(self.sel.value)
        ids |= {f"{REC}:{n}" for n in self._extra_ids()[0]}
        return sorted(ids, key=lambda s: int(s.split(":")[1]))

    def _update(self, *_):
        v = self.value
        ok, bad = self._extra_ids()
        msg = f"<b>{len(v)} hotspots:</b> {', '.join(v) if v else 'none yet'}"
        if bad:
            msg += f"<br><span style='color:#B74919'>Not in the receptor model or not readable: {', '.join(map(str, bad))}</span>"
        if len(v) < 3:
            msg += "<br><span style='color:#B74919'>Choose at least 3 hotspots.</span>"
        elif len(v) > 8:
            msg += "<br><span style='color:#B74919'>More than 8 hotspots over-constrains the design; 3 to 8 works best.</span>"
        self.info.value = msg


class FixPicker:
    """Choose which binder residues stay fixed in ProteinMPNN. Presets, a list, and boxes for manual fixes and overrides."""
    def __init__(self, classes, seq, view_cb=None, temperature=0.2):
        w, display, HTML, clear_output = _w()
        self.classes, self.seq, self.view_cb = classes, seq, view_cb
        self.cls = {c["pos"]: c["cls"] for c in classes}
        opts = [(f"{c['pos']:>3}  {c['aa']}   {c['cls']}", c["pos"]) for c in classes]
        self.sel = w.SelectMultiple(options=opts, value=tuple(c["pos"] for c in classes if c["cls"] == "interface"), rows=12,
                                    description="Fixed", layout=w.Layout(width="360px"))
        self.fix_extra = w.Text(description="Also fix", placeholder="e.g. 5-12, 40", layout=w.Layout(width="360px"))
        self.free_extra = w.Text(description="Make free", placeholder="e.g. 7, 20-22", layout=w.Layout(width="360px"))
        self.temp = w.FloatSlider(value=temperature, min=0.1, max=0.5, step=0.05, description="Temperature", readout_format=".2f",
                                  layout=w.Layout(width="360px"))
        self.strip = w.HTML()
        self.out = w.Output()
        self.buttons = {}
        for label, fn in (("Fix interface", lambda: self._set("interface")), ("Fix core", lambda: self._set("core")),
                          ("Fix interface + core", lambda: self._set("interface", "core")), ("Fix nothing", lambda: self._set()),
                          ("Fix everything", lambda: self._set("interface", "core", "surface"))):
            b = w.Button(description=label, layout=w.Layout(width="150px"))
            b.on_click(lambda _b, fn=fn: fn())
            self.buttons[label] = b
        self.view_btn = w.Button(description="Show in 3D", button_style="info")
        self.view_btn.on_click(lambda _b: self._view())
        for x in (self.sel, self.fix_extra, self.free_extra):
            x.observe(self._update, names="value")
        left = w.VBox([w.HBox(list(self.buttons.values())[:3]), w.HBox(list(self.buttons.values())[3:]), self.sel,
                       self.fix_extra, self.free_extra, self.temp, self.view_btn])
        display(w.VBox([left, self.strip, w.HTML("<i>If <b>Show in 3D</b> shows nothing (it can happen in Google Colab), run the cell below the picker.</i>"), self.out]))
        self._update()

    def _set(self, *classes):
        self.fix_extra.value = ""
        self.free_extra.value = ""
        self.sel.value = tuple(p for p, c in self.cls.items() if c in classes)

    def _parse(self, text):
        try:
            return set(parse_ranges(text, 1, len(self.seq))), None
        except ValueError as e:
            return set(), str(e)

    @property
    def fixed(self):
        add, _ = self._parse(self.fix_extra.value)
        free, _ = self._parse(self.free_extra.value)
        return sorted((set(self.sel.value) | add) - free)

    @property
    def temperature(self):
        return float(self.temp.value)

    def _update(self, *_):
        fx = set(self.fixed)
        spans = []
        for i, a in enumerate(self.seq, 1):
            st = f"background:{CLS_COLOR[self.cls[i]]};padding:1px 2px;"
            st += "font-weight:700;border-bottom:3px solid #222;" if i in fx else "color:#555;"
            spans.append(f"<span style='{st}'>{a}</span>" + ("<span style='color:#999'>&nbsp;</span>" if i % 10 == 0 else ""))
        legend = " ".join(f"<span style='background:{c};padding:1px 6px'>{k}</span>" for k, c in CLS_COLOR.items())
        err = [e for e in (self._parse(self.fix_extra.value)[1], self._parse(self.free_extra.value)[1]) if e]
        warn = ""
        if err:
            warn = f"<br><span style='color:#B74919'>{err[0]}</span>"
        if len(fx) == len(self.seq):
            warn += "<br><span style='color:#B74919'>Everything is fixed: ProteinMPNN has nothing to change.</span>"
        self.strip.value = (f"<div style='font-family:monospace;font-size:15px;line-height:1.8;margin-top:8px'>{''.join(spans)}</div>"
                            f"<div style='font-size:12px'>{legend} &nbsp; <b>bold + underline = fixed</b> ({len(fx)} fixed, {len(self.seq) - len(fx)} free)</div>{warn}")

    def _view(self):
        w, display, HTML, clear_output = _w()
        with self.out:
            clear_output(wait=True)
            if self.view_cb:
                self.view_cb(self.fixed)


class Form:
    """A few text boxes. form.values() returns the answers; form.check(n) says which are too short."""
    def __init__(self, questions, rows=2, width="900px"):
        w, display, HTML, clear_output = _w()
        self.keys = list(questions)
        self.boxes = {k: w.Textarea(value="", placeholder=q, description="", rows=rows, layout=w.Layout(width=width)) for k, q in questions.items()}
        items = []
        for k, q in questions.items():
            items += [w.HTML(f"<b>{q}</b>"), self.boxes[k]]
        display(w.VBox(items))

    def values(self):
        return {k: b.value.strip() for k, b in self.boxes.items()}

    def check(self, n=15):
        return [k for k, v in self.values().items() if len(v) < n]


class Chooser:
    """A drop-down or a multi-select over candidates with a one-line summary each."""
    def __init__(self, df, multiple=False, max_pick=2, sort="iptm", ascending=None, description="Candidate"):
        w, display, HTML, clear_output = _w()
        if ascending is None:
            ascending = sort in ("iface_pae", "backbone_rmsd", "pose_rmsd", "n_clash", "min_dist")
        d = df.sort_values(sort, ascending=ascending, na_position="last") if sort in df else df
        opts = []
        for _, r in d.iterrows():
            def f(c, fmt):
                v = r.get(c)
                return format(v, fmt) if v is not None and not (isinstance(v, float) and math.isnan(v)) else "n/a"
            opts.append((f"{r['id']}   ipTM {f('iptm', '.2f')}   pLDDT {f('binder_plddt', '.0f')}   iPAE {f('iface_pae', '.1f')}   checks {r.get('checks', '') or 'n/a'}", r["id"]))
        self.multiple, self.max_pick = multiple, max_pick
        layout = w.Layout(width="900px")
        if multiple:
            self.w = w.SelectMultiple(options=opts, rows=min(10, max(4, len(opts))), description=description, layout=layout)
        else:
            self.w = w.Dropdown(options=opts, description=description, layout=layout)
        self.opts = opts
        display(self.w)

    @property
    def value(self):
        v = self.w.value
        return list(v) if self.multiple else v


def sequence_strip_html(seq, fixed):
    fx = set(fixed)
    return "".join(f"<span style='font-family:monospace;{'font-weight:700;border-bottom:3px solid #222;' if i in fx else 'color:#555;'}'>{a}</span>"
                   for i, a in enumerate(seq, 1))


# =====================================================================================
#  Schedule helpers, residue inspector, crystal view
# =====================================================================================
CLUSTERS = {1: [1, 2], 2: [3, 4], 3: [5, 6], 4: [7, 8], 5: [9, 10]}


def cluster_of(group):
    g = int(group)
    for c, gs in CLUSTERS.items():
        if g in gs:
            return c
    return None


def slot_for(group, first="14:10", step_s=90):
    """Start of this group's submission slot: groups are spread out so the GPUs are not hit by 10 jobs in the same minute."""
    h, m = map(int, first.split(":"))
    t = h * 3600 + m * 60 + (int(group) - 1) * step_s
    return f"{t // 3600:02d}:{(t % 3600) // 60:02d}:{t % 60:02d}"


def residue_contacts(model_text, pos, ref, cutoff=4.5):
    """Receptor residues touching binder residue `pos` (1-based) in a model, with interaction kinds,
    and whether GLP-1 touches the same receptor residue in the crystal."""
    atoms = parse_pdb(model_text)
    rec, bind = get_chain(atoms, REC), get_chain(atoms, BIND)
    if not 1 <= pos <= len(bind["res"]):
        raise ValueError(f"binder position must be 1 to {len(bind['res'])}")
    cd = contact_detail(rec, bind, cutoff, interactions=True)
    rows = []
    for (j, b), e in cd.items():
        if b == pos - 1:
            rr = rec["res"][j]
            rows.append(dict(receptor=f"{REC}:{rr['num']}", aa=rr["aa"], atom_pairs=e["n"], closest_A=round(e["dmin"], 2),
                             interactions=", ".join(sorted(e["kinds"])), touched_by_GLP1_in_6X18=rr["num"] in ref["footprint"]))
    cols = ["receptor", "aa", "atom_pairs", "closest_A", "interactions", "touched_by_GLP1_in_6X18"]
    return pd.DataFrame(rows, columns=cols).sort_values("atom_pairs", ascending=False).reset_index(drop=True)


def view_crystal(ref, hotspots=(), height=460):
    """6X18: receptor grey, GLP-1 orange, receptor residues within 4.5 A cyan, dashed lines for potential interactions."""
    layers = [dict(text=crystal_as_design(ref), name="GLP-1", color="#F19D19", lines=True, sticks="all",
                   numbers=[r["num"] for r in ref["pep"]["res"]])]
    return view_layers(layers, ref, hotspots, height)


def align_pairs(sa, sb):
    """Residue pairs (i, j) of two similar sequences: identical stretches and equal-length stretches with substitutions."""
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    pairs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            pairs += [(i1 + k, j1 + k) for k in range(i2 - i1)]
    return pairs


def delta_table(df, parent_id):
    """Change of the main metrics of every row relative to its parent row (NaN if either is missing)."""
    base = df[df["id"] == parent_id]
    if base.empty:
        return df.assign()
    b = base.iloc[0]
    out = df[["id", "sequence"]].copy()
    out["n_changed"] = [sequence_changes(b["sequence"], s)[0] if len(s) == len(b["sequence"]) else None for s in df["sequence"]]
    for c in ("iptm", "binder_plddt", "iface_pae", "ipsae", "pose_rmsd", "hotspot_hits"):
        if c in df:
            out["d_" + c] = (df[c] - b[c]).round(3)
    return out


def apply_mutations(seq, text, max_n=5):
    """'A12K, L20D' (old letter, position, new letter) -> new sequence. Raises ValueError with a plain message."""
    items = [t for t in re.split(r"[,\s;]+", text.strip()) if t]
    if not items:
        raise ValueError("no mutations written")
    if len(items) > max_n:
        raise ValueError(f"at most {max_n} manual changes per variant")
    s = list(seq); seen = set()
    for t in items:
        m = re.fullmatch(r"([A-Za-z])(\d+)([A-Za-z])", t)
        if not m:
            raise ValueError(f"cannot read '{t}': write old letter, position, new letter, e.g. A12K")
        old, pos, new = m.group(1).upper(), int(m.group(2)), m.group(3).upper()
        if not 1 <= pos <= len(s):
            raise ValueError(f"position {pos} is outside the binder (1 to {len(s)})")
        if pos in seen:
            raise ValueError(f"position {pos} appears twice")
        if s[pos - 1] != old:
            raise ValueError(f"position {pos} is {s[pos - 1]} in this sequence, not {old}")
        if new not in AA:
            raise ValueError(f"'{new}' is not one of the 20 amino acids")
        seen.add(pos); s[pos - 1] = new
    return "".join(s)


def plot_footprint(ref, ax=None, hotspots=()):
    """Atom contacts per GLP-1 position in 6X18, split by interaction kind."""
    plt = _plt()
    ax = ax or plt.subplots(figsize=(9.0, 3.8))[1]
    t = ref["table"]
    n = len(ref["pep_seq"])
    tot = np.zeros(n)
    for _, r in t.iterrows():
        tot[int(r["glp1_pos"]) - 1] += r["atom_pairs"]
    ax.bar(range(1, n + 1), tot, color="#B74919")
    ax.set_xticks(range(1, n + 1)); ax.set_xticklabels(list(ref["pep_seq"]), fontsize=11)
    ax.set_xlabel("GLP-1 residue (one-letter code, position 1 to %d)" % n); ax.set_ylabel("heavy-atom contacts to GLP-1R")
    ax.set_title("Which GLP-1 residues touch the receptor in 6X18 (4.5 Å)", fontsize=13)
    return ax


def plot_lineage(df, ax=None, ycol="iptm"):
    """Metric of every design by round; lines join each design to its parent."""
    plt = _plt()
    ax = ax or plt.subplots(figsize=(7.2, 5))[1]
    d = df[df[ycol].notna()]
    pos = {r["id"]: (float(r["round"] or 0), float(r[ycol])) for _, r in d.iterrows()}
    rng = np.random.default_rng(0)
    jit = {k: (v[0] + rng.uniform(-0.18, 0.18), v[1]) for k, v in pos.items()}
    for _, r in d.iterrows():
        p = r.get("parent")
        if p in jit:
            ax.plot([jit[p][0], jit[r["id"]][0]], [jit[p][1], jit[r["id"]][1]], color="#bbb", lw=0.5, zorder=1)
    colors = {"rfd4": "#1D9A78", "mpnn": "#B74919", "manual": "#44546A"}
    for o, g in d.groupby("origin"):
        ax.scatter([jit[i][0] for i in g["id"]], g[ycol], s=60, color=colors.get(o, "#44546A"), label=o, zorder=2)
    ax.set_xticks(sorted({int(v[0]) for v in pos.values()}))
    ax.set_xlabel("round (0 = RFD4-Proteina)"); ax.set_ylabel(ycol); ax.legend(fontsize=11)
    ax.set_title(f"{ycol} along the design history", fontsize=13)
    return ax


# =====================================================================================
#  Candidate card (one-page HTML) and files
# =====================================================================================
def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def candidate_card_html(group, nominee, hist, refs, state, pae_b64="", pl_b64="", overview_b64=""):
    def fmt(v, f="{:.2f}"):
        return "n/a" if v is None or (isinstance(v, float) and math.isnan(v)) else f.format(v)
    keys = [("ipTM", "iptm", "{:.2f}"), ("pTM", "ptm", "{:.2f}"), ("binder pLDDT", "binder_plddt", "{:.0f}"),
            ("interface PAE (Å)", "iface_pae", "{:.1f}"), ("ipSAE", "ipsae", "{:.2f}"), ("backbone RMSD (Å)", "backbone_rmsd", "{:.1f}"),
            ("pose RMSD (Å)", "pose_rmsd", "{:.1f}"), ("hotspots touched", "hotspot_frac", "{:.2f}"),
            ("overlap with GLP-1 site", "site_overlap", "{:.2f}")]
    rows = "".join(f"<tr><td>{a}</td><td><b>{fmt(nominee.get(k), f)}</b></td>" +
                   "".join(f"<td>{fmt(r.get(k), f)}</td>" for _, r in refs.iterrows()) + "</tr>" for a, k, f in keys)
    head = "".join(f"<th>{_esc(r['id'].replace('ref_', '').replace('ctrl_', ''))}</th>" for _, r in refs.iterrows())
    lineage = []
    cur = nominee.get("id")
    byid = {r["id"]: r for _, r in hist.iterrows()}
    while cur and cur in byid:
        lineage.append(f"{cur} (round {int(byid[cur].get('round') or 0)})")
        cur = byid[cur].get("parent")
    rounds = "".join(f"<li><b>Round {r.get('round')}</b>: parent {_esc(r.get('parent'))}; fixed {_esc(len(r.get('fixed', [])))} positions; "
                     f"decision <b>{_esc(r.get('decision', ''))}</b>. {_esc(r.get('conclusion', ''))}</li>" for r in state.get("rounds", []))
    imgs = "".join(f"<img src='data:image/png;base64,{b}' style='height:250px'>" for b in (pae_b64, pl_b64, overview_b64) if b)
    s = state
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{_esc(group)} candidate card</title>
<style>body{{font-family:Calibri,Arial,sans-serif;max-width:1000px;margin:20px auto;color:#222}}h1{{color:#901A1E;font-size:26px;margin-bottom:0}}
table{{border-collapse:collapse;margin:6px 0}}td,th{{border:1px solid #ccc;padding:3px 8px;font-size:13px;text-align:right}}td:first-child{{text-align:left}}
.seq{{font-family:monospace;word-break:break-all;background:#f3f3f3;padding:6px}}.note{{background:#fbeee6;padding:6px 10px;font-size:13px}}</style></head><body>
<h1>Candidate card: {_esc(nominee.get('id'))}</h1><div>Group {_esc(group)} · GLP-1R (6X18) · {_esc(now_stamp())}</div>
<p class='note'>All numbers are computed predictions (RFD4-Proteina, ProteinMPNN, OpenFold3), not measurements. Teaching thresholds are a starting point.</p>
<h3>Sequence ({len(nominee.get('sequence', ''))} residues)</h3><div class='seq'>{_esc(nominee.get('sequence', ''))}</div>
<div>Lineage: {' ← '.join(lineage)}</div>
<h3>Metrics against the reference peptides</h3><table><tr><th></th><th>this candidate</th>{head}</tr>{rows}</table>
<div>{imgs}</div>
<h3>What we expected and what we saw</h3><ul><li><b>Hotspots</b>: {_esc(', '.join(s.get('hotspots', [])))}</li>
<li><b>Hypothesis for generation</b>: {_esc(s.get('gen_hypothesis', {}).get('text', ''))}</li>{rounds}</ul>
<h3>Evidence and doubt</h3><ul><li><b>Strongest evidence</b>: {_esc(s.get('final', {}).get('evidence', ''))}</li>
<li><b>Biggest weakness</b>: {_esc(s.get('final', {}).get('weakness', ''))}</li>
<li><b>Open uncertainty</b>: {_esc(s.get('final', {}).get('uncertainty', ''))}</li>
<li><b>Next experiment</b>: {_esc(s.get('final', {}).get('next_experiment', ''))}</li></ul></body></html>"""


# =====================================================================================
#  Google Colab support (everything here also works in plain Jupyter)
# =====================================================================================
def in_colab():
    return "google.colab" in sys.modules


def workspace_root(save_to="drive", drive_dir=None, log=print):
    """Folder for all files of the workshop. In Colab with save_to='drive' it is a folder in the user's Google Drive, so the
    work survives a disconnected runtime (for example after the break). The Drive itself is mounted in its own cell (0.3):
    the permission pop-up only works when drive.mount is the visible code of a cell. Falls back to the local folder with a warning."""
    drive_dir = drive_dir or os.environ.get("WS3_DRIVE_DIR", "/content/drive/MyDrive")
    if save_to == "drive" and in_colab():
        if Path(drive_dir).exists():
            root = Path(drive_dir) / "ws3_data"
            root.mkdir(parents=True, exist_ok=True)
            log(f"Saving to your Google Drive: {root}")
            return str(root)
        log("Your Google Drive is not mounted. Run cell 0.3 on its own and accept the pop-up (or set SAVE_TO to local). "
            "Until then your work is saved in this Colab session only: a disconnected runtime loses it.")
    elif save_to == "drive":
        log("Not running in Colab: saving in the local folder ws3_data.")
    return "ws3_data"


def download_url(url, dest):
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    return dest


def offer_download(folder, name=None, log=print):
    """Zip a folder; in Colab start the browser download, elsewhere just say where the zip is."""
    folder = Path(folder)
    zpath = shutil.make_archive(str(folder.parent / (name or folder.name)), "zip", str(folder))
    if in_colab():
        try:
            from google.colab import files
            files.download(zpath)
            log(f"Download started: {Path(zpath).name}")
            return zpath
        except Exception as e:
            log(f"Automatic download failed ({str(e)[:60]}). Use the file browser on the left (folder icon) to download {zpath}.")
    else:
        log(f"Zip written: {zpath}")
    return zpath


def cluster_order(M, similarity=False):
    """Row/column order from hierarchical clustering (average linkage) of a square matrix. Returns (order, linkage matrix or None)."""
    n = len(M)
    if n < 3:
        return list(range(n)), None
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform
    A = np.array(M, float)
    A = np.where(np.isfinite(A), A, np.nanmax(A[np.isfinite(A)]) if np.isfinite(A).any() else 0.0)
    Dm = (1.0 - A) if similarity else A
    Dm = (Dm + Dm.T) / 2
    np.fill_diagonal(Dm, 0.0)
    Dm = np.clip(Dm, 0, None)
    Z = linkage(squareform(Dm, checks=False), method="average")
    return [int(x) for x in leaves_list(Z)], Z


def plot_clustered_pair(ids, D, I):
    """Binder position (RMSD) and sequence identity, each as a clustered heat map with a dendrogram on the left."""
    plt = _plt()
    from scipy.cluster.hierarchy import dendrogram
    n = len(ids)
    labs = [str(x).split("_")[-1] for x in ids]
    fig = plt.figure(figsize=(max(16.0, 0.9 * n + 6.0), max(7.5, 0.5 * n + 2.5)))
    gs = fig.add_gridspec(1, 4, width_ratios=[0.5, 3.0, 0.5, 3.0], wspace=0.25)
    for col, (M, title, cmap, sim, lab) in enumerate(((D, "Binder position: Cα RMSD (Å)", "viridis", False, "Å"),
                                                    (I, "Sequence identity (%)", "viridis_r", True, "% identical"))):
        order, Z = cluster_order(M, similarity=sim)
        axd, ax = fig.add_subplot(gs[0, 2 * col]), fig.add_subplot(gs[0, 2 * col + 1])
        if Z is not None:
            dendrogram(Z, orientation="left", ax=axd, no_labels=True, color_threshold=0, above_threshold_color="#555555")
            axd.invert_yaxis()
        axd.axis("off")
        P = np.array(M, float)[np.ix_(order, order)]
        shown = 100 * P if sim else P
        im = ax.imshow(shown, cmap=cmap, aspect="auto")
        ax.set_xticks(range(n)); ax.set_xticklabels([labs[k] for k in order], rotation=90, fontsize=12)
        ax.set_yticks(range(n)); ax.set_yticklabels([labs[k] for k in order], fontsize=12)
        ax.yaxis.tick_right()
        ax.set_title(title, fontsize=14)
        lo, hi = np.nanmin(shown), np.nanmax(shown)
        for i in range(n):
            for j in range(n):
                if n <= 20 and np.isfinite(shown[i, j]):
                    frac = (shown[i, j] - lo) / (hi - lo + 1e-9)
                    dark = frac < 0.5 if cmap == "viridis" else frac > 0.5
                    ax.text(j, i, f"{shown[i, j]:.0f}", ha="center", va="center", fontsize=9 if n > 14 else 10, color="white" if dark else "black")
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.12)
        cb.set_label(lab, fontsize=12); cb.ax.tick_params(labelsize=11)
    fig.suptitle("Hierarchical clustering of the designs (average linkage; numbers = design numbers)", fontsize=14, y=0.995)
    return fig


from html import escape as html_escape


def _js_call(name, args):
    if name == "setHoverable":
        sel, flag, show, hide = args
        return f"v.setHoverable({json.dumps(sel)},{'true' if flag else 'false'},{show},{hide});"
    return "v." + name + "(" + ",".join(json.dumps(a) for a in args) + ");"


_3DMOL_URLS = ["https://cdn.jsdelivr.net/npm/3dmol@2/build/3Dmol-min.js", "https://3Dmol.org/build/3Dmol-min.js"]


def layers_html(layers, ref, hotspots=(), height=560, width=760, info=None):
    """The same scene as view_layers, as ONE self-contained HTML block with a check box for every layer. Showing and hiding a design happens
    inside the page (the viewer is built once and never redrawn from Python), so nothing flickers or goes blank.
    info: one dict(label, color) per layer for the check boxes."""
    rec = _Rec()
    view_layers(layers, ref, hotspots, height, width, _view=rec)
    chains = {_LAYER_CHAINS[k]: k for k in range(len(layers))}
    base, own = [], [[] for _ in layers]
    for name, args, _kw in rec.calls:
        sel = args[0] if args and isinstance(args[0], dict) else {}
        if name in ("setStyle", "addStyle") and sel.get("chain") in chains:
            own[chains[sel["chain"]]].append(_js_call(name, args))
        else:
            base.append(_js_call(name, args))
    u = "v" + uuid.uuid4().hex[:10]
    info = info or [dict(label=L.get("name", f"layer {k + 1}"), color=L.get("color", "#1D9A78")) for k, L in enumerate(layers)]
    boxes = "".join(
        f"<label style='display:flex;align-items:center;gap:4px;white-space:nowrap;overflow:hidden'>"
        f"<input type='checkbox' checked data-k='{k}'><span style='display:inline-block;width:12px;height:12px;flex:none;background:{i['color'] if str(i['color']).startswith('#') else '#1D9A78'};border:1px solid #333'></span>"
        f"<span>{html_escape(str(i['label']))}</span> <a href='#' data-only='{k}' style='font-size:11px;color:#06c'>only</a></label>"
        for k, i in enumerate(info))
    layer_js = ",".join("function(v){" + "".join(o) + "}" for o in own)
    js = ("(function(){var U=" + json.dumps(u) + ",EL=document.getElementById(U+'v'),CH=" + json.dumps(list(chains)) + ";"
          "function loadOne(uri){return new Promise(function(res,rej){var sx=window.exports,sm=window.module;if(typeof sx==='undefined')window.exports={};"
          "if(typeof sm==='undefined')window.module={};var t=document.createElement('script');t.src=uri;t.async=true;"
          "t.onload=function(){window.exports=sx;window.module=sm;res();};t.onerror=function(){window.exports=sx;window.module=sm;rej(new Error(uri));};"
          "(document.head||document.body).appendChild(t);});}"
          "if(window.$3Dmolpromise===undefined){if(window.$3Dmol!==undefined){window.$3Dmolpromise=Promise.resolve();}else{"
          "var urls=" + json.dumps(_3DMOL_URLS) + ";window.$3Dmolpromise=loadOne(urls[0]).catch(function(){return loadOne(urls[1]);});}}"
          "var BASE=function(v){" + "".join(base) + "};var LAYERS=[" + layer_js + "];var on=CH.map(function(){return true;});var v=null;"
          "var boxes=document.querySelectorAll('#'+U+' input[data-k]');"
          "function apply(){if(!v)return;for(var k=0;k<CH.length;k++){v.setStyle({chain:CH[k]},{});}"
          "for(var k=0;k<CH.length;k++){if(on[k])LAYERS[k](v);}v.render();}"
          "function sync(){for(var i=0;i<boxes.length;i++){boxes[i].checked=on[+boxes[i].getAttribute('data-k')];}apply();}"
          "for(var i=0;i<boxes.length;i++){boxes[i].addEventListener('change',function(e){on[+e.target.getAttribute('data-k')]=e.target.checked;apply();});}"
          "document.getElementById(U+'all').onclick=function(){on=on.map(function(){return true;});sync();};"
          "document.getElementById(U+'none').onclick=function(){on=on.map(function(){return false;});sync();};"
          "var onl=document.querySelectorAll('#'+U+' a[data-only]');"
          "for(var i=0;i<onl.length;i++){onl[i].addEventListener('click',function(e){e.preventDefault();var q=+e.target.getAttribute('data-only');on=on.map(function(_,k){return k===q;});sync();});}"
          "window.$3Dmolpromise.then(function(){EL.innerHTML='';v=$3Dmol.createViewer(EL,{backgroundColor:'white'});BASE(v);apply();"
          "}).catch(function(e){EL.innerHTML='<p style=\\'padding:8px\\'>The 3D viewer could not be loaded (no connection to cdn.jsdelivr.net?). Run the cell again.</p>';});})();")
    return (f"<div id='{u}' style='font-family:sans-serif;font-size:13px;background:#fff;color:#111;padding:6px;max-width:{width + 20}px'>"
            f"<div style='margin-bottom:6px'><button id='{u}all'>Show all</button> <button id='{u}none'>Show none</button> "
            f"<small>Tick the designs you want to see, or click <i>only</i> to look at a single design.</small></div>"
            f"<div style='display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3px 12px'>{boxes}</div>"
            f"<div id='{u}v' style='position:relative;width:{width}px;height:{height}px;margin-top:8px;border:1px solid #ddd'><p style='padding:8px'>Loading the 3D viewer ...</p></div>"
            f"<small>Hover over a bead for the design, residue and metric.</small>"
            f"<script>{js}</script></div>")


class OverlayViewer:
    """All binders on the receptor with a check box for every design (and one for GLP-1 from 6X18): switch designs on and off to look at one,
    a few or all of them. One HTML block: the switching happens in the page, the viewer is not redrawn from Python."""
    def __init__(self, session, metric=None, with_glp1=True, height=560):
        from IPython.display import display, HTML
        self.s, self.height = session, height
        recs = sorted(session.designs(), key=lambda x: x["id"])
        if not recs:
            raise RuntimeError("Collect the RFD4 designs first (cell 4.1).")
        df = session.score(recs).set_index("id")
        cols = rfd4_columns(df.reset_index())
        metric = metric if metric in df.columns else (cols[0] if cols else None)
        self.metric = metric
        self.layers, info = {}, []
        for k, r in enumerate(recs):
            col = LAYER_COLORS[k % len(LAYER_COLORS)]
            v = df.loc[r["id"], metric] if metric else float("nan")
            tag = f"{metric.replace('rfd4_', '')} {v:.3g}" if metric and v == v else ""
            self.layers[r["id"]] = dict(text=session._framed_design(r["id"]), name=r["id"], color=col, opacity=0.9, tag=tag)
            info.append(dict(label="design " + r["id"].split("_")[-1] + (f" ({tag})" if tag else ""), color=col))
        if with_glp1:
            self.layers["GLP-1 (6X18)"] = dict(text=crystal_as_design(session.ref), name="GLP-1 (6X18)", color="#222222", opacity=0.45,
                                               numbers=[x["num"] for x in session.ref["pep"]["res"]])
            info.append(dict(label="GLP-1 (6X18)", color="#222222"))
        self.html = layers_html(list(self.layers.values()), session.ref, session.hotspots, height, 760, info)
        display(HTML(self.html))


class MetricGuide:
    """Pick a design metric and see what it does across the designs: bar chart in rank order, summary numbers, and the three highest and lowest
    designs. Use it together with the check boxes of cell 4.3 to look at those designs in 3D."""
    def __init__(self, df, session=None):
        w, display, HTML, clear_output = _w()
        self.df = df.reset_index(drop=True)
        cols = rfd4_columns(self.df) + [c for c in ("des_hotspot_hits", "des_site_overlap", "des_site_cover", "des_n_clash", "des_min_dist") if c in self.df]
        cols = [c for c in cols if self.df[c].notna().any()]
        self.out = w.Output()
        self.dd = w.Dropdown(options=[(c.replace("rfd4_", "RFD4: ").replace("des_", "design file: "), c) for c in cols], description="Metric", layout=w.Layout(width="520px"))
        self.dd.observe(lambda _c: self.render(), names="value")
        self.display, self.clear_output, self.HTML = display, clear_output, HTML
        display(w.VBox([self.dd, self.out]))
        if cols:
            self.render()

    def render(self):
        plt = _plt()
        c = self.dd.value
        d = self.df[["id", c]].dropna().sort_values(c, ascending=False)
        with self.out:
            self.clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(10, 4.6))
            ax.bar(range(len(d)), d[c], color="#1D9A78", edgecolor="black", linewidth=0.5)
            ax.set_xticks(range(len(d))); ax.set_xticklabels([str(i).split("_")[-1] for i in d["id"]], fontsize=12, rotation=90)
            ax.set_xlabel("design number (sorted from the highest to the lowest value)", fontsize=13)
            ax.set_ylabel(c.replace("rfd4_", "").replace("des_", ""), fontsize=13)
            ax.set_title(c.replace("rfd4_", "RFD4: ").replace("des_", "design file: "), fontsize=14)
            self.display(fig); plt.close(fig)
            top = ", ".join(str(i).split("_")[-1] for i in d["id"].head(3)); bot = ", ".join(str(i).split("_")[-1] for i in d["id"].tail(3))
            self.display(self.HTML(f"<b>lowest {d[c].min():.3g} · median {d[c].median():.3g} · highest {d[c].max():.3g}</b> &nbsp;|&nbsp; "
                                   f"highest designs: <b>{top}</b> &nbsp;|&nbsp; lowest designs: <b>{bot}</b>"))


class MetricExplorer:
    """Interactive version of the two plots of cell 4.7: drop-downs choose the metrics, the plots are drawn again after every change.
    Left: an RFD4 / design-file metric against an OpenFold3 metric. Right: two OpenFold3 metrics for designs (symbols) and reference peptides (stars),
    colour = mean binder pLDDT."""
    def __init__(self, df, ref_df=None):
        w, display, HTML, clear_output = _w()
        self.df, self.ref_df = df, ref_df
        left_x = rfd4_columns(df) + [c for c in ("des_hotspot_hits", "des_site_overlap", "des_site_cover", "des_n_clash", "des_min_dist") if c in df and df[c].notna().any()]
        of3 = [c for c in OF3_COLS if c in df and df[c].notna().any()]
        nice = lambda c: c.replace("rfd4_", "RFD4: ").replace("des_", "design file: ").replace("_", " ")
        lay = w.Layout(width="360px")
        self.x1 = w.Dropdown(options=[(nice(c), c) for c in left_x] or [("-", None)], description="Left x", layout=lay)
        self.y1 = w.Dropdown(options=[(c.replace("_", " "), c) for c in of3] or [("-", None)], value="iptm" if "iptm" in of3 else None, description="Left y", layout=lay)
        self.x2 = w.Dropdown(options=[(c.replace("_", " "), c) for c in of3] or [("-", None)], value="iface_pae" if "iface_pae" in of3 else None, description="Right x", layout=lay)
        self.y2 = w.Dropdown(options=[(c.replace("_", " "), c) for c in of3] or [("-", None)], value="iptm" if "iptm" in of3 else None, description="Right y", layout=lay)
        for dd in (self.x1, self.y1, self.x2, self.y2):
            dd.observe(lambda _c: self.render(), names="value")
        self.out = w.Output()
        self.display, self.clear_output = display, clear_output
        display(w.VBox([w.HBox([self.x1, self.y1]), w.HBox([self.x2, self.y2]), self.out]))
        self.render()

    def render(self):
        plt = _plt()
        with self.out:
            self.clear_output(wait=True)
            fig, axs = plt.subplots(1, 2, figsize=(17, 6.6), gridspec_kw=dict(wspace=0.32))
            plot_xy(axs[0], self.df, self.x1.value, self.y1.value)
            plot_overview(self.df, self.ref_df, xcol=self.x2.value, ycol=self.y2.value, ax=axs[1])
            self.display(fig); plt.close(fig)


# =====================================================================================
#  Session: everything a group does, saved to disk after each step (so a restart loses nothing)
# =====================================================================================
class Session:
    def __init__(self, group, token="", server="", mode="auto", root="ws3_data", log=print, pack_url=""):
        g = str(group).strip()
        if not g.isdigit() or not 1 <= int(g) <= N_GROUPS:
            raise ValueError(f"Choose your group number (1 to {N_GROUPS}) in the dropdown of cell 0.2 first, then run this cell again.")
        self.group = g.zfill(2)
        self.seed = SEED + int(g)
        self.extra_refs = {}
        self.region = "site"
        self.pack_url = (pack_url or "").strip()
        self.root = Path(root)
        self.dir = self.root / f"group{self.group}"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "state.json"
        self.log = log
        self.ref = None
        self.state = json.loads(self.path.read_text()) if self.path.exists() else dict(
            group=self.group, created=now_stamp(), hotspots=[], notes={}, jobs={}, records=[], rounds=[], thresholds={})
        self.thr = dict(THRESHOLDS, **self.state.get("thresholds", {}))
        self.client = self._connect(token, server, mode)

    # ---- connection
    def _pack(self):
        pack = self.root / "pack"
        if not (pack / "cache").exists():
            import zipfile
            cands = [Path("ws3_pack.zip"), self.root / "ws3_pack.zip", self.root.parent / "ws3_pack.zip",
                     Path("/content/ws3_pack.zip"), Path("/content/drive/MyDrive/ws3_pack.zip")]
            z = next((c for c in cands if c.exists()), None)
            if z is None and self.pack_url:
                try:
                    self.log("Downloading the stored results ...")
                    z = Path(download_url(self.pack_url, self.root / "ws3_pack.zip"))
                except Exception as e:
                    self.log(f"Could not download the stored results ({str(e)[:70]}).")
            if z is not None:
                zipfile.ZipFile(z).extractall(self.root)
        return pack if (pack / "cache").exists() else None

    def _connect(self, token, server, mode):
        pack = self._pack()
        if mode not in ("auto", "server", "stored"):
            raise ValueError("MODE must be 'auto', 'server' or 'stored'")
        if mode in ("auto", "server") and server:
            c = ApiClient(server, token, retries=2, log=self.log)
            try:
                h = c.health()
                self.log(f"Connected to the server: {h.get('status', h)}")
                self.mode_used = "server"
                return c
            except RuntimeError as e:
                if mode == "server" or not pack:
                    raise
                self.log(f"Server not usable ({str(e)[:90]}). Switching to the stored results.")
        elif mode == "server":
            raise RuntimeError("MODE is 'server' but SERVER is empty.")
        if not pack:
            raise RuntimeError("No server and no stored results (ws3_data/pack or ws3_pack.zip). Ask an instructor.")
        self.mode_used = "stored"
        self.log("Using the stored (precomputed) results. Only the preset choices can be run in this mode.")
        return LocalPack(pack, log=self.log)

    def save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1, default=str))
        tmp.replace(self.path)

    # ---- notes with time stamps (hypotheses are written before results are seen)
    def note(self, key, **fields):
        self.state["notes"][key] = dict(fields, time=now_stamp())
        self.save()
        return self.state["notes"][key]

    def get_note(self, key):
        return self.state["notes"].get(key, {})

    # ---- reference complex
    def load_reference(self, pdb_id="6X18", rec_chain=None, pep_chain=None):
        txt = None
        for ext in ("pdb", "cif"):
            for base in (self.root, Path(".")):
                p = base / f"{pdb_id}.{ext}"
                if p.exists():
                    txt = p.read_text(); break
            if txt:
                break
        if txt is None and getattr(self, "mode_used", "") == "stored":
            p = self.root / "pack" / f"{pdb_id}.pdb"
            txt = p.read_text() if p.exists() else None
        if txt is None:
            txt = fetch_rcsb(pdb_id, self.root)
        self.ref = build_reference(txt, rec_chain, pep_chain)
        r = self.ref
        self.log(f"{pdb_id}: receptor chain {r['rec_chain']} ({len(r['rec']['res'])} residues, numbers {r['rec_nums'][0]} to {r['rec_nums'][-1]}), "
                 f"peptide chain {r['pep_chain']} ({len(r['pep']['res'])} residues: {r['pep_seq']}), "
                 f"other chains kept out of the design: {', '.join(r['other_chains']) or 'none'}")
        self.log(f"GLP-1 touches {len(r['footprint'])} receptor residues within {r['cutoff']} A.")
        return r

    def set_hotspots(self, hotspots, reason=""):
        hs = sorted(set(hotspots), key=lambda s: int(str(s).split(":")[1]))
        if not 3 <= len(hs) <= 8:
            raise ValueError("Choose between 3 and 8 hotspots.")
        self.state["hotspots"] = hs
        self.note("hotspots", hotspots=hs, reason=reason)
        return hs

    @property
    def hotspots(self):
        return self.state["hotspots"]

    def set_thresholds(self, why="", **kw):
        bad = [k for k in kw if k not in THRESHOLDS]
        if bad:
            raise ValueError(f"unknown threshold(s) {bad}; choose from {list(THRESHOLDS)}")
        self.thr.update(kw)
        self.state["thresholds"] = {k: v for k, v in self.thr.items() if THRESHOLDS[k] != v}
        self.note("thresholds", values=dict(self.thr), why=why)

    # ---- jobs
    def submit(self, key, task, payload):
        """Send a job and return at once. Sending the same key twice does nothing (no double submission)."""
        if key in self.state["jobs"] and not self.state["jobs"][key]["collected"]:
            dead, why = False, "failed"
            try:
                dead = self.client.status(self.state["jobs"][key]["job_id"]).get("state") in FAIL_STATES
            except RuntimeError as e:
                if "Server error 404" in str(e):          # the server does not know this job (empty id, server restarted, ...)
                    dead, why = True, "is not known to the server"
            if dead:
                self.log(f"The earlier job for '{key}' {why}. Sending it again.")
                self.state["jobs"].pop(key)
        if key in self.state["jobs"]:
            j = self.state["jobs"][key]
            self.log(f"'{key}' was already submitted at {j['submitted']} (job {j['job_id']}). Not sending it again.")
            return j
        payload = dict(payload, target_id=TARGET_ID, seed=SEED if key == "refs" else self.seed, group=self.group)
        job = self.client.submit(task, payload)
        self.state["jobs"][key] = dict(task=task, job_id=job["job_id"], payload=payload, submitted=now_stamp(), collected=False)
        self.save()
        self.log(f"Submitted '{key}' ({task}) as job {job['job_id']} at {now_stamp()}.")
        return self.state["jobs"][key]

    def reset_job(self, key):
        """Forget a job that was submitted but not collected (for a stuck job): the submit cell can then send it again. Collected jobs are kept."""
        j = self.state["jobs"].get(key)
        if j and not j["collected"]:
            self.state["jobs"].pop(key); self.save()
            self.log(f"Forgot the uncollected job '{key}'. Run the submit cell again.")
        elif j:
            self.log(f"'{key}' was already collected: nothing to reset.")
        else:
            self.log(f"There is no job '{key}'.")

    def status(self):
        rows = []
        for k, j in self.state["jobs"].items():
            if j["collected"]:
                st = "collected"
            else:
                try:
                    s = self.client.status(j["job_id"]); st = s["state"]
                    if s.get("queue_position") is not None:
                        st += f" (position {s['queue_position']})"
                except RuntimeError as e:
                    st = "unreachable: " + str(e)[:40]
            rows.append(dict(job=k, task=j["task"], job_id=j["job_id"], submitted=j["submitted"], state=st))
        return pd.DataFrame(rows, columns=["job", "task", "job_id", "submitted", "state"])

    def collect(self, key, origin=None):
        j = self.state["jobs"].get(key)
        if not j:
            raise RuntimeError(f"There is no submitted job called '{key}'. Run the submit cell first.")
        local = self._collected_locally(key, j)
        if local is not None:
            self.log(f"'{key}' was collected before: using the {len(local)} designs saved in your folder (the server is not contacted).")
            return local
        if self.mode_used == "stored" and not str(j["job_id"]).startswith("pack-"):
            # the group switched from the server to the stored results after submitting: ask the pack for the same request
            job = self.client.submit(j["task"], j["payload"])
            j["job_id"], j["switched_to_stored"] = job["job_id"], now_stamp()
            self.save()
            self.log(f"'{key}' was submitted to the server; using the stored result for the same request instead.")
        try:
            res = self.client.collect(j["job_id"])
        except RuntimeError as e:
            if "Server error 404" not in str(e) or not j.get("payload"):
                raise
            job = self.client.submit(j["task"], j["payload"])          # the server does not know the job: same request again (served from the cache if it was computed)
            j["job_id"], j["resubmitted"] = job["job_id"], now_stamp()
            self.save()
            self.log(f"The server did not know the job of '{key}'. The same request was sent again (job {job['job_id']}).")
            res = self.client.collect(j["job_id"])
        recs = save_result(self.client, res, self.dir)
        for r in recs:
            r["job"] = key
            if origin:
                r["origin"] = origin
            if j["task"] == "redesign" and j["payload"].get("round"):
                r["round"] = j["payload"]["round"]          # a stored result may have been made for another round number
        ids = {r["id"] for r in recs}
        old = {r["id"]: r for r in self.state["records"]}
        merged = []
        for r in recs:       # a predict job adds files to an existing design instead of replacing it
            o = old.get(r["id"])
            if o and j["task"] == "predict":
                o["files"].update(r["files"]); o["mode"] = r["mode"]; o["version"] = r["version"]
                merged.append(o)
            else:
                merged.append(r)
        self.state["records"] = [r for r in self.state["records"] if r["id"] not in ids] + merged
        j["collected"], j["collected_at"], j["execution_mode"] = True, now_stamp(), res.get("execution_mode", "")
        j["record_ids"] = [r["id"] for r in recs]
        self.save()
        self.log(f"Collected {len(recs)} designs from '{key}'.")
        return merged

    def _collected_locally(self, key, j):
        """The records of a job that was collected before, if all their files are still in the folder (a student who runs a cell again
        does not need the server). None if anything is missing: the job is then collected from the server again."""
        if not j.get("collected"):
            return None
        ids = j.get("record_ids") or [r["id"] for r in self.state["records"] if r.get("job") == key]
        by = {r["id"]: r for r in self.state["records"]}
        if not ids or any(i not in by for i in ids):
            return None
        need = {"predict": "model"}.get(j["task"], "design")
        out = []
        for i in ids:
            f = by[i].get("files") or {}
            if need not in f or any(not Path(v).exists() for v in f.values()):
                return None
            out.append(by[i])
        return out

    def records(self, job=None, origin=None):
        out = self.state["records"]
        if job:
            out = [r for r in out if r.get("job") == job]
        if origin:
            out = [r for r in out if r.get("origin") == origin]
        return out

    # ---- scoring
    def score(self, recs=None, with_notes=True):
        if self.ref is None:
            raise RuntimeError("Load the reference first (Step 1).")
        recs = recs if recs is not None else [r for r in self.state["records"] if r.get("origin") != "reference"]
        extra = dict(group=self.group, target="GLP-1R (6X18)")
        df = score_records(recs, self.ref, self.hotspots, extra, self.thr)
        if not df.empty:
            rounds = {r["round"]: r for r in self.state["rounds"]}
            fx = [";".join(map(str, rounds.get(rn, {}).get("fixed", []))) if o in ("mpnn", "manual") else "" for rn, o in zip(df["round"], df["origin"])]
            df["fixed_positions"] = fx
            df["hypothesis"] = [rounds.get(rn, {}).get("hypothesis", "") if o in ("mpnn", "manual") else self.get_note("gen_hypothesis").get("text", "")
                                for rn, o in zip(df["round"], df["origin"])]
            df["decision"] = [rounds.get(rn, {}).get("decision", "") if o in ("mpnn", "manual") else "" for rn, o in zip(df["round"], df["origin"])]
        return df

    def reference_scores(self):
        recs = [r for r in self.state["records"] if r.get("origin") == "reference"]
        return score_records(recs, self.ref, self.hotspots, dict(group=self.group), self.thr) if recs else pd.DataFrame()

    def run_references(self, wait=True):
        """Step 2: predict the reference peptides (GLP-1 from 6X18, three other peptides, one scrambled control)."""
        refs = reference_list(self.ref)
        payload = dict(designs=[dict(id=r["id"], sequence=r["seq"]) for r in refs])
        self.submit("refs", "predict", payload)
        recs = self.collect("refs", origin="reference")
        meta = {r["id"]: r for r in refs}
        for r in self.state["records"]:
            if r["id"] in meta:
                r["label"], r["expected"] = meta[r["id"]]["label"], meta[r["id"]]["expected"]
        self.save()
        return self.reference_scores()

    # ---- looking at a design
    def record(self, rid):
        for r in self.state["records"]:
            if r["id"] == rid:
                return r
        raise KeyError(f"no design called {rid}")

    def model_for_view(self, rid):
        r = self.record(rid)
        conf = load_confidence(r["files"].get("confidence"))
        return model_text_with_plddt(r["files"]["model"], conf)

    def _framed_design(self, rid):
        r = self.record(rid)
        if not r["files"].get("design"):
            return None
        return superpose_text(Path(r["files"]["design"]).read_text(), self.ref, self.region)[0]

    def framed_model(self, rid):
        """The prediction (or, before OpenFold3 has run, the design) moved onto the 6X18 receptor. Returns (text, rmsd, n residues, is_prediction)."""
        r = self.record(rid)
        if "model" in r["files"]:
            txt, pl, n_rec = self.model_for_view(rid)
            return superpose_text(txt, self.ref, self.region) + (True,)
        txt, fit, n = superpose_text(Path(r["files"]["design"]).read_text(), self.ref, self.region)
        return txt, fit, n, False

    def view(self, rid, color="plddt", fixed=None, with_crystal=False, with_design=False, compare=(), height=520):
        """3D view of one candidate, always superposed on the 6X18 receptor. with_crystal adds GLP-1 from 6X18, with_design the design
        of the server (before the OpenFold3 prediction), compare a list of other candidates."""
        txt, fit, n, is_pred = self.framed_model(rid)
        if not is_pred and color == "plddt":
            color = "#1D9A78"
        self.log(f"Superposed on the receptor: {n} C-alpha atoms of the residues around GLP-1, RMSD {fit:.2f} A.")
        extra = []
        if with_design and is_pred and self._framed_design(rid):
            extra.append(dict(text=self._framed_design(rid), name=f"{rid} (design)", color="#7B3294", opacity=0.9))
        for k, other in enumerate(compare):
            t2 = self.framed_model(other)[0]
            extra.append(dict(text=t2, name=other, color=LAYER_COLORS[(k + 2) % len(LAYER_COLORS)], opacity=0.9))
        cry = crystal_as_design(self.ref) if with_crystal else None
        return view_complex(txt, self.ref, color, self.hotspots, fixed, cry, height, extra, name=rid)

    # ---- an experimental structure for comparison (Step 2: 9BYO)
    def load_extra_reference(self, pdb_id="9BYO"):
        txt = None
        for base in (self.root / "pack", self.root, Path(".")):
            for ext in ("pdb", "cif"):
                p = base / f"{pdb_id}.{ext}"
                if p.exists():
                    txt = p.read_text(); break
            if txt:
                break
        if txt is None:
            txt = fetch_rcsb(pdb_id, self.root)
        r2 = build_reference(txt)
        self.extra_refs[pdb_id] = r2
        self.log(f"{pdb_id}: receptor chain {r2['rec_chain']} ({len(r2['rec']['res'])} residues), peptide chain {r2['pep_chain']} "
                 f"({len(r2['pep']['res'])} residues: {r2['pep_seq']})")
        return r2

    def _experimental_frame(self, pdb_id):
        r2 = self.extra_refs[pdb_id]
        R, t, fit, n = fit_to_reference(r2["atoms"], r2["rec_chain"], self.ref, self.region)
        atoms = transform_atoms(r2["atoms"], R, t) if R is not None else r2["atoms"]
        return atoms_to_pdb(atoms, chain_map={r2["rec_chain"]: REC, r2["pep_chain"]: BIND}), fit, n

    def compare_experimental(self, rid, pdb_id="9BYO"):
        """OpenFold3 prediction of a peptide against an experimental structure of a related peptide (both on the 6X18 receptor).
        Returns (summary table, per-position table, text about the sequence differences)."""
        r2 = self.extra_refs[pdb_id]
        txt, fit, n, _ = self.framed_model(rid)
        atoms = parse_pdb(txt)
        pred_b = get_chain(atoms, BIND)
        exp_text, fit2, n2 = self._experimental_frame(pdb_id)
        exp_b = get_chain(parse_pdb(exp_text), BIND)
        pairs = align_pairs(chain_seq(pred_b), chain_seq(exp_b))
        ca_p, ca_e = ca_coords(pred_b), ca_coords(exp_b)
        d = [float(np.linalg.norm(ca_p[i] - ca_e[j])) for i, j in pairs]
        diff = [f"position {i + 1}: {pred_b['res'][i]['aa']} in the prediction, {exp_b['res'][j]['aa']} in {pdb_id}"
                for i, j in pairs if pred_b["res"][i]["aa"] != exp_b["res"][j]["aa"]]
        extra = f"{len(pairs)} of {len(pred_b['res'])} residues aligned. " + ("Differences: " + "; ".join(diff) if diff else "The sequences are identical in the aligned part.")
        rows = pd.DataFrame(dict(position_prediction=[i + 1 for i, _ in pairs], letter_prediction=[pred_b["res"][i]["aa"] for i, _ in pairs],
                                 residue_in_structure=[f"{exp_b['res'][j]['aa']}{exp_b['res'][j]['num']}" for _, j in pairs],
                                 ca_distance_A=np.round(d, 2)))
        # contacts, expressed in 6X18 receptor numbering
        rec_p = get_chain(atoms, REC)
        touch_p = {rec_p["res"][j]["num"] for (j, _) in contact_detail(rec_p, pred_b, 4.5)}
        rm = dict(residue_map(r2["rec"], self.ref["rec"]))
        touch_e = set()
        for (j, _) in contact_detail(r2["rec"], r2["pep"], 4.5):
            if j in rm:
                touch_e.add(self.ref["rec"]["res"][rm[j]]["num"])
        glp = self.ref["footprint"]
        def row(name, t):
            return dict(structure=name, receptor_residues_in_contact=len(t), shared_with_exp=len(t & touch_e), shared_with_GLP1_6X18=len(t & glp),
                        overlap_with_exp=round(len(t & touch_e) / max(1, len(t | touch_e)), 2))
        summ = pd.DataFrame([row(f"OpenFold3 prediction ({rid})", touch_p), row(f"{pdb_id} (experimental)", touch_e), row("GLP-1 in 6X18 (experimental)", glp)])
        summ["peptide_CA_rmsd_to_exp_A"] = [round(float(np.sqrt(np.mean(np.square(d)))), 2) if d else float("nan"), 0.0, float("nan")]
        self.log(f"Both structures moved onto the 6X18 receptor (prediction: {n} CA, RMSD {fit:.2f} A; {pdb_id}: {n2} CA, RMSD {fit2:.2f} A).")
        return summ, rows, extra

    def view_experimental(self, rid, pdb_id="9BYO", label="exendin-D3", height=520):
        txt, fit, n, _ = self.framed_model(rid)
        exp_text, _, _ = self._experimental_frame(pdb_id)
        r2 = self.extra_refs[pdb_id]
        layers = [dict(text=txt, name=rid, color="plddt", lines=True),
                  dict(text=exp_text, name=f"{pdb_id} {label}", color="#B74919", numbers=[r["num"] for r in r2["pep"]["res"]], sticks="all"),
                  dict(text=crystal_as_design(self.ref), name="GLP-1 (6X18)", color="#F19D19", opacity=0.45,
                       numbers=[r["num"] for r in self.ref["pep"]["res"]])]
        return view_layers(layers, self.ref, self.hotspots, height)

    # ---- Step 4: the RFD4-Proteina designs before any OpenFold3 run
    def designs(self, job="gen"):
        return [r for r in self.state["records"] if r.get("job") == job and r.get("origin") == "rfd4"]

    def rfd4_scores(self):
        return self.score(self.designs())

    def overlay_designs(self, metric=None, with_glp1=True, height=560):
        """All RFD4-Proteina binders on top of each other on the receptor, one colour each. Returns (view, legend as HTML)."""
        recs = self.designs()
        if not recs:
            raise RuntimeError("Collect the RFD4 designs first (cell 4.1).")
        df = self.score(recs).set_index("id")
        cols = rfd4_columns(df.reset_index())
        metric = metric if metric in df.columns else (cols[0] if cols else None)
        layers, rows = [], []
        for k, r in enumerate(sorted(recs, key=lambda x: x["id"])):
            col = LAYER_COLORS[k % len(LAYER_COLORS)]
            tag = f"{metric.replace('rfd4_', '')} {df.loc[r['id'], metric]:.3g}" if metric and metric in df and df.loc[r["id"], metric] == df.loc[r["id"], metric] else ""
            layers.append(dict(text=self._framed_design(r["id"]), name=r["id"], color=col, opacity=0.9, tag=tag))
            rows.append(f"<tr><td><span style='display:inline-block;width:14px;height:14px;background:{col}'></span></td><td>{r['id']}</td>"
                        f"<td>{tag or '-'}</td><td>{int(df.loc[r['id'], 'des_hotspot_hits']) if 'des_hotspot_hits' in df else ''}</td></tr>")
        if with_glp1:
            layers.append(dict(text=crystal_as_design(self.ref), name="GLP-1 (6X18)", color="#222222", opacity=0.45,
                               numbers=[r["num"] for r in self.ref["pep"]["res"]]))
            rows.append("<tr><td><span style='display:inline-block;width:14px;height:14px;background:#222'></span></td><td>GLP-1 (6X18)</td><td>-</td><td></td></tr>")
        legend = ("<table style='font-size:12px;border-collapse:collapse'><tr><th></th><th>design</th><th>" + ((metric or "rfd4 metric").replace("rfd4_", "RFD4 ")) +
                  "</th><th>hotspots touched</th></tr>" + "".join(rows) + "</table>")
        return view_layers(layers, self.ref, self.hotspots, height), legend

    def diversity_matrices(self):
        """(ids, Calpha RMSD matrix of the binders on the common receptor, sequence identity matrix) of the RFD4 designs."""
        recs = sorted(self.designs(), key=lambda x: x["id"])
        B = [get_chain(parse_pdb(self._framed_design(r["id"])), BIND) for r in recs]
        n = len(recs)
        D = np.full((n, n), np.nan); I = np.zeros((n, n))
        CA = [ca_coords(b) for b in B]
        for i in range(n):
            for j in range(n):
                if len(CA[i]) == len(CA[j]):
                    D[i, j] = rmsd(CA[i], CA[j])
                I[i, j] = identity(recs[i]["sequence"], recs[j]["sequence"])
        return [r["id"] for r in recs], D, I

    def overlay_widget(self, metric=None, height=560):
        """Interactive overlay of the RFD4 designs with a check box per design (see OverlayViewer)."""
        return OverlayViewer(self, metric, True, height)

    def plot_diversity(self):
        """Two heat maps with hierarchical clustering (average linkage): binder position (Calpha RMSD in A after superposing the receptors)
        and sequence identity. The rows and columns are re-ordered by the dendrogram, so designs that are alike end up next to each other."""
        plt = _plt()
        ids, D, I = self.diversity_matrices()
        return plot_clustered_pair(ids, D, I)

    def rerun_openfold3(self, key="of3"):
        """Send the RFD4-Proteina sequences to OpenFold3 (independent prediction of each complex from the sequence alone)."""
        recs = self.designs()
        if not recs:
            raise RuntimeError("Collect the RFD4 designs first (cell 4.1).")
        return self.submit(key, "predict", dict(designs=[dict(id=r["id"], sequence=r["sequence"]) for r in recs]))

    def plots(self, rid):
        r = self.record(rid)
        txt, pl, n_rec = self.model_for_view(rid)
        plt = _plt()
        fig, ax = plt.subplots(1, 2, figsize=(14, 5.2))
        plot_pae(load_pae(r["files"].get("pae")), n_rec, ax[0], f"{rid}: PAE")
        plot_plddt(pl, n_rec, ax[1])
        fig.tight_layout()
        return fig

    # ---- manual edits and round bookkeeping
    def submit_manual(self, rnd, parent_id, texts):
        """Hand-written variants of a parent ('A12K, L20D' per line). They are evaluated by OpenFold3 only (no live design step)."""
        if getattr(self, "mode_used", "") == "stored":
            raise RuntimeError("Manual variants need the live server; they cannot be run from the stored results.")
        par = self.record(parent_id)
        lines = [t for t in (texts if isinstance(texts, list) else texts.splitlines()) if t.strip()]
        if not lines:
            raise ValueError("write at least one variant")
        if len(lines) > 5:
            raise ValueError("at most 5 manual variants per round")
        designs = []
        for k, t in enumerate(lines, 1):
            seq = apply_mutations(par["sequence"], t)
            designs.append(dict(id=f"{parent_id}_man{rnd}{k}", sequence=seq, parent_id=parent_id, mutations=t.strip()))
        key = f"r{rnd}_manual"
        self.submit(key, "predict", dict(designs=designs))
        for d in designs:
            self.state.setdefault("manual", {})[d["id"]] = d["mutations"]
        self.save()
        return key

    def collect_manual(self, rnd):
        key = f"r{rnd}_manual"
        if key not in self.state["jobs"]:
            return []
        recs = self.collect(key, origin="manual")
        for r in recs:
            r["round"], r["parent"] = rnd, r["id"].split("_man")[0]
            r["design_from"] = r["parent"]
        # the parent's design file is the reference for backbone and pose comparison
        for r in recs:
            pd_ = self.record(r["parent"])["files"].get("design")
            if pd_:
                r["files"]["design"] = pd_
        self.save()
        return recs

    def record_round(self, rnd, parent, fixed, temperature, hypothesis, decision="", conclusion=""):
        rec = dict(round=rnd, parent=parent, fixed=sorted(fixed), temperature=temperature, hypothesis=hypothesis,
                   decision=decision, conclusion=conclusion, time=now_stamp())
        rs = [r for r in self.state["rounds"] if r["round"] != rnd]
        self.state["rounds"] = sorted(rs + [rec], key=lambda r: r["round"])
        self.save()
        return rec

    def update_round(self, rnd, **kw):
        for r in self.state["rounds"]:
            if r["round"] == rnd:
                r.update(kw); self.save(); return r
        raise KeyError(f"round {rnd} has not been started")

    # ---- the final package
    def export(self, nominee_id, folder=None):
        folder = Path(folder or self.dir / "handin")
        folder.mkdir(parents=True, exist_ok=True)
        df = self.score()
        refdf = self.reference_scores()
        full = pd.concat([refdf.assign(evidence_type="computed (reference peptide, OpenFold3)"),
                          df.assign(evidence_type="computed (design, OpenFold3)")], ignore_index=True) if len(refdf) else df
        full.to_csv(folder / f"scorecard_group{self.group}.csv", index=False)
        self.ref["table"].to_csv(folder / "crystal_contacts_6X18_experimental_structure.csv", index=False)
        nom = df[df["id"] == nominee_id]
        if nom.empty:
            raise KeyError(f"nominee {nominee_id} is not in the scorecard")
        n = nom.iloc[0].to_dict()
        rec = self.record(nominee_id)
        txt, pl, n_rec = self.model_for_view(nominee_id)
        plt = _plt()
        figs = []
        for fn in (lambda ax: plot_pae(load_pae(rec["files"].get("pae")), n_rec, ax, "PAE"), lambda ax: plot_plddt(pl, n_rec, ax),
                   lambda ax: plot_overview(df, refdf, ax=ax)):
            f, ax = plt.subplots(figsize=(6.6, 5.4)); fn(ax); figs.append(fig_to_b64(f)); plt.close(f)
        state = dict(self.state, hotspots=self.hotspots)
        state["rounds"] = [dict(r) for r in self.state["rounds"]]
        state["gen_hypothesis"] = self.get_note("gen_hypothesis")
        state["final"] = self.get_note("final")
        refs_view = refdf if len(refdf) else df.iloc[0:0]
        card = candidate_card_html(self.group, n, df, refs_view, state, *figs)
        (folder / f"candidate_card_group{self.group}.html").write_text(card)
        (folder / "session_state.json").write_text(json.dumps(self.state, indent=1, default=str))
        return sorted(p.name for p in folder.iterdir()), folder
