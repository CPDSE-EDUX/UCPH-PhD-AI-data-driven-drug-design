# Day 3 instructor resources

Material for running the *de novo* binder design workshop (GLP-1R).

| Resource | Purpose |
| --- | --- |
| [Instructor runbook](Instructor-runbook.md) | What was tested, API contract, throughput budget, rolling-break slots, staffing, pre-day checks and the stored-results fallback |
| [rehearsal_kit/](rehearsal_kit/) | Helpers, a mock server and tests to rehearse the whole day without GPUs, `precompute.py` for the stored-results pack, and `warm_cache.py` to fill the server cache before class |

The runbook names the student notebook, [Workshop3_GLP1R_binder_design.ipynb](../../day03/workshop_content/Workshop3_GLP1R_binder_design.ipynb), and the scripts it refers to. They all live in [rehearsal_kit/](rehearsal_kit/), so run the commands in the runbook from that folder. `ws3_helpers.py` there holds the same helper code that is embedded in the notebook's first cell, and `make_nb.py` generates the notebook. The kit is stored as plain files because the repository ignores archives.

## Student-facing material

| Content | Location |
| --- | --- |
| Workshop guide | [day03/workshop_content/index.md](../../day03/workshop_content/index.md) |
| Student notebook | [Workshop3_GLP1R_binder_design.ipynb](../../day03/workshop_content/Workshop3_GLP1R_binder_design.ipynb) |

[Instructor resources](../README.md) · [Day 3 overview](../../day03/README.md)
