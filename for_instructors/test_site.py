#!/usr/bin/env python3
"""Check generated course pages, resource links and publication boundaries."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from build_site import CONTENT, DAYS, REPO, build, course_navigation, day_folder, page_manifest, published_files


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.references, self.images = set(), [], []
        self.h1_count = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        for attribute in ["href", "src"]:
            if attribute in attrs:
                self.references.append(attrs[attribute])
        if tag == "img":
            self.images.append(attrs)


class CourseSiteTests(unittest.TestCase):
    output = REPO / "_site"

    @classmethod
    def setUpClass(cls):
        cls.navigation = course_navigation()
        cls.pages = page_manifest(cls.navigation)
        cls.resources = published_files(cls.navigation)
        cls.documents = {path.relative_to(cls.output).as_posix(): Document(path.read_text())
                         for path in cls.output.rglob("*.html")}

    def test_every_course_page_is_generated(self):
        for page in self.pages:
            self.assertIn(page.route, self.documents)
            self.assertEqual(self.documents[page.route].h1_count, 1, page.route)
        for day in DAYS:
            self.assertIn(f"day{day['number']:02d}/index.html", self.documents)
        # Pages, plus any HTML a day's app publishes alongside them.
        app_documents = [route for route in self.resources.values() if route.endswith(".html")]
        self.assertEqual(len(self.documents), len(self.pages) + len(app_documents))

    def test_every_day_contributes_its_own_content(self):
        """A team adds Markdown or a resource to its day; the site picks it up."""
        routes = {page.source.resolve() for page in self.pages}
        for day in self.navigation:
            content = day_folder(day["number"]) / CONTENT
            self.assertTrue(content.is_dir(), content)
            for source in content.glob("*.md"):
                self.assertIn(source.resolve(), routes, source)
            for folder in ["assets", "downloads"]:
                for source in (content / folder).rglob("*"):
                    if source.is_file() and not source.name.startswith("."):
                        self.assertIn(source.resolve(), self.resources, source)

    def test_every_internal_link_and_fragment(self):
        # Include the project prefix to catch links that accidentally escape it.
        base = "https://course.example/UCPH-PhD-AI-data-driven-drug-design/"
        for route, doc in self.documents.items():
            for reference in doc.references:
                parsed = urlsplit(reference)
                if parsed.scheme or parsed.netloc:
                    continue
                absolute = urlsplit(urljoin(base + route, reference))
                self.assertTrue(absolute.path.startswith(urlsplit(base).path), (route, reference))
                relative = unquote(absolute.path[len(urlsplit(base).path):])
                if relative.endswith("/") or not relative:
                    relative += "index.html"
                target = self.output / relative
                self.assertTrue(target.is_file(), (route, reference, relative))
                if absolute.fragment and relative in self.documents:
                    self.assertIn(unquote(absolute.fragment), self.documents[relative].ids, (route, reference))

    def test_only_student_files_are_published(self):
        forbidden = {"for_instructors", "archive", "temp", ".git", "__pycache__"}
        for path in self.output.rglob("*"):
            self.assertFalse(forbidden.intersection(path.relative_to(self.output).parts), path)
            self.assertFalse(path.is_symlink(), path)
            self.assertNotIn(path.suffix, {".py", ".md", ".yml", ".yaml"}, path)
        for route in self.documents:
            text = (self.output / route).read_text()
            self.assertNotIn("for_instructors/", text, route)
        expected = {page.route for page in self.pages} | set(self.resources.values()) | {
            "assets/site.css", "assets/site.js", "assets/search.json", ".nojekyll", ".course-site-build"
        }
        actual = {path.relative_to(self.output).as_posix() for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(actual, expected)

    def test_day_apps_are_published_unchanged_and_embedded(self):
        for day in self.navigation:
            for app in day["features"]:
                self.assertEqual((app.directory / "index.html").read_bytes(),
                                 (self.output / app.entry_route).read_bytes())
                self.assertIn("app-frame", self.documents[app.page_route].ids, app.page_route)

    def test_worksheet_downloads_are_published_unchanged(self):
        downloads = {source: route for source, route in self.resources.items() if "/downloads/" in route}
        self.assertTrue(downloads, "expected at least one student download")
        for source, route in downloads.items():
            self.assertEqual(source.read_bytes(), (self.output / route).read_bytes())

    def test_lecture_slides_are_published_as_pdf_only(self):
        """Other formats in dayNN/lectures, such as PowerPoint, stay in the repository."""
        for day in self.navigation:
            for source in (day_folder(day["number"]) / "lectures").rglob("*"):
                if source.is_file() and not source.name.startswith("."):
                    self.assertEqual(source.resolve() in self.resources,
                                     source.suffix.lower() == ".pdf", source)
        for path in self.output.glob("day*/lectures/**/*"):
            if path.is_file():
                self.assertEqual(path.suffix.lower(), ".pdf", path)

    def test_search_covers_all_published_pages(self):
        index = json.loads((self.output / "assets/search.json").read_text())
        self.assertEqual({page["path"] for page in index}, {page.route for page in self.pages})
        self.assertEqual(len(index), len(self.pages))
        self.assertNotIn("for_instructors", json.dumps(index))

    def test_workshop_previous_and_next_navigation(self):
        for day in self.navigation:
            steps = day["steps"]
            for position, page in enumerate(steps):
                links = {urljoin("https://course.example/" + page.route, reference)
                         for reference in self.documents[page.route].references}
                if position:
                    self.assertIn("https://course.example/" + steps[position - 1].route, links)
                if position < len(steps) - 1:
                    self.assertIn("https://course.example/" + steps[position + 1].route, links)

    def test_workflow_matches_reviewed_template(self):
        self.assertEqual((REPO / ".github/workflows/pages.yml").read_bytes(),
                         (REPO / "for_instructors/site/pages.yml").read_bytes())

    def test_build_does_not_overwrite_unrelated_files(self):
        with tempfile.TemporaryDirectory() as folder:
            sentinel = Path(folder) / "keep.txt"
            sentinel.write_text("keep me")
            with self.assertRaises(ValueError):
                build(Path(folder))
            self.assertEqual(sentinel.read_text(), "keep me")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CourseSiteTests.output)
    args, rest = parser.parse_known_args()
    CourseSiteTests.output = args.output.resolve()
    unittest.main(argv=[__file__, *rest])
