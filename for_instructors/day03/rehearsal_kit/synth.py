"""Synthetic stand-ins for 6X18 and for server outputs. For tests only (no real chemistry)."""
import numpy as np, json, io
from ws3_helpers import ONE2THREE, REC, BIND, GLP1_SEQ

SIDE = {  # extra side-chain atoms (name, radial offset along the CB direction, in A)
    "K": [("CG", 1.5), ("CD", 2.5), ("NZ", 3.7)], "R": [("CG", 1.5), ("CD", 2.5), ("NH1", 3.8)],
    "D": [("CG", 1.5), ("OD1", 2.5)], "E": [("CG", 1.5), ("CD", 2.5), ("OE1", 3.3)],
    "S": [("OG", 1.4)], "T": [("OG1", 1.4)], "N": [("CG", 1.5), ("OD1", 2.5)], "Q": [("CG", 1.5), ("CD", 2.5), ("OE1", 3.4)],
    "L": [("CG", 1.5), ("CD1", 2.6)], "I": [("CG1", 1.5), ("CD1", 2.6)], "V": [("CG1", 1.5)], "F": [("CG", 1.5), ("CD1", 2.6)],
    "W": [("CG", 1.5), ("CD1", 2.6)], "Y": [("CG", 1.5), ("OH", 4.0)], "M": [("CG", 1.5), ("SD", 2.6)], "A": [], "G": [],
    "H": [("CG", 1.5), ("ND1", 2.6)], "C": [("SG", 1.8)], "P": [("CG", 1.5)],
}


def helix(seq, origin, axis=(1, 0, 0), phase=0.0, chain="A", num0=1, rise=1.5, radius=2.3, noise=0.0, rng=None, bfac=85.0,
          side_shift=0.0):
    """Atoms of an alpha helix along `axis`; side chains point away from the axis."""
    rng = rng or np.random.default_rng(0)
    ax = np.array(axis, float); ax /= np.linalg.norm(ax)
    u = np.cross(ax, [0, 0, 1.0]); u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-6 else np.array([0, 1.0, 0])
    v = np.cross(ax, u)
    atoms = []
    for i, a in enumerate(seq):
        th = phase + np.deg2rad(100 * i)
        rad = np.cos(th) * u + np.sin(th) * v
        ca = np.array(origin) + ax * rise * i + rad * radius
        rn = ONE2THREE[a]
        n = num0 + i
        pts = [("N", ca - ax * 1.2 + rad * 0.2), ("CA", ca), ("C", ca + ax * 1.2 + rad * 0.2), ("O", ca + ax * 1.6 - rad * 0.8)]
        if a != "G":
            pts.append(("CB", ca + rad * 1.5))
        for nm, off in SIDE[a]:
            pts.append((nm, ca + rad * (1.5 + off * 0.9 + side_shift)))
        for nm, p in pts:
            p = p + rng.normal(0, noise, 3)
            atoms.append((chain, n, "", rn, nm, float(p[0]), float(p[1]), float(p[2]), bfac))
    return atoms


def pdb_text(atoms):
    from ws3_helpers import atoms_to_pdb
    return atoms_to_pdb(atoms)


REC_LEN, REC_NUM0 = 160, 30


def receptor_seq(seed=3):
    rng = np.random.default_rng(seed)
    return "".join(rng.choice(list("ACDEFGHIKLMNPQRSTVWYLLAAEEKK"), REC_LEN))


def dbref_line(pdb_id, chain, a, b, ua, ub, acc="P43220"):
    line = list(" " * 80)
    for i, txt in ((0, "DBREF "), (7, pdb_id), (12, chain), (14, "%4d" % a), (20, "%4d" % b), (26, "UNP"), (33, acc), (42, "GLP1R_HUMAN"),
                   (55, "%5d" % ua), (62, "%5d" % ub)):
        line[i:i + len(txt)] = list(txt)
    return "".join(line).rstrip()


