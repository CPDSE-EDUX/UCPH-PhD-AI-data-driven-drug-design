# Instructor resources

Use these files to prepare and maintain the workshop:

| Resource | Purpose |
| --- | --- |
| [Instructor notes](Instructor-notes.md) | Rehearsal, shared settings, pooled docking, timing and contingencies |
| [Dashboard setup](Dashboard-setup.md) | Configure the GitHub Pages app and Google Form / Sheet collection |
| [Wiki publishing](PUBLISHING.md) | Stage and publish the student manual and downloadable worksheets |
| [Wiki exporter](export_wiki.py) | Export student pages, screenshots and worksheets; excludes instructor files |
| [Worksheet generator](build_worksheets.py) | Regenerate Word and Excel worksheets in the student downloads folder |

Run the maintenance commands from `day02`:

```bash
python3 for_instructors/export_wiki.py /tmp/day02-wiki-review
python for_instructors/build_worksheets.py
```

The worksheet generator requires `openpyxl` in the selected Python environment. The publishing guide describes review and deployment; neither script publishes changes automatically.

[Day 2 overview](../README.md) · [Student manual](../workshop_manual/Home.md)
