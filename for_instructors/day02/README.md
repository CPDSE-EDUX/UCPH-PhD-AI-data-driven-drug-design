# Day 2 instructor resources

Material for running the structure-based drug design workshop. None of it is published to the course website.

| Resource | Purpose |
| --- | --- |
| [Instructor notes](Instructor-notes.md) | Rehearsal, shared calculation settings, pooled docking, pacing and contingencies |
| [Dashboard setup](Dashboard-setup.md) | Configure the SMILES app and its Google Form / Sheet collection |
| [build_equations.py](build_equations.py) | Re-render the selectivity calculator's equation SVGs |
| [build_manual_word.py](build_manual_word.py) | Assemble the whole workshop into one Word review copy |

Run from the repository root:

```bash
python for_instructors/day02/build_equations.py    # needs matplotlib
python for_instructors/day02/build_manual_word.py  # needs python-docx, mistune<3, Pillow
```

Rebuild and re-check the site afterwards, because these outputs are published to students.

## Student-facing material

| Content | Location |
| --- | --- |
| Workshop guide and steps | [day02/workshop_content/](../../day02/workshop_content/index.md) |
| Setup and Maestro basics | [setup.md](../../day02/workshop_content/setup.md) · [maestro-basics.md](../../day02/workshop_content/maestro-basics.md) |
| References | [references.md](../../day02/workshop_content/references.md) |
| SMILES submission app | [day02/apps/smiles/](../../day02/apps/smiles/index.html) |
| Selectivity calculator | [day02/apps/selectivity/](../../day02/apps/selectivity/index.html) |

[Instructor resources](../README.md) · [Day 2 overview](../../day02/README.md)
