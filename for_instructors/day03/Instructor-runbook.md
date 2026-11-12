# Workshop 3 (GLP-1R binder design): instructor runbook

Day 3 of the PhD course "AI- and data-driven drug design". <br/>13:00 to 17:00, 30-40 students, 10 groups of 3-4, 2-3 staff.

## 1. Files

| File | Use |
|---|---|
| `Workshop3_GLP1R_binder_design.ipynb` | The student notebook. Helpers are embedded in the first (hidden) cell. |
| `ws3_helpers.py` | The same helper code as a file (needed only by `precompute.py` and the rehearsal kit). |
| `precompute.py` | Fills the stored-results pack by running the real API once with the base seed 2026 (also stores 6X18 and 9BYO). |
| `warm_cache.py` | Sends every request that does not depend on the students (10 groups × 3 default hotspot sets: RFD4 generate and the OpenFold3 re-run, plus the reference peptides) so that the server cache is full before class (section 8b). |
| `mock_server.py`, `synth.py`, `test_*.py` | Rehearsal kit: a fake server with the assumed API, so you can try the whole day without GPUs. |
| Pack: `ws3_pack.zip` | Output of `precompute.py` (folder `pack/`, zipped). Students upload it next to the notebook (or into Drive), or give `PACK_URL`; the notebook unzips it. |

## 1b. Running in Google Colab

The notebook runs on the default Colab **CPU** runtime (no GPU: the models run on your server). Hand students the `.ipynb` (File, Upload notebook in Colab, or put it in a shared Drive folder and open with Colab).

* **The API server must be reachable from Google's cloud over HTTPS.** Colab runs on Google infrastructure, so a server that is only visible inside the KU or UCloud network will not work. Check this first: from a Colab cell, `import urllib.request; print(urllib.request.urlopen("<SERVER>/health").read())`.
* **Cell 0.1** installs `py3Dmol`, `scipy`, `prolif` and `ipywidgets` if missing, with pip (`prolif` is optional: if it is missing or fails, the notebook says so and uses distance rules) and turns on Colab's custom widget manager. It is a collapsed form cell. **Cell 0.2** is a form (`#@param`): group (dropdown 1 to 10, nothing selected at the start), token, server, mode, `SAVE_TO`, `PACK_URL`. The server default in the form is `https://SERVER/api`; the token is not pre-filled.
* **Persistence:** `SAVE_TO = drive` (default) keeps everything in `MyDrive/ws3_data`. The Drive is mounted in **its own cell, 0.3** (`drive.mount` as the visible code of a cell; calling it from inside the hidden toolbox gave *credential propagation was unsuccessful*). If a student still gets that error: run 0.3 alone again and accept the pop-up, one Google account signed in, third-party cookies allowed for colab.research.google.com; otherwise `SAVE_TO = local`. This matters for the break: an idle Colab runtime may be disconnected, and without Drive the local `state.json` is lost (the server job survives, but the student loses the link to it). Students without a usable Google account can use `local` and should not close the tab during the break.
* **Stored results:** upload `ws3_pack.zip` to the Colab file browser or Drive (`MyDrive/ws3_pack.zip`), or put it on any direct download link and give that link as `PACK_URL`.
* **Show in 3D** in the fix picker may render nothing in Colab (output widgets and JavaScript); cell 5.2b shows the same view in the normal cell output and is the reliable route. The 3D views use hover labels (JavaScript passed to py3Dmol) and dashed cylinders for interactions: check them in Colab (section 7). Hand-written variants are separated by `;` in the Colab form (a form field has one line).
* **ProLIF (smoke test before the day):** run cells 0.1 to 1.3 in Colab. Cell 1.3 prints `Interactions calculated with: ProLIF <version>`; if it prints `simple distance rules`, run `PROLIF_STATE["error"]` in a cell to see why (typical causes: the install failed, RDKit could not read the structure, a change in the ProLIF API). Hydrogens are added with RDKit (`Chem.AddHs`), charges are set for Lys, Arg, Asp, Glu and the termini, and the interactions are Hydrophobic, HBDonor, HBAcceptor, Anionic, Cationic, CationPi, PiCation and PiStacking, grouped into H-bond, ionic and aromatic. Installing ProLIF takes about a minute in Colab. Results are cached per structure; the 3D view of a design needs a few seconds the first time.
* **Hand-in:** cell 6.5 zips `handin` and starts a browser download; with Drive the folder is also in the student's Drive.
* Tell students to use the default runtime and not to request a GPU.

