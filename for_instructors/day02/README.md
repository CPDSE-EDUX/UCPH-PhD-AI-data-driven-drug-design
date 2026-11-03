# Day 2 instructor resources

Material for running the structure-based drug design workshop. None of it is published to the course website.

| Resource | Purpose |
| --- | --- |
| [Instructor notes](Instructor-notes.md) | Rehearsal, shared calculation settings, pooled docking, pacing and contingencies |
| [Dashboard setup](Dashboard-setup.md) | Configure the SMILES app and its Google Form / Sheet collection |
| [build_worksheets.py](build_worksheets.py) | Regenerate the Word and Excel group worksheets in `day02/workshop_content/downloads/` |
| [build_manual_word.py](build_manual_word.py) | Assemble the whole workshop into one Word review copy |

Run from the repository root:

```bash
python for_instructors/day02/build_worksheets.py   # needs openpyxl
python for_instructors/day02/build_manual_word.py  # needs python-docx, mistune<3, Pillow
```

Rebuild and re-check the site after regenerating the worksheets, because they are published as student downloads.

## Student-facing material

| Content | Location |
| --- | --- |
| Workshop guide and steps | [day02/workshop_content/](../../day02/workshop_content/index.md) |
| Group worksheets | [worksheets.md](../../day02/workshop_content/worksheets.md) |
| References | [references.md](../../day02/workshop_content/references.md) |
| SMILES submission app | [day02/apps/smiles/](../../day02/apps/smiles/index.html) |

[Instructor resources](../README.md) · [Day 2 overview](../../day02/README.md)
