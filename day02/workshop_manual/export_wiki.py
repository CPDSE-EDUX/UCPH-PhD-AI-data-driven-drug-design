#!/usr/bin/env python3
"""Stage the workshop manual for a GitHub Wiki; never publish or run git."""

import argparse
from pathlib import Path
import re
import shutil
from urllib.parse import quote, urlparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New or empty staging directory")
    parser.add_argument(
        "--wiki-url",
        default="https://github.com/cpdse-edux/UCPH-PhD-AI-data-driven-drug-design/wiki",
    )
    parser.add_argument(
        "--prefix", default="Day02-",
        help="Page namespace; use an empty string only for a standalone workshop wiki",
    )
    args = parser.parse_args()
    wiki_url = args.wiki_url.rstrip("/")
    parsed = urlparse(wiki_url)
    parts = parsed.path.strip("/").split("/")
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or len(parts) != 3 or parts[-1] != "wiki"
            or not all(re.fullmatch(r"[A-Za-z0-9_.-]+", p) for p in parts[:2])
            or parsed.query or parsed.fragment):
        parser.error("--wiki-url must be https://github.com/OWNER/REPOSITORY/wiki")
    if not re.fullmatch(r"[A-Za-z0-9-]*", args.prefix):
        parser.error("--prefix may contain only letters, digits and hyphens")

    source = Path(__file__).resolve().parent
    destination = args.destination.expanduser().resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        parser.error("destination must be a new or empty directory; existing files are never overwritten")

    pages = sorted(source.glob("[0-9][0-9]-*.md")) + [
        source / name for name in (
            "Home.md", "Group-worksheet.md", "Instructor-notes.md", "References.md", "_Sidebar.md"
        )
    ]
    if len(pages) != 23 or any(not page.is_file() for page in pages):
        parser.error("expected 18 step pages plus Home, worksheet, instructors, references and sidebar")
    names = {
        page.name: (
            args.prefix + "Navigation" if args.prefix else "_Sidebar"
        ) if page.stem == "_Sidebar" else args.prefix + page.stem
        for page in pages
    }
    asset_directory = "assets/" + (args.prefix.rstrip("-") or "manual")
    raw_root = f"https://raw.githubusercontent.com/wiki/{parts[0]}/{parts[1]}"
    resources = {}

    def rewrite_link(match):
        target = match.group(1)
        if urlparse(target).scheme or target.startswith(("#", "//")):
            return match.group(0)
        path, separator, fragment = target.partition("#")
        if path in names:
            return "](" + wiki_url + "/" + quote(names[path]) + (separator + fragment) + ")"
        if path.startswith(("assets/", "downloads/")):
            resource_type = path.split("/", 1)[0]
            asset = (source / path).resolve()
            if asset.parent != (source / resource_type).resolve() or not asset.is_file():
                raise ValueError(f"Missing or unsupported resource: {path}")
            if resource_type == "downloads" and asset.suffix not in (".docx", ".xlsx"):
                raise ValueError(f"Unsupported worksheet download: {path}")
            output_directory = asset_directory if resource_type == "assets" else "downloads/" + (args.prefix.rstrip("-") or "manual")
            output_path = output_directory + "/" + asset.name
            resources[asset] = output_path
            return "](" + raw_root + "/" + quote(output_path, safe="/") + ")"
        raise ValueError(f"Unresolved local link: {target}")

    rendered = {}
    for page in pages:
        rendered[names[page.name] + ".md"] = re.sub(
            r"\]\(([^\s)]+)\)", rewrite_link, page.read_text(encoding="utf-8")
        )

    destination.mkdir(parents=True, exist_ok=True)
    for name, content in rendered.items():
        (destination / name).write_text(content, encoding="utf-8")
    for asset, output_path in sorted(resources.items()):
        target = destination / output_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset, target)
    images = sum(path.startswith("assets/") for path in resources.values())
    downloads = sum(path.startswith("downloads/") for path in resources.values())
    print(f"Staged {len(rendered)} Markdown files, {images} images and {downloads} downloads in {destination}")
    print(f"Landing page after publication: {wiki_url}/{names['Home.md']}")
    if args.prefix:
        print(f"Merge {names['_Sidebar.md']}.md navigation into the course wiki sidebar as appropriate.")


if __name__ == "__main__":
    main()