## 2. Design decisions (so you can defend or change them)

* **Target:** full-length GLP-1R from 6X18 (receptor chain, numbering kept). GLP-1 and the receptor chain are found automatically as the short chain with most contacts to a long chain. The Gs chains stay out of the design and the predictions. Check cell 1.1 output on the day (section 7).
* **Goal:** a binder with the best evidence of binding in the lab. No agonist or antagonist question.
* **Binder length is fixed to the length of GLP-1 (30 residues)** for everybody, so all groups design the same size and hotspot-preset batches can be reused.
* **Seed = 2026 + group number** (`SEED = 2026`, group 3 sends 2029; the notebook prints it in cell 0.4). It is part of every request and of the fingerprint, so a group that repeats a request gets the same designs (and a cache hit), while two groups that choose the same hotspots get different designs. Two exceptions use the base seed 2026 itself: the five reference peptides of Step 2 (identical for all groups and computed once, then cached) and the stored-results pack (made with 2026 and served to every group, so in stored mode all groups with the same preset see the same designs). Consequence for throughput: generate and redesign jobs are never shared between groups, so budget the GPU time for all ten groups (section on throughput).
* **Request fingerprint** = SHA-1 of the sorted-key JSON of the task and these fields (`ws3_helpers.request_fingerprint`):
  * generate: `target_id, seed, n_designs` (15), `binder_length` (30), `hotspots` (sorted)
  * redesign: `target_id, seed, parent_id, fixed_positions` (sorted), `temperature` (3 decimals), `n_sequences`
  * predict: `target_id, seed, designs` as sorted `[id, sequence]` pairs

  The server should use the same key for its cache; `group` and `round` are deliberately not part of it, so groups with the same choices share results.
* **Step 4 is deliberately two-stage.** A `generate` job returns the RFD4-Proteina design files and the design server's own metrics only. The students look at those and at an overlay of all 15 binders, and then send the same sequences to OpenFold3 with a `predict` job (cell 4.5). **Redesign jobs still include the OpenFold3 evaluation** (design and evaluation in one job). `predict` is also used for the 5 reference peptides and for hand-written variants.
* **Scorecard:** metrics are kept separate, no combined score. Missing outputs stay missing (NaN), never zero. Interface = residues within 8 Å across the chains. Interface PAE = mean of both directions over those residues. ipSAE is a re-implementation (Dunbrack 2025, PAE cutoff 10) for teaching. Backbone RMSD = binder CA after fitting binder onto binder. Pose RMSD = binder CA after fitting the receptor CA within 12 Å of the designed binder, without moving the binder. Footprint overlap and cover compare the binder contacts with the receptor residues GLP-1 touches in 6X18 (4.5 Å heavy atoms). Teaching thresholds are in `THRESHOLDS` and students may change them with a reason. RFD4 metrics: the live server returns about 50 numeric metrics per design in a flat dictionary with dotted names (clashes, bond lengths, `hotspot_obedience`, inter-chain interaction counts, secondary structure, sequence adherence, `pre_oracle_pass`). The notebook shows 11 of them as `rfd4_*` columns (list `RFD4_CORE` in the helpers) and keeps all of them as `rfd4all_*` columns in the scorecard file. Design-file contacts computed by the notebook are the `des_*` columns. **Superposition:** every 3D comparison is first superposed on the receptor (Cα of the residues within 15 Å of GLP-1 in 6X18; Kabsch). 9BYO is placed on 6X18 by sequence alignment of the receptors.
* **Experimental data stays separate:** the only experimental information is the 6X18 contact table, exported to its own CSV. Everything in the scorecard is a computed prediction and is labelled so.

## 3. Assumed API

All paths are relative to `SERVER`. Auth: `Authorization: Bearer <group token>`. Status codes the client handles: 401/403 (token), 429 (too many running jobs for the group; suggested limit 3), 5xx (retried 3 times).

