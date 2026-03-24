#!/usr/bin/env python3
"""Migrate Hashnode markdown posts into Hugo-compatible content/blog files."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT_DIR = Path("/Users/a.vasiliu/git_repo/anvaplus/personal-blog")
SOURCE_DIR = ROOT_DIR / "hashnode_blog"
TARGET_DIR = ROOT_DIR / "content" / "blog"

HASHNODE_DOMAIN_PATTERN = re.compile(r"https://andreivasiliu\.com/([a-z0-9-]+)")
FILENAME_PATTERN = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\s*-\s*(.+)\.md$", re.IGNORECASE)

KNOWN_SLUGS_WITHOUT_FRONTMATTER = {
    "Why not a homelab?": "why-not-a-homelab",
    "From Enterprise to Homelab: Transforming My Home Network": "from-enterprise-to-homelab-transforming-my-home-network",
    "From Blueprint to Bare Metal: Building a Segmented Homelab Network": "from-blueprint-to-bare-metal-building-a-segmented-homelab-network",
    "Enterprise Kubernetes at Home - A Guide to Installing Talos Omni": "enterprise-kubernetes-at-home-a-guide-to-installing-talos-omni",
}

ALIASES_BY_CANONICAL_SLUG = {
    "the-four-repo-gitops-structure-for-my-homelab-platform": ["/four-repo-gitops-structure-homelab-platform/"],
    "the-database-dilemma-mastering-postgresql-on-kubernetes-with-cloudnativepg": ["/the-database-dilemma/"],
    "stop-outsourcing-identity-a-production-guide-to-keycloak-on-k8s": [
        "/stop-outsourcing-identity-a-production-guide-to-keycloak-on-kubernetes/"
    ],
    "how-i-chose-my-homelab-hardware-part-2": [
        "/how-i-chose-my-homelab-hardware-part-2-from-design-principles-to-physical-build/"
    ],
}


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    source_files = sorted(SOURCE_DIR.glob("*.md"))
    posts = [p for p in source_files if "linkedin" not in p.name.lower()]

    migrated_count = 0
    with_frontmatter_count = 0
    without_frontmatter_count = 0
    migrated_paths: List[Path] = []

    for post_file in posts:
        raw_content = post_file.read_text(encoding="utf-8")
        has_frontmatter = raw_content.startswith("---")

        if has_frontmatter:
            frontmatter, body = split_frontmatter(raw_content)
            output = migrate_with_frontmatter(frontmatter, body, post_file.name)
            with_frontmatter_count += 1
        else:
            output = migrate_without_frontmatter(raw_content, post_file.name)
            without_frontmatter_count += 1

        output_path = TARGET_DIR / f"{output['slug']}.md"
        output_path.write_text(render_hugo_post(output), encoding="utf-8")
        migrated_paths.append(output_path)
        migrated_count += 1

    print(f"Scanned {len(source_files)} markdown files in {SOURCE_DIR}")
    print(f"Excluded {len(source_files) - len(posts)} linkedin posts")
    print(f"Migrated {migrated_count} posts to {TARGET_DIR}")
    print(f"- With frontmatter: {with_frontmatter_count}")
    print(f"- Without frontmatter: {without_frontmatter_count}")
    for path in migrated_paths:
        print(f"  - {path.relative_to(ROOT_DIR)}")


def split_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content

    end_index: Optional[int] = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break

    if end_index is None:
        return {}, content

    frontmatter_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    frontmatter = parse_frontmatter_lines(frontmatter_lines)
    return frontmatter, body


def parse_frontmatter_lines(lines: List[str]) -> Dict[str, str]:
    data: Dict[str, str] = {}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = clean_yaml_scalar(value.strip())

    return data


def clean_yaml_scalar(value: str) -> str:
    if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
        return value[1:-1]
    return value


def parse_hashnode_date(value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError("Missing datePublished value")

    # First, handle ISO values such as 2026-02-25T10:00:00Z.
    try:
        iso_candidate = text.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_candidate)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat(timespec="seconds")
    except ValueError:
        pass

    # Handle verbose values such as: Sat Jan 03 2026 02:16:46 GMT+0000 (Coordinated Universal Time)
    normalized = re.sub(r"\s*\([^)]*\)\s*$", "", text)
    dt = datetime.strptime(normalized, "%a %b %d %Y %H:%M:%S GMT%z")
    return dt.isoformat(timespec="seconds")


def parse_tags(value: str) -> List[str]:
    if not value:
        return []
    tags = [tag.strip() for tag in value.split(",")]
    return [tag for tag in tags if tag]


def convert_internal_links(body: str) -> str:
    return HASHNODE_DOMAIN_PATTERN.sub(r"/\1/", body)


def find_first_paragraph(body: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    for paragraph in paragraphs:
        if paragraph.startswith("#"):
            continue
        if paragraph.startswith("!"):
            continue
        plain = re.sub(r"\s+", " ", paragraph)
        if plain:
            return plain[:160]
    return ""


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s-]", "", lowered)
    lowered = re.sub(r"[\s_]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered)
    return lowered.strip("-")


def extract_title_and_body(raw_content: str) -> Tuple[str, str]:
    lines = raw_content.splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = "\n".join(lines[1:]).lstrip("\n")
        return title, body

    for line in lines:
        if line.startswith("# "):
            return line[2:].strip(), raw_content

    return "", raw_content


def filename_date_to_iso(filename: str) -> str:
    match = FILENAME_PATTERN.match(filename)
    if not match:
        raise ValueError(f"Unable to parse date from filename: {filename}")

    year, month, day, _ = match.groups()
    dt = datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
    return dt.isoformat(timespec="seconds")


def migrate_with_frontmatter(frontmatter: Dict[str, str], body: str, filename: str) -> Dict[str, object]:
    title = frontmatter.get("title", "").strip()
    slug = frontmatter.get("slug", "").strip()

    if not slug:
        raise ValueError(f"Missing slug in frontmatter for: {filename}")

    date_value = parse_hashnode_date(frontmatter.get("datePublished", ""))
    description = frontmatter.get("seoDescription", "").strip()
    tags = parse_tags(frontmatter.get("tags", ""))
    featureimage = frontmatter.get("cover", "").strip()

    aliases = ALIASES_BY_CANONICAL_SLUG.get(slug, [])

    return {
        "title": title,
        "date": date_value,
        "slug": slug,
        "description": description,
        "tags": tags,
        "featureimage": featureimage if featureimage else None,
        "aliases": aliases if aliases else None,
        "body": convert_internal_links(body),
    }


def migrate_without_frontmatter(raw_content: str, filename: str) -> Dict[str, object]:
    title, body = extract_title_and_body(raw_content)
    if not title:
        match = FILENAME_PATTERN.match(filename)
        if not match:
            raise ValueError(f"Unable to infer title from filename: {filename}")
        title = match.group(4).strip()

    slug = KNOWN_SLUGS_WITHOUT_FRONTMATTER.get(title, slugify(title))

    date_value = filename_date_to_iso(filename)
    body = convert_internal_links(body)
    description = find_first_paragraph(body)

    aliases = ALIASES_BY_CANONICAL_SLUG.get(slug, [])

    return {
        "title": title,
        "date": date_value,
        "slug": slug,
        "description": description,
        "tags": ["homelab", "anvaplus"],
        "featureimage": None,
        "aliases": aliases if aliases else None,
        "body": body,
    }


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_hugo_post(post: Dict[str, object]) -> str:
    lines: List[str] = ["---"]
    lines.append(f"title: {quote_yaml(str(post['title']))}")
    lines.append(f"date: {quote_yaml(str(post['date']))}")
    lines.append(f"slug: {quote_yaml(str(post['slug']))}")
    lines.append(f"description: {quote_yaml(str(post['description']))}")

    tags = post.get("tags", []) or []
    tags_yaml = ", ".join(quote_yaml(str(tag)) for tag in tags)
    lines.append(f"tags: [{tags_yaml}]")

    featureimage = post.get("featureimage")
    if featureimage:
        lines.append(f"featureimage: {quote_yaml(str(featureimage))}")

    aliases = post.get("aliases")
    if aliases:
        aliases_yaml = ", ".join(quote_yaml(str(alias)) for alias in aliases)
        lines.append(f"aliases: [{aliases_yaml}]")

    lines.append("---")
    lines.append("")
    lines.append(str(post["body"]).rstrip())
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
