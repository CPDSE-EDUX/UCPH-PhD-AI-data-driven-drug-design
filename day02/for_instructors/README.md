# Instructor resources

Use these files to prepare and maintain the workshop:

| Resource | Purpose |
| --- | --- |
| [Instructor notes](Instructor-notes.md) | Rehearsal, shared settings, pooled docking, timing and contingencies |
| [Dashboard setup](Dashboard-setup.md) | Configure the GitHub Pages app and Google Form / Sheet collection |
| [Website publishing](PUBLISHING.md) | Build, preview and publish the whole course through GitHub Pages |
| [Course site builder](build_site.py) | Render the overview, full program, five day pages and workshop; embed the existing SMILES app |
| [Site checks](test_site.py) | Check page coverage, links, downloads and exclusion of instructor files |
| [Site source](site/) | HTML template, CSS, browser interactions, dependencies and GitHub Actions workflow template |
| [Worksheet generator](build_worksheets.py) | Regenerate Word and Excel worksheets in the student downloads folder |

Run the maintenance commands from `day02`:

```bash
python for_instructors/build_site.py
python for_instructors/test_site.py
python for_instructors/build_worksheets.py
```

The site builder requires the packages in `site/requirements.txt`; the worksheet generator requires `openpyxl`. The publishing guide describes local preview and GitHub Actions deployment. Only the generated student site is uploaded to GitHub Pages.

[Day 2 overview](../README.md) · [Student manual](../workshop_manual/Home.md)