| Call | Purpose |
|---|---|
| `GET /health` | `{"status":"ok","models":{...},"backends":{...}}` (seen live: `{"status":"ok","models":{"openfold3":"fullfold","rfd4_proteina":"generate","proteinmpnn":"redesign"},"backends":{"gpu7":"up"}}`) |
| `POST /jobs/generate` | body: `target_id, seed, group, n_designs, binder_length, hotspots` (`["R:104", ...]`, chain R, 6X18 numbering) → `{"job_id": "..."}` |
| `POST /jobs/redesign` | body: `target_id, seed, group, parent_id, fixed_positions` (1-based binder positions), `temperature, n_sequences, round` |
| `POST /jobs/predict` | body: `target_id, seed, group, designs: [{"id","sequence"}, optionally "parent_id","mutations"]` |
| `GET /jobs/{id}` | `{"status": queued|running|succeeded|failed, "queue_position", "execution_mode": live|cache|precomputed, "result_id", "message"}` |
| `GET /results/{id}` | `{"result_id","model_version","designs":{"<id>":{"sequence","origin":"rfd4|mpnn","parent","round","artifacts":{"design","model","confidence","pae"},"metrics":{...}}}}` (a generate result has only `design` and `metrics`; a predict result has `model`, `confidence`, `pae`); artifact values are URLs or paths that `GET` returns (design/model: PDB text with receptor chain `R` and binder chain `B`, binder numbered from 1; confidence: JSON with `ptm`, `iptm`, `plddt` per residue; pae: `.npz` with array `pae`, receptor residues first) |

If your deployment differs (for example mmCIF output, atom-level pLDDT, a different PAE layout), change `ApiClient`, `load_pae`, `residue_plddt` and `parse_pdb` only; the rest of the notebook does not touch the raw formats. Design ids must be unique across groups and reproducible from the request (the mock uses a prefix of the fingerprint).

**Seen on the live server (6 Nov 2026):** the receptor construct is residues 29 to 405 of GLP-1R; a hotspot outside it, or not modelled in 6X18, is refused with HTTP 400 (`hotspot R:131 is outside the 29-405 construct or not modelled in 6X18`; the notebook prints this text as `NOT submitted`). The design file has receptor chain `R` (366 modelled residues, 29 to 405, B-factor 0) and binder chain `B` (1 to 30, all atoms). Predict results label the origin of a re-run design as `manual`; the notebook keeps the origin `rfd4` it already has. A single-peptide `predict` (GLP-1 with the receptor) took **40 s** of run time (`run_seconds` in the result). Result files are served at `/api/files/<result_id>/<design>/...`.

## 4. Throughput budget

The brief gives about 6 designs per minute per GPU for the full GLP-1R complex including peptide design, 4 GPUs, so about **24 designs per minute**. Measured on the live server on 6 Nov 2026 (only `gpu7` was listed as up): one OpenFold3 `predict` of GLP-1 with the receptor took 40 s, two designs in one job 46 s (`run_seconds`), which suggests about 35 s fixed cost plus about 6 s per extra design. That is two data points: **measure a batch of 15 and of 30 before the day**. The RFD4 generate time was not timed.

Load per cycle with 10 groups (15 designs per group, 25 + up to 5 manual variants per redesign round):

| | Designs | At 24/min (all stages) | OpenFold3 alone at the measured ~6 s per design, one GPU |
|---|---|---|---|
| RFD4 generate, 10 × 15 | 150 | 6.3 min | not applicable |
| OpenFold3 re-run of those, 10 × 15 | 150 | 6.3 min | about 15 min (about 4 min on four GPUs) |
| One redesign round (design + evaluation), 10 × 30 | 300 | 12.5 min | about 30 min (about 8 min on four GPUs) |
| Three rounds | 900 | 37.5 min | 90 min (23 min on four GPUs) |
| References (5, cached after the first group) | 5 | negligible | negligible |

* Step 4 now has a natural stagger: the OpenFold3 re-run starts only after the students have looked at the RFD4 output (a few minutes), so the load comes in a second wave. Slots (section 5) spread the generate jobs; the re-run waves spread themselves.
* If only one GPU is up, three rounds do not fit in the afternoon; the stored pack (section 8) then carries round 1, and rounds 2 and 3 are limited to what the server can do. Check `GET /health` (`backends`) before class.
* Caching is per group now (the seed is 2026 + the group number): a group that repeats a request gets a cache hit, but two groups never share a generate or re-run result, so budget the GPU time for all 10 groups. Only the five reference peptides (base seed 2026) are shared. The length is fixed at 30.
* Cap per group: 3 running jobs. Manual variants are limited to 5 per round.
* **There is no submission deadline in the notebook.** Announce the end of Step 5 yourself (16:15 in the schedule).

