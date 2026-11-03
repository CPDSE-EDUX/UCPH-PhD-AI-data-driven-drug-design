#!/usr/bin/env python3
"""Build the student course website from the content each day keeps in workshop_content/.

Each day contributes Markdown in `dayNN/workshop_content/` and optional browser
features in `dayNN/apps/<name>/`. Nothing here is specific to a single day: add a
file, and the matching page, navigation entry and search record follow.

Runs on Python 3.9 or newer, so that any reasonably current environment can
build the site.
"""

# Keeps "App | None" and similar annotations from being evaluated on Python 3.9.
from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit

if sys.version_info < (3, 9):
    raise SystemExit(
        "The course site builder needs Python 3.9 or newer; this is "
        f"{sys.version.split()[0]} at {sys.executable}. Activate a newer "
        "environment, or create one with the packages in site/requirements.txt."
    )

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


REPO = Path(__file__).resolve().parents[1]
SITE_SOURCE = Path(__file__).resolve().parent / "site"
BRAND_SOURCE = REPO / "assets/brand"
CONTENT = "workshop_content"
APPS = "apps"
SITE_URL = "https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/"
MARKER = ".course-site-build"

# Course-level metadata for the home page and day navigation. Session tables,
# workshop steps and resources are read from the Markdown sources instead.
# "image" names a banner in assets/brand/; "alt" describes it for screen readers.
HOME_BANNER = {
    "image": "course-overview.jpg",
    "alt": "Fresco in the style of the Creation of Adam: a human hand reaching towards a robotic hand.",
}
DAYS = [
    {"number": 1, "date": "Monday, 9 November", "short_date": "Mon 09 Nov",
     "topic": "Databases", "tag": "Find the evidence",
     "summary": "Explore drug, target and disease data, then find the evidence for your own research questions.",
     "image": "day01-databases.jpg",
     "alt": "Fresco-style illustration: a human hand and a robotic hand arranging molecules and biomedical data in a cabinet of glass cases."},
    {"number": 2, "date": "Tuesday, 10 November", "short_date": "Tue 10 Nov",
     "topic": "Structure-based drug design", "tag": "From structure to hypothesis",
     "summary": "Compare receptor binding sites, design ligands with and without AI, and evaluate them through docking.",
     "image": "day02-structure-based-design.jpg",
     "alt": "Fresco-style illustration: a human hand and a robotic hand fitting a small molecule into a protein binding pocket."},
    {"number": 3, "date": "Wednesday, 11 November", "short_date": "Wed 11 Nov",
     "topic": "Peptide & protein design", "tag": "Explore molecular design",
     "summary": "Explore AI/ML tools for protein modeling, peptide design and mini-protein binders.",
     "image": "day03-protein-design.jpg",
     "alt": "Fresco-style illustration: a human hand offering a peptide chain while a robotic hand shapes it into a protein helix."},
    {"number": 4, "date": "Thursday, 12 November", "short_date": "Thu 12 Nov",
     "topic": "Data visualization", "tag": "Make the patterns visible",
     "summary": "Choose visual representations and use scripting tools and Claude to communicate data.",
     "image": "day04-data-visualization.jpg",
     "alt": "Fresco-style illustration: a human hand and a robotic hand arranging scattered data points into a chart on a glass panel."},
    {"number": 5, "date": "Friday, 13 November", "short_date": "Fri 13 Nov",
     "topic": "Data analysis with AI/ML", "tag": "Turn data into insight",
     "summary": "Prepare molecular data, explore predictive machine learning and analyse data using Claude.",
     "image": "day05-data-analysis.jpg",
     "alt": "Fresco-style illustration: a human hand and a robotic hand drawing clusters and a trend out of scattered data points."},
]

# A line that is only cross-reference links is repository navigation; the site
# generates its own breadcrumbs, sidebar and pagination instead.
NAV_LINE = re.compile(r"^(?:\[[^\]]+\]\([^)]+\)|·|\s)+$")


@dataclass(frozen=True)
class App:
    """A browser feature a day publishes next to its Markdown pages."""

    day: int
    name: str
    directory: Path
    entry_route: str
    page_route: str
    source: Path
    title: str
    nav_label: str
    heading: str
    blurb: str


@dataclass(frozen=True)
class Page:
    source: Path
    route: str
    title: str
    kind: str
    day: int = 0
    step: int = 0
    app: App | None = None


