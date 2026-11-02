#!/usr/bin/env python3
"""Build the student course website from an explicit list of repository content."""

import argparse
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
from urllib.parse import quote, unquote, urlsplit

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


REPO = Path(__file__).resolve().parents[2]
SITE_SOURCE = Path(__file__).resolve().parent / "site"
APP_URL = "https://cpdse-edux.github.io/UCPH-PhD-AI-data-driven-drug-design/day02/workshop_content/"
APP_ROUTE = "day02/workshop_content/index.html"
SUBMIT_ROUTE = "day02/submit/index.html"
MARKER = ".course-site-build"
DAYS = [
    {"number": 1, "date": "Monday, 9 November", "short_date": "Mon 09 Nov", "topic": "Databases", "tag": "Find the evidence", "summary": "Explore drug, target and disease data, then find the evidence for your own research questions."},
    {"number": 2, "date": "Tuesday, 10 November", "short_date": "Tue 10 Nov", "topic": "Structure-based drug design", "tag": "From structure to hypothesis", "summary": "Compare receptor binding sites, design ligands with and without AI, and evaluate them through docking."},
    {"number": 3, "date": "Wednesday, 11 November", "short_date": "Wed 11 Nov", "topic": "Peptide & protein design", "tag": "Explore molecular design", "summary": "Explore AI/ML tools for protein modeling, peptide design and mini-protein binders."},
    {"number": 4, "date": "Thursday, 12 November", "short_date": "Thu 12 Nov", "topic": "Data visualization", "tag": "Make the patterns visible", "summary": "Choose visual representations and use scripting tools and Claude to communicate data."},
    {"number": 5, "date": "Friday, 13 November", "short_date": "Fri 13 Nov", "topic": "Data analysis with AI/ML", "tag": "Turn data into insight", "summary": "Prepare molecular data, explore predictive machine learning and analyse data using Claude."},
]


@dataclass(frozen=True)
class Page:
    source: Path
    route: str
    title: str
    kind: str
    day: int = 0
    step: int = 0


def title_of(path):
    return next(line[2:].strip() for line in path.read_text().splitlines() if line.startswith("# "))


def page_manifest():
    pages = [Page(REPO / "README.md", "index.html", "AI & data-driven drug design", "home"),
             Page(REPO / "PROGRAM.md", "program/index.html", "Course program", "program")]
    for day in DAYS:
        number = day["number"]
        source = REPO / f"day{number:02d}" / "README.md"
        pages.append(Page(source, f"day{number:02d}/index.html", day["topic"], "day", number))
    manual = REPO / "day02/workshop_manual"
    pages.append(Page(manual / "Home.md", "day02/workshop/index.html", "Human vs AI: ligand design", "workshop", 2))
    steps = sorted(manual.glob("[0-9][0-9]-*.md"))
    if [p.name[:2] for p in steps] != [f"{n:02d}" for n in range(1, 19)]:
        raise ValueError("Expected exactly 18 numbered workshop steps")
    for step, source in enumerate(steps, 1):
        title = title_of(source).split(" · ", 1)[-1]
        pages.append(Page(source, f"day02/workshop/{source.stem.lower()}/index.html", title, "lesson", 2, step))
    pages += [
        Page(manual / "Group-worksheet.md", "day02/workshop/worksheets/index.html", "Group worksheets", "resource", 2),
        Page(manual / "References.md", "day02/workshop/references/index.html", "References & further reading", "resource", 2),
        Page(REPO / "day02/workshop_content/README.md", SUBMIT_ROUTE, "Submit your molecule designs", "submission", 2),
    ]
    if any(not page.source.is_file() for page in pages):
        raise ValueError("Missing course content")
    return pages


def published_files():
    """No recursive repository copy: enumerate student resources explicitly."""
    files = {}
    for name in ["logo_ku.png", "logo_cpdse.png", "hero.jpg", "index.html"]:
        source = REPO / "day02/workshop_content" / name
        files[source.resolve()] = f"day02/workshop_content/{name}"
    manual = REPO / "day02/workshop_manual"
    for source in (manual / "assets").glob("*.png"):
        files[source.resolve()] = f"day02/workshop/assets/{source.name}"
    for name in ["Group-worksheet.docx", "Group-worksheet.xlsx"]:
        files[(manual / "downloads" / name).resolve()] = f"day02/workshop/downloads/{name}"
    for name in ["LICENSE", "LICENSE-code"]:
        files[(REPO / name).resolve()] = f"licenses/{name}.txt"
    for source in files:
        if not source.is_file() or not source.is_relative_to(REPO):
            raise ValueError(f"Missing or unsupported resource: {source}")
    return files


