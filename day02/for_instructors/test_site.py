#!/usr/bin/env python3
"""Check generated course pages, resource links and publication boundaries."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from build_site import APP_ROUTE, REPO, build, page_manifest, published_files


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
    output = REPO / "day02/_site"

    @classmethod
    def setUpClass(cls):
        cls.documents = {path.relative_to(cls.output).as_posix(): Document(path.read_text()) for path in cls.output.rglob("*.html")}

    def test_complete_course_and_workshop(self):
        self.assertEqual(len(page_manifest()), 29)
        self.assertEqual(len(self.documents), 30)
        for page in page_manifest():
            self.assertIn(page.route, self.documents)
            self.assertEqual(self.documents[page.route].h1_count, 1, page.route)
        for number in range(1, 6):
            self.assertIn(f"day{number:02d}/index.html", self.documents)

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
            self.assertNotIn("export_wiki", text, route)
        expected = {page.route for page in page_manifest()} | set(published_files().values()) | {
            "assets/site.css", "assets/site.js", "assets/search.json", ".nojekyll", ".course-site-build"
        }
        actual = {path.relative_to(self.output).as_posix() for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(actual, expected)

    def test_original_smiles_app_and_downloads_are_unchanged(self):
        source = REPO / "day02/workshop_content/index.html"
        self.assertEqual(source.read_bytes(), (self.output / APP_ROUTE).read_bytes())
        for name in ["Group-worksheet.docx", "Group-worksheet.xlsx"]:
            self.assertEqual((REPO / "day02/workshop_manual/downloads" / name).read_bytes(),
                             (self.output / "day02/workshop/downloads" / name).read_bytes())
        self.assertIn("smiles-app", self.documents["day02/submit/index.html"].ids)

    def test_search_covers_all_published_pages(self):
        index = json.loads((self.output / "assets/search.json").read_text())
        self.assertEqual({page["path"] for page in index}, {page.route for page in page_manifest()})
        self.assertEqual(len(index), 29)
        self.assertNotIn("for_instructors", json.dumps(index))

    def test_workshop_previous_and_next_navigation(self):
        steps = [page for page in page_manifest() if page.step]
        for position, page in enumerate(steps):
            links = {urljoin("https://course.example/" + page.route, ref) for ref in self.documents[page.route].references}
            if position:
                self.assertIn("https://course.example/" + steps[position - 1].route, links)
            if position < 17:
                self.assertIn("https://course.example/" + steps[position + 1].route, links)

    def test_workflow_matches_reviewed_template(self):
        self.assertEqual((REPO / ".github/workflows/pages.yml").read_bytes(),
                         (REPO / "day02/for_instructors/site/pages.yml").read_bytes())

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
