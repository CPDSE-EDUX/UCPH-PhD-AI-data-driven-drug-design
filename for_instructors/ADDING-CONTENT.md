# Adding your day's content

The course website is built from the Markdown each day keeps in `dayNN/workshop_content/`. Add a file there, rebuild, and its page, navigation entry and search record appear. You do not need to change the builder.

## Where content goes

| Path | Becomes |
| --- | --- |
| `dayNN/README.md` | The day page at `/dayNN/`, with your session table |
| `dayNN/lectures/` | Lecture slides. PDFs are published at `/dayNN/lectures/` and linked from the day page as `lectures/your-slides.pdf`; other formats, such as PowerPoint, stay in the repository, so link to them on GitHub |
| `dayNN/workshop_content/index.md` | Your workshop landing page at `/dayNN/workshop/` |
| `dayNN/workshop_content/01-your-topic.md` | Step 01 at `/dayNN/workshop/01-your-topic/`, in the sidebar with previous/next links |
| `dayNN/workshop_content/your-topic.md` | A resource page at `/dayNN/workshop/your-topic/`, listed under Quick access |
| `dayNN/workshop_content/assets/` | Images at `/dayNN/workshop/assets/`, linked from Markdown as `assets/your-file.png`; subfolders are preserved |
| `dayNN/workshop_content/downloads/` | Student downloads, linked as `downloads/your-file.docx`; subfolders are preserved (for example, `downloads/Round_1/data.csv`) |
| `dayNN/apps/<name>/` | A browser app at `/dayNN/apps/<name>/`, plus a course page that embeds it |
| `dayNN/photos/` with `photos.json` | Small photo thumbnails at the end of the day page and, for the whole week, on the home page; selecting one opens a viewer |

Day 2 is a worked example of all of these.

## Conventions the build enforces

The build fails rather than publishing something broken, so a failing check is a message about your content, not a problem with the site.

- **One level-one heading per file**, on the first line. It becomes the page title.
- **Numbered steps run consecutively from `01`.** Use a two-digit prefix and a slug: `04-prepare-your-data.md`. A step title may carry its number (`# 04 · Prepare your data`); the site strips the prefix for the sidebar.
- **Every local link must point at published content.** Linking to a file the site does not publish — anything in `for_instructors/`, a scratch file, a notebook — stops the build. Use an external URL for material that lives elsewhere.
- **A line of only links** separated by `·` is treated as repository navigation and dropped from the web page, because the site generates its own breadcrumbs and previous/next links. Keep such lines if you want the Markdown to read well on GitHub.
- **Instructor material is never published.** Keep rehearsal notes, answer keys and generator scripts in `for_instructors/dayNN/`.

Steps are the ordered walkthrough a participant follows once. Resources are the pages they jump back to: setup guides, references, cheat sheets.

## Adding an app

An app is any self-contained browser feature: a form, a dashboard, a visualization. Put it in `dayNN/apps/<name>/` with an `index.html` and an `app.json`:

```json
{
  "route": "submit",
  "page": "submit.md",
  "title": "Submit your molecule designs",
  "nav_label": "Submit molecule designs",
  "heading": "Your group's designs",
  "blurb": "One sentence shown above the embedded app."
}
```

| Key | Meaning |
| --- | --- |
| `route` | URL segment for the course page that embeds the app: `/dayNN/<route>/` |
| `page` | A Markdown file in your `workshop_content/` providing the text around the app |
| `title` | Page heading; defaults to the Markdown file's own heading |
| `nav_label` | Sidebar label under Quick access |
| `heading`, `blurb` | Text in the panel header above the embedded app |
| `entry` | Entry file, if not `index.html` |

Everything else in the app folder is published unchanged at `/dayNN/apps/<name>/`, so the app also works as a standalone page. Shared course images live in `assets/brand/` at the repository root; reference them from an app as `../../../assets/brand/<file>`.

## Your day's banner

Each day page opens with a wide illustration from `assets/brand/`, named `dayNN-topic.jpg` and declared with its alt text in the `DAYS` list in [build_site.py](build_site.py):

```python
"image": "day04-data-visualization.jpg",
"alt": "Fresco-style illustration: a human hand and a robotic hand arranging scattered data points into a chart on a glass panel.",
```

Keep the proportions at roughly **3:1** so the banners line up across days, export at about **2000 px wide as JPEG** (quality 82 gives ~200 KB), and write alt text that describes the picture for someone who cannot see it. The build fails if a declared image is missing, so a typo is caught before publication.

## Adding photos

Put the photos in `dayNN/photos/` and list them, in the order to show them, in `dayNN/photos/photos.json`:

```json
[
  {
    "file": "lecture-08-1.jpg",
    "caption": "Lecture 8 · Rodrigo Alonso Ochoa, Novo Nordisk A/S",
    "detail": "Modelling and cheminformatics approaches for peptide analysis and design",
    "alt": "The speaker beside the blue title slide of the lecture."
  }
]
```

| Key | Meaning |
| --- | --- |
| `file` | A JPEG, PNG or WebP file in the same folder |
| `caption` | Shown in the viewer and on hover, usually the session and speaker |
| `detail` | Optional second line in the viewer, such as the talk title |
| `alt` | What the photo shows, for someone who cannot see it |

Export each photo as an upright JPEG about **1600 px** on its long side with all metadata removed, for example with squoosh.app. Phone photos carry GPS coordinates, so the checks fail if a published photo still has EXIF or XMP metadata. Keep the original files out of the repository, and only publish photos of people who have agreed to be on the website.

## Build and preview

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r for_instructors/site/requirements.txt
python for_instructors/build_site.py
python for_instructors/test_site.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. Search loads a JSON index, so preview over HTTP rather than opening files from disk. The generated `_site/` is ignored by Git; pushing to `main` rebuilds and publishes it.

Any Python 3.9 or newer works. If you use conda, activate an environment deliberately rather than relying on whichever `python` comes first on your path — the builder reports the version it is running under if it is too old.

Your day's summary line and tag on the home page and sidebar come from the `DAYS` list in [build_site.py](build_site.py). Edit your own entry there if the topic changes.

[Instructor resources](README.md) · [Publishing](PUBLISHING.md)