def relative_url(current, target):
    return quote(posixpath.relpath(target, posixpath.dirname(current) or "."), safe="/-._~")


def student_markdown(page):
    text = page.source.read_text(encoding="utf-8")
    if page.source == REPO / "day02/README.md":
        # Repository maintenance sections are not participant instructions.
        text = re.split(r"^### (?:GitHub Wiki delivery|Website delivery)\s*$", text, maxsplit=1, flags=re.M)[0]
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    nav_prefixes = ("[Previous](", "[Home](", "[Start step 01](", "[Course overview](", "[Day 2](")
    return "\n".join(line for line in lines if not line.startswith(nav_prefixes)).strip()


class RenderedHTML(HTMLParser):
    def __init__(self, page, routes, resources):
        super().__init__(convert_charrefs=False)
        self.page, self.routes, self.resources = page, routes, resources
        self.parts = []

    def link(self, target):
        if target.rstrip("/") == APP_URL.rstrip("/"):
            return relative_url(self.page.route, SUBMIT_ROUTE)
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            return target
        source = (self.page.source.parent / unquote(parsed.path)).resolve()
        route = self.routes.get(source) or self.resources.get(source)
        if route is None:
            raise ValueError(f"Unpublished local link in {self.page.source.name}: {target}")
        return relative_url(self.page.route, route) + ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")

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
        self.parts.append("<" + tag + "".join(" " + key + ("=\"" + escape(value, quote=True) + "\"" if value is not None else "") for key, value in attrs.items()) + ">")

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
    pages, resources = page_manifest(), published_files()
    routes = {page.source.resolve(): page.route for page in pages}
    routes[(REPO / "day02/workshop_content/index.html").resolve()] = SUBMIT_ROUTE
    env = Environment(loader=FileSystemLoader(SITE_SOURCE), autoescape=select_autoescape(["html"]))
    template = env.get_template("page.html")
    steps = [page for page in pages if page.kind == "lesson"]
    search = []
    with tempfile.TemporaryDirectory(prefix=".course-build-", dir=output.parent) as temporary:
        staging = Path(temporary)
        (staging / MARKER).write_text("Generated student course site\n")
        (staging / ".nojekyll").touch()
        for source, route in resources.items():
            destination = staging / route
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        (staging / "assets").mkdir()
        for name in ["site.css", "site.js"]:
            shutil.copy2(SITE_SOURCE / name, staging / "assets" / name)
        for page in pages:
            url = lambda target: relative_url(page.route, target)
            md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])
            content = md.convert(student_markdown(page)) if page.kind != "home" else ""
            renderer = RenderedHTML(page, routes, resources)
            renderer.feed(content)
            content = "".join(renderer.parts)
            plain = PlainText()
            plain.feed(content)
            body_text = re.sub(r"\s+", " ", " ".join(plain.parts)).strip()
            description = body_text[:170] or "A University of Copenhagen PhD course in AI- and data-driven drug design, 9–13 November 2026."
            previous = steps[page.step - 2] if page.step > 1 else None
            following = steps[page.step] if page.step and page.step < 18 else None
            html = template.render(
                page=page, days=DAYS, steps=steps, url=url,
                content=content, toc=md.toc if content and md.toc_tokens else "", description=description,
                previous=previous, following=following,
                day_info=DAYS[page.day - 1] if page.day else None,
                app_route=APP_ROUTE, submit_route=SUBMIT_ROUTE,
            )
            destination = staging / page.route
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(html, encoding="utf-8")
            search.append({"title": page.title, "path": page.route, "section": f"Day {page.day}" if page.day else "Course", "text": body_text if page.kind != "home" else "AI data-driven drug design PhD University Copenhagen course overview November 2026"})
        (staging / "assets/search.json").write_text(json.dumps(search, ensure_ascii=False), encoding="utf-8")
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(staging, output)
    print(f"Built {len(pages)} course pages, the original SMILES app and {len(resources) - 1} resources in {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO / "day02/_site")
    args = parser.parse_args()
    build(args.output)