def fake_6x18(seed=3, chain_rec="R", chain_pep="P", uniprot_offset=None):
    """GLP-1 helix lying along the receptor helix at ~9 A; plus a dummy 'G protein' helix far away (chain A).
    uniprot_offset: write a DBREF record in which UniProt numbers = PDB numbers + offset."""
    rng = np.random.default_rng(seed)
    rs = receptor_seq(seed)
    rec = helix(rs, (0, 0, 0), chain=chain_rec, num0=REC_NUM0, rng=rng)
    pep = helix(GLP1_SEQ, (95, 10.8, 0), chain=chain_pep, num0=7, rng=rng, phase=1.2)
    gal = helix("A" * 60, (0, 80, 80), chain="A", num0=1, rng=rng)
    head = ["HEADER    SYNTHETIC TEST COMPLEX"]
    if uniprot_offset is not None:
        head.append(dbref_line("6X18", chain_rec, REC_NUM0, REC_NUM0 + REC_LEN - 1, REC_NUM0 + uniprot_offset, REC_NUM0 + REC_LEN - 1 + uniprot_offset))
    lines = head + pdb_text(rec + pep + gal).splitlines()
    return "\n".join(lines) + "\n", rs


EXENDIN_D3 = "HGDGTFTSDLSKQMEEEAVRLFIEWLKNGGPSSGAPPPS"


def fake_9byo(rs, seed=5, num_shift=100):
    """A second GLP-1R complex with a related peptide (exendin-like, one substitution), other chain ids, other residue numbers,
    and another orientation in space: for testing the superposition by sequence."""
    rng = np.random.default_rng(seed)
    rec = helix(rs, (0, 0, 0), chain="A", num0=REC_NUM0 + num_shift, rng=rng)
    pep = helix(EXENDIN_D3, (95, 10.8, 0), chain="B", num0=1, rng=rng, phase=1.0)
    gal = helix("A" * 100, (0, 80, 80), chain="C", num0=1, rng=rng)
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    t = rng.normal(0, 20, 3)
    atoms = [a[:5] + tuple(float(x) for x in (q @ np.array(a[5:8]) + t)) + a[8:] for a in rec + pep + gal]
    return "HEADER    SYNTHETIC SECOND COMPLEX\n" + pdb_text(atoms)


def make_design(rs, binder_seq, quality=1.0, hot_x=100.0, seed=0, offset=(0, 0)):
    """A 'designed' complex: receptor chain R (numbers kept), binder chain B placed near x=hot_x. quality<1 moves it away."""
    rng = np.random.default_rng(seed)
    rec = helix(rs, (0, 0, 0), chain=REC, num0=REC_NUM0, rng=np.random.default_rng(3))
    shift = (1.0 - quality) * 25.0
    # binder axis kept at ~10.8 A (touching) minus a quality dependent shift
    bind = helix(binder_seq, (hot_x - 8 + offset[0], 10.8 + shift + offset[1], 0), chain=BIND, num0=1, rng=rng,
                 phase=float(rng.uniform(0, 6)))
    return rec + bind


def make_prediction(design_atoms, rs, binder_seq, quality, seed=0, ref_rmsd=0.6):
    """Perturb the design, produce confidence and PAE whose level follows `quality` (0..1)."""
    rng = np.random.default_rng(seed)
    n_rec = len(rs); n_b = len(binder_seq)
    out = []
    for a in design_atoms:
        p = np.array(a[5:8])
        if a[0] == BIND:
            p = p + rng.normal(0, ref_rmsd * (1.6 - quality), 3)
        out.append(a[:5] + (float(p[0]), float(p[1]), float(p[2]), 70 + 25 * quality))
    pl = np.clip(np.r_[np.full(n_rec, 88.0), 55 + 38 * quality + rng.normal(0, 4, n_b)], 20, 98)
    pae = np.full((n_rec + n_b,) * 2, 28.0 - 22 * quality)
    pae[:n_rec, :n_rec] = 2.0; pae[n_rec:, n_rec:] = 3.0 - quality
    pae += np.abs(rng.normal(0, 0.4, pae.shape)); pae = (pae + pae.T) / 2
    conf = dict(ptm=round(0.55 + 0.35 * quality, 3), iptm=round(0.15 + 0.7 * quality, 3), plddt=[round(float(x), 1) for x in pl])
    return out, conf, np.clip(pae, 0, 31.75)


def npz_bytes(pae):
    buf = io.BytesIO(); np.savez(buf, pae=pae); return buf.getvalue()