## 5. Rolling break and slots

Students submit in a slot of their own and then take the break; the notebook does not need to stay open and saves state to disk.

* Slot start for group *g* = 14:10 + 90 s × (g − 1), so 14:10:00 for group 1 to 14:23:30 for group 10 (`slot_for`). Write the slots on the board.
* The Step 3 work (hypothesis, length) is done before the slot; submission is one cell. The break is about 15 minutes after each group's own submission, back by 14:50.
* Round slots are not enforced; if the queue is long, staff announce a wave order (groups 1 to 4, then 5 to 7, then 8 to 10) instead.

## 6. Staffing (2-3 people)

Watch for: no hypothesis written, hotspots left at the default without thought, everything fixed in ProteinMPNN, metrics read as affinity.

## 7. Check before the day (pilot)

1. **6X18 on RCSB:** the PDB-format file exists (the notebook falls back to mmCIF). Cell 1.1 reports the chains: the receptor must be the chain with about 400 residues of full-length GLP-1R and the peptide the 30-residue GLP-1; if not, pass `rec_chain=` and `pep_chain=` to `S.load_reference`. Confirm the GLP-1 sequence printed matches your expectation (the helpers use GLP-1(7-36) only to label the scrambled control).
2. **API contract** against the real deployment (section 3), with a real token and the 429 limit.
3. **Residue numbering:** hotspots are `R:<6X18 number>`; the generation and prediction services must keep the 6X18 numbering for chain R, and the OpenFold3 model must use the same receptor construct (so receptor residue numbers line up for pose RMSD).
4. **Reference ranking:** the expected classes (GLP-1 and exendin-4 strong, oxyntomodulin moderate, glucagon weak, scrambled none) come from the literature in broad terms. Check them against the references you want to cite before class; they are labelled "expected", not measured.
5. **Metric sanity on real outputs:** run one group through the notebook; check that scrambled GLP-1 scores clearly below GLP-1 on ipTM and interface PAE, and that the teaching thresholds (ipTM ≥ 0.60, binder pLDDT ≥ 80, interface PAE ≤ 10 Å, backbone RMSD ≤ 2 Å, pose RMSD ≤ 3 Å, ≥ 50 % hotspots) are sensible. If the scrambled control passes, change the thresholds in `THRESHOLDS` (first cell) before class.
6. **Throughput:** run a 10-group rehearsal against the real servers (10 parallel notebooks or 10 scripted clients): 10 × generate (15), then 10 × re-run (15), then one redesign round (10 × 25 + 5). Compare with section 4.
7. **Widgets and Colab:** open the notebook in Colab (and, if you also offer it, on the UCloud image) with a student-like Google account. Check: cell 0.1 finishes without errors, the 0.2 form shows, Drive mounts in 0.3, the hotspot picker and fix picker render, 3D views appear (cells 1.2, 2.3, 2.3b, 4.3, 4.8 and 5.2b) with working hover labels and dashed interaction lines, the PAE plots show, and cell 6.5 downloads the zip. Check that `SERVER` is reachable from Colab (section 1b).
8. **Pack:** run `precompute.py` (below), zip, and test one student machine in `MODE = "stored"` with the server unreachable.
9. **Cache:** run `warm_cache.py --verify` (section 8b) and check in one notebook that cells 1.5 and 4.1 report `[cache]`.

## 8. Precompute the stored results

```
python precompute.py --server https://SERVER/api --token <admin token> --pdb 6X18.pdb --pdb2 9BYO.pdb --out ws3_data/pack
cd ws3_data && zip -r ../ws3_pack.zip pack
```