def title_of(path):
    """The first level-one heading, which every content file must provide."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError(f"No level-one heading in {path.relative_to(REPO)}")


def day_folder(number):
    return REPO / f"day{number:02d}"


def read_apps(number):
    """Discover `dayNN/apps/<name>/app.json` features for one day."""
    apps = []
    for definition in sorted((day_folder(number) / APPS).glob("*/app.json")):
        meta = json.loads(definition.read_text(encoding="utf-8"))
        directory = definition.parent
        entry = meta.get("entry", "index.html")
        source = day_folder(number) / CONTENT / meta["page"]
        if not (directory / entry).is_file():
            raise ValueError(f"App entry point missing: {directory.relative_to(REPO)}/{entry}")
        if not source.is_file():
            raise ValueError(f"App page missing: {source.relative_to(REPO)}")
        apps.append(App(
            day=number, name=directory.name, directory=directory,
            entry_route=f"day{number:02d}/{APPS}/{directory.name}/{entry}",
            page_route=f"day{number:02d}/{meta['route']}/index.html",
            source=source,
            title=meta.get("title") or title_of(source),
            nav_label=meta.get("nav_label", meta.get("title", directory.name)),
            heading=meta.get("heading", ""), blurb=meta.get("blurb", ""),
        ))
    return apps


def day_pages(number):
    """Pages, steps, resources and apps contributed by one day, in reading order."""
    content = day_folder(number) / CONTENT
    apps = read_apps(number)
    claimed = {app.source.resolve() for app in apps}
    prefix = f"day{number:02d}/workshop"

    workshop = None
    if (content / "index.md").is_file():
        workshop = Page(content / "index.md", f"{prefix}/index.html",
                        title_of(content / "index.md"), "workshop", number)

    steps = sorted(content.glob("[0-9][0-9]-*.md"))
    if [path.name[:2] for path in steps] != [f"{n:02d}" for n in range(1, len(steps) + 1)]:
        raise ValueError(f"Day {number} workshop steps must be numbered consecutively from 01")
    step_pages = [
        Page(source, f"{prefix}/{source.stem.lower()}/index.html",
             title_of(source).split(" · ", 1)[-1], "lesson", number, position)
        for position, source in enumerate(steps, 1)
    ]

    resources = [
        Page(source, f"{prefix}/{source.stem.lower()}/index.html", title_of(source), "resource", number)
        for source in sorted(content.glob("*.md"))
        if source.name != "index.md" and source.resolve() not in claimed and source not in steps
    ]
    app_pages = [Page(app.source, app.page_route, app.title, "app", number, app=app) for app in apps]
    return {"workshop": workshop, "steps": step_pages, "resources": resources,
            "apps": app_pages, "features": apps}


def course_navigation():
    """Day metadata joined with the pages each day actually provides."""
    navigation = []
    for banner in [HOME_BANNER, *DAYS]:
        if not (BRAND_SOURCE / banner["image"]).is_file():
            raise ValueError(f"Missing banner image: assets/brand/{banner['image']}")
    for day in DAYS:
        source = day_folder(day["number"]) / "README.md"
        if not source.is_file():
            raise ValueError(f"Missing day description: {source.relative_to(REPO)}")
        navigation.append({**day, **day_pages(day["number"]),
                           "page": Page(source, f"day{day['number']:02d}/index.html",
                                        day["topic"], "day", day["number"])})
    return navigation


def page_manifest(navigation=None):
    navigation = navigation or course_navigation()
    pages = [Page(REPO / "README.md", "index.html", "AI & data-driven drug design", "home"),
             Page(REPO / "PROGRAM.md", "program/index.html", "Course program", "program")]
    for day in navigation:
        pages.append(day["page"])
        if day["workshop"]:
            pages.append(day["workshop"])
        pages += day["steps"] + day["resources"] + day["apps"]
    missing = [page.source for page in pages if not page.source.is_file()]
    if missing:
        raise ValueError(f"Missing course content: {missing}")
    return pages


def published_files(navigation=None):
    """No recursive repository copy: enumerate student resources explicitly."""
    navigation = navigation or course_navigation()
    files = {}
    for source in sorted(BRAND_SOURCE.iterdir()):
        if source.is_file() and not source.name.startswith("."):
            files[source.resolve()] = f"assets/brand/{source.name}"
    for day in navigation:
        content = day_folder(day["number"]) / CONTENT
        for folder in ["assets", "downloads"]:
            for source in sorted((content / folder).glob("*")):
                if source.is_file() and not source.name.startswith("."):
                    files[source.resolve()] = f"day{day['number']:02d}/workshop/{folder}/{source.name}"
        for app in day["features"]:
            for source in sorted(app.directory.rglob("*")):
                if not source.is_file() or source.name in {"app.json", ".DS_Store"}:
                    continue
                relative = source.relative_to(app.directory).as_posix()
                files[source.resolve()] = f"day{day['number']:02d}/{APPS}/{app.name}/{relative}"
    for name in ["LICENSE", "LICENSE-code"]:
        files[(REPO / name).resolve()] = f"licenses/{name}.txt"
    for source in files:
        if not source.is_file() or not source.is_relative_to(REPO):
            raise ValueError(f"Missing or unsupported resource: {source}")
    return files


def relative_url(current, target):
    return quote(posixpath.relpath(target, posixpath.dirname(current) or "."), safe="/-._~")


def student_markdown(page):
    """Markdown body without its heading or repository navigation lines."""
    lines = page.source.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(line for line in lines if not NAV_LINE.match(line)).strip()


class RenderedHTML(HTMLParser):
    """Rewrites repository links to site routes and hardens the generated markup."""

    def __init__(self, page, routes, resources, aliases):
        super().__init__(convert_charrefs=False)
        self.page, self.routes, self.resources, self.aliases = page, routes, resources, aliases
        self.parts = []

    def link(self, target):
        if target.rstrip("/") in self.aliases:
            return relative_url(self.page.route, self.aliases[target.rstrip("/")])
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            return target
        source = (self.page.source.parent / unquote(parsed.path)).resolve()
        route = self.routes.get(source) or self.resources.get(source)
        if route is None:
            raise ValueError(f"Unpublished local link in {self.page.source.name}: {target}")
        return (relative_url(self.page.route, route)
                + ("?" + parsed.query if parsed.query else "")
                + ("#" + parsed.fragment if parsed.fragment else ""))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            if key in attrs:
                attrs[key] = self.link(attrs[key])
        if tag == "img":
            attrs.update(loading="lazy", decoding="async")
        if tag == "th":
            attrs["scope"] = "col"
        if tag == "table":
            self.parts.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable table">')
        self.parts.append("<" + tag + "".join(
            " " + key + ("=\"" + escape(value, quote=True) + "\"" if value is not None else "")
            for key, value in attrs.items()) + ">")

    def handle_endtag(self, tag):
        self.parts.append(f"</{tag}>")
        if tag == "table":
            self.parts.append("</div>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.parts.append(data)

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, text):
        self.parts.append(text)


def build(output):
    output = output.expanduser().resolve()
    if output == REPO or REPO.is_relative_to(output):
        raise ValueError("Build output cannot be the repository or one of its parents")
    if output.exists() and any(output.iterdir()) and not (output / MARKER).is_file():
        raise ValueError("Refusing to overwrite a non-empty directory without a course build marker")
    output.parent.mkdir(parents=True, exist_ok=True)

    navigation = course_navigation()
    pages, resources = page_manifest(navigation), published_files(navigation)
    routes = {page.source.resolve(): page.route for page in pages}
    # Links written to a feature's published location or public URL open its course page.
    aliases = {}
    for day in navigation:
        for app in day["features"]:
            page_route = app.page_route
            routes.setdefault((app.directory / "index.html").resolve(), app.entry_route)
            aliases[(SITE_URL + posixpath.dirname(app.entry_route)).rstrip("/")] = page_route
            aliases[(SITE_URL + f"day{day['number']:02d}/{CONTENT}").rstrip("/")] = page_route

    env = Environment(loader=FileSystemLoader(SITE_SOURCE), autoescape=select_autoescape(["html"]))
    template = env.get_template("page.html")
    search = []
    with tempfile.TemporaryDirectory(prefix=".course-build-", dir=output.parent) as temporary:
        staging = Path(temporary)
        (staging / MARKER).write_text("Generated student course site\n")
        (staging / ".nojekyll").touch()
        for source, route in resources.items():
            destination = staging / route
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        (staging / "assets").mkdir(exist_ok=True)
        for name in ["site.css", "site.js"]:
            shutil.copy2(SITE_SOURCE / name, staging / "assets" / name)

        for page in pages:
            day = navigation[page.day - 1] if page.day else None
            steps = day["steps"] if day else []
            url = lambda target: relative_url(page.route, target)
            md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])
            content = md.convert(student_markdown(page)) if page.kind != "home" else ""
            renderer = RenderedHTML(page, routes, resources, aliases)
            renderer.feed(content)
            content = "".join(renderer.parts)
            plain = PlainText()
            plain.feed(content)
            body_text = re.sub(r"\s+", " ", " ".join(plain.parts)).strip()
            description = body_text[:170] or (
                "A University of Copenhagen PhD course in AI- and data-driven drug design, 9–13 November 2026.")
            html = template.render(
                page=page, days=navigation, steps=steps, url=url, content=content,
                toc=md.toc if content and md.toc_tokens else "", description=description,
                previous=steps[page.step - 2] if page.step > 1 else None,
                following=steps[page.step] if page.step and page.step < len(steps) else None,
                day_info=day, site_url=SITE_URL, home_banner=HOME_BANNER,
            )
            destination = staging / page.route
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(html, encoding="utf-8")
            search.append({
                "title": page.title, "path": page.route,
                "section": f"Day {page.day}" if page.day else "Course",
                "text": body_text if page.kind != "home" else
                        "AI data-driven drug design PhD University Copenhagen course overview November 2026",
            })
        (staging / "assets/search.json").write_text(json.dumps(search, ensure_ascii=False), encoding="utf-8")
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(staging, output)

    features = sum(len(day["features"]) for day in navigation)
    print(f"Built {len(pages)} course pages, {features} day app(s) and {len(resources)} resources in {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO / "_site")
    build(parser.parse_args().output)
