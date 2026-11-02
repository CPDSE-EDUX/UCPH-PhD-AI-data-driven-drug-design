# Publish the course with GitHub Pages

The course website is built from this repository and deployed through GitHub Actions. The build includes the course overview, full program, five day pages, the complete Day 2 workshop, worksheet downloads and the existing SMILES collection app.

**Publication target:** <https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/>

## Content and site source

| Edit | Source |
| --- | --- |
| Repository course description | [Course README](../../README.md) |
| Full schedule and teaching staff | [PROGRAM.md](../../PROGRAM.md) |
| Day descriptions and session tables | Each day's `README.md` |
| Day 2 workshop steps and worksheets | [Workshop manual](../workshop_manual/Home.md) |
| Existing SMILES collection interface | [workshop_content/index.html](../workshop_content/index.html) |
| Homepage copy, learning outcomes, layout and visual style | [page.html](site/page.html), [site.css](site/site.css), [site.js](site/site.js) |
| Course navigation and content selection | [build_site.py](build_site.py) |
| Automated checks | [test_site.py](test_site.py) |

The build reads an explicit list of student Markdown pages and resource files. It renders student content from the day READMEs, omitting repository administration sections. Instructor files, archives, temporary files, source scripts and repository metadata are not copied into the published site.

The home page layout and short course-day summaries are defined in the template and builder. Update those summaries if the course structure changes. Day session tables and workshop instructions are rendered from their Markdown sources.

## Build and preview locally

From the repository root, create a Python environment and install the small site dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r day02/for_instructors/site/requirements.txt
python day02/for_instructors/build_site.py
python day02/for_instructors/test_site.py
python -m http.server 8000 --directory day02/_site
```

Open `http://localhost:8000/`. Stop the preview with Ctrl+C. Search loads a JSON index, so use the HTTP preview instead of opening HTML files directly from disk.

The default generated output is `day02/_site/`, which is ignored by Git. To use another output directory, pass the same `--output` argument to the builder and checks. The builder refuses to overwrite an unrelated non-empty directory.

## Enable GitHub Pages

1. Commit the course content, site source, both Word/Excel worksheet files and `.github/workflows/pages.yml` to this repository.
2. In **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**. If Pages was serving the repository directly, switch it to this source so only the generated student site is published.
3. Push to `main`, or run **Publish course website** through the Actions tab. Pull requests build and check the site without deploying.
4. Confirm that the build checks pass and the deployment job succeeds. The workflow publishes only its `_site` artifact through the `github-pages` environment.
5. Open the deployment URL and verify the course navigation, worksheet downloads, search, workshop progress and SMILES collection interface.

The workflow follows GitHub's [custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). No separate Wiki repository is needed. The workflow template is retained at [site/pages.yml](site/pages.yml); update the installed repository-root workflow when changing it.

## SMILES collection

- **Embedded course page:** `/day02/submit/`
- **Existing standalone app:** `/day02/workshop_content/`

Both use the same app, Google Form and Sheet configuration. The build copies the original app unchanged, preserving its IDs, structure validation, dashboard and `.smi` export. The embedded page also offers an open-in-new-tab link. See [dashboard setup](Dashboard-setup.md) for collection configuration.

The browser must be able to reach the app's existing RDKit CDN and Google collection endpoints. Website search and workshop navigation do not depend on those services. Browser checks should exercise previews and navigation without submitting test molecules into the live collection.

## Word and Excel worksheets

The downloadable files are versioned at `day02/workshop_manual/downloads/`. To regenerate them, use a Python environment with `openpyxl` installed:

```bash
python day02/for_instructors/build_worksheets.py
```

Rebuild and check the course site after regenerating the worksheets. Participants submit SMILES through the web app and use either worksheet for observations, returned compound IDs, predictions and analysis.

[Instructor resources](README.md) · [Day 2 overview](../README.md)