Stored: the 5 references; 3 generate batches (3 hotspot presets, binder length 30) with their OpenFold3 re-run; for each batch the 3 best designs by ipTM × 4 fix-presets (interface, core, interface + core, nothing) at temperature 0.20, 25 variants, round 1. That is 1 + 3 + 3 + 36 jobs and about 1 000 designs. The script also copies `6X18.pdb` and, with `--pdb2 9BYO.pdb`, the 9BYO structure into the pack so that Step 2 works offline. It resumes where it stopped. **Not stored:** custom hotspots, rounds 2 and 3, manual variants, other fix choices or temperatures; the notebook says so in plain words when a request is not in the pack. Add known interesting failures by running `precompute.py` with different parents if you want a teaching example for the discussion.

## 8b. Optional: warm the server cache before class

Because the seed is 2026 + the group number, the first request of each group is a cache miss unless somebody has sent it before. `warm_cache.py` sends exactly the requests a group will send when it picks one of the three default hotspot sets in cell 1.5 and runs cells 4.1 and 4.5 unchanged (binder length 30, 15 designs), all other requests depend much more on the group design steps and are not warmed:

```
python warm_cache.py --token <token> --pdb 6X18.pdb --verify        # all 10 groups, 3 sets, RFD4 + OpenFold3
python warm_cache.py --dry-run                                        # plan and estimate only, sends nothing
python warm_cache.py --token <token> --groups 1-5 --presets 1,3      # a part (e.g. to measure throughput first)
python warm_cache.py --token <token> --skip-of3                       # RFD4 only
```

* **What is sent:** 1 reference `predict` (base seed 2026, shared by all groups) + 30 `generate` + 30 `predict` (the OpenFold3 re-run of the sequences that `generate` returned) = 61 jobs. Payloads are built like the notebook builds them (`target_id`, `seed` = 2026 + group, `group`, hotspots sorted), so the fingerprints match. The test in `test_warm.py` runs the real `Session` code of groups 1, 7 and 10 after a warm-up and checks that all three presets and the references come back with `execution_mode: cache`, while a custom hotspot set does not.
* **Not sent:** ProteinMPNN `redesign`, the OpenFold3 evaluation of the redesigns, manual variants and generate requests with any other hotspots. They depend on the students' choices (the parent, the fixed positions, the temperature, the typed mutations) and are computed live.
* **Order and load:** `--concurrency 3` (default) runs three group/preset pipelines at a time, each generate followed by its re-run. On HTTP 429 (running-job limit) it waits `--backoff` seconds (30) and tries again; a failed job is retried twice; other errors are reported and the script goes on. Time estimate printed in the plan uses guessed durations (`--est-gen`, `--est-of3`); set them from your own measurements. If the server has one GPU the real time is closer to the serial figure printed by `--dry-run` (about 1.5 h with the defaults).
* **Resume and check:** run it again at any time; finished requests come back immediately with mode `cache`. `--verify` sends everything a second time and fails (exit code 1) if anything is not answered from the cache. The result is written to `warm_cache_report.json` (job ids, fingerprints, mode and seconds per request).
* **If the server's cache key differs from the fingerprint in `request_fingerprint`** (for example if it includes `group`), the warm-up still sends the right requests, but `--verify` will pass only if the key is stable. Check once by hand: warm group 1 with `--groups 1 --presets 1 --verify`, then run cells 1.5 and 4.1 as group 1 and see `[cache]` in the job line.
* Run it a few hours before class and again after any server restart; it does not replace the stored pack of section 8, which covers the case that the server is down.

## 9. Fallback rules

| Situation | Action |
|---|---|
| Job still `queued` 5 minutes after the group's slot | Set `MODE = "stored"` in cell 0.2 and re-run 0.4. The submitted job is replaced by the stored result for the same request, if it exists. In Step 4 the OpenFold3 re-run (cell 4.5) is stored as well. |
| Server unreachable | `MODE = "auto"` already falls back to the pack if `ws3_pack.zip` is present (TBD). |
| Failed job twice | Same as above; note it for the discussion. |
| Group chose custom hotspots and the server is slow | Ask them to use a preset, or give them a stored batch. |
| Notebook kernel died | Re-run 0.1 to 0.4 (cell 0.3, the Drive, in Colab); everything is restored from `ws3_data/group<NN>/state.json`. Do not re-run the submit cells; they refuse to send a job twice. |

## 10. After the course

Collect `handin/` folders (scorecard CSV, candidate card HTML, session JSON). `session_state.json` holds the time-stamped hypotheses, hotspots with reasons, fixed positions per round and decisions, which is useful for assessing the reasoning rather than the scores.
