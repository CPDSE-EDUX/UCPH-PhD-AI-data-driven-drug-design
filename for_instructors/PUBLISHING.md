# Publish the course with GitHub Pages

The website is built from this repository and deployed through GitHub Actions. It covers the course overview, the full program, the suggested follow-up courses, all five day pages, and each day's workshop content and apps.

**Publication target:** <https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/>

## What to edit

| Edit | Source |
| --- | --- |
| Course description and home page copy | [Course README](../README.md), [page.html](site/page.html) |
| Full schedule and teaching staff | [PROGRAM.md](../PROGRAM.md) |
| Suggested follow-up courses | [FOLLOW-UP-COURSES.md](../FOLLOW-UP-COURSES.md) |
| Photos from the week | That day's `photos/` folder and `photos.json` |
| A day's description and session table | That day's `README.md` |
| A day's workshop pages, images and downloads | That day's `workshop_content/` |
| A day's browser app | That day's `apps/<name>/` |
| Day summaries, tags and banner images | `DAYS` in [build_site.py](build_site.py) |
| Banner and logo image files | `assets/brand/` |
| Layout and visual style | [page.html](site/page.html), [site.css](site/site.css), [site.js](site/site.js) |
| Automated checks | [test_site.py](test_site.py) |

[Adding content](ADDING-CONTENT.md) describes the per-day conventions. The builder reads an explicit list of student files: instructor folders, archives, temporary files and repository metadata are not copied into the published site, and the checks fail if any of them appear.

## Build and preview locally

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r for_instructors/site/requirements.txt
python for_instructors/build_site.py
python for_instructors/test_site.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/` and stop the preview with Ctrl+C. Search loads a JSON index, so use the HTTP preview rather than opening HTML files from disk.

The builder needs **Python 3.9 or newer** and the two packages in `site/requirements.txt`; GitHub Actions uses 3.12. A dedicated virtual environment avoids picking up an old conda environment that happens to be active.

The default output is `_site/`, which is ignored by Git. To use another directory, pass the same `--output` to the builder and the checks. The builder refuses to overwrite a non-empty directory that it did not generate.

## Enable GitHub Pages

1. Commit the course content, the site source, any student downloads and `.github/workflows/pages.yml`.
2. In **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**.
3. Push to `main`, or run **Publish course website** from the Actions tab. Pull requests build and check the site without deploying.
4. Confirm the checks pass and the deployment job succeeds. Only the generated `_site` artifact is published, through the `github-pages` environment.
5. Open the deployment URL and check navigation, images, downloads, search, workshop progress and any embedded apps.

The workflow follows GitHub's [custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). Its reviewed copy is kept at [site/pages.yml](site/pages.yml); a check compares the two, so update both together.

## Day 2: SMILES collection

- **Course page:** `/day02/submit/`
- **Standalone app:** `/day02/apps/smiles/`

Both serve the same app, Google Form and Sheet configuration. The build copies the app unchanged, preserving its structure validation, dashboard and `.smi` export, and a check compares the published bytes with the source. See [Day 2 dashboard setup](day02/Dashboard-setup.md) for the collection configuration.

The browser must be able to reach the app's RDKit CDN and Google endpoints. Site search and workshop navigation do not depend on those services. Exercise previews and navigation when testing, without submitting molecules into the live collection.

## Student downloads

Day 2 publishes the Maestro cheat sheets and Schrödinger installation guides from `day02/workshop_content/downloads/`. Anything dropped in a day's `downloads/` folder is published as a student download; the same convention applies to any day.

Groups no longer fill in a spreadsheet — the [selectivity calculator](../day02/apps/selectivity/index.html) does the score arithmetic in the browser.

[Instructor resources](README.md) · [Adding content](ADDING-CONTENT.md)
