# Instructor resources

Shared tooling for the course website, plus one folder per day for that day's teaching material.

| Resource | Purpose |
| --- | --- |
| [Adding content](ADDING-CONTENT.md) | How each day contributes Markdown, images, downloads and apps |
| [Website publishing](PUBLISHING.md) | Build, preview and publish the course through GitHub Pages |
| [build_site.py](build_site.py) | Render every day's content into the student website |
| [test_site.py](test_site.py) | Check pages, links, downloads and publication boundaries |
| [site/](site/) | HTML template, styles, browser interactions, dependencies and the workflow template |
| [day02/](day02/) | Day 2 workshop notes, submission-app setup and the equation renderer |

Nothing in this folder is published. The builder reads an explicit list of student files, and the checks fail if instructor material, archives or temporary files reach the output.

## Routine commands

Run from the repository root:

```bash
python -m pip install -r for_instructors/site/requirements.txt
python for_instructors/build_site.py
python for_instructors/test_site.py
```

## Adding a day

Each day owns `dayNN/README.md` and `dayNN/workshop_content/`, and may add `dayNN/apps/<name>/` for browser features. Put that day's instructor-only material in `for_instructors/dayNN/`. [Adding content](ADDING-CONTENT.md) has the conventions; Day 2 is a complete worked example.

[Course overview](../README.md) · [Full program](../PROGRAM.md)
