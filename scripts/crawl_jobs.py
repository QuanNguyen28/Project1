from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.sources import GreenhouseSource, JobPosting, JsonLdSource, LeverSource


def _slug(value: str, limit: int = 50) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (value or "job")[:limit]


def _yaml_string(value: str) -> str:
    return json.dumps(value or "", ensure_ascii=False)


def write_posting(posting: JobPosting, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    external_hash = hashlib.sha256(posting.external_id.encode("utf-8")).hexdigest()[:12]
    code = f"{_slug(f'{posting.source_name}-{posting.company}', 32)}-{external_hash}"
    fetched_at = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    metadata = [
        "---",
        f"job_code: {_yaml_string(code)}",
        f"title: {_yaml_string(posting.title)}",
        f"department: {_yaml_string(posting.department)}",
        f"job_family: {_yaml_string(posting.department)}",
        f"employment_type: {_yaml_string(posting.employment_type)}",
        f"location: {_yaml_string(posting.location)}",
        f"source_name: {_yaml_string(posting.source_name)}",
        f"source_external_id: {_yaml_string(posting.external_id)}",
        f"source_company: {_yaml_string(posting.company)}",
        f"source_url: {_yaml_string(posting.source_url)}",
        f"source_published_at: {_yaml_string(posting.published_at.isoformat() if posting.published_at else '')}",
        f"source_fetched_at: {_yaml_string(fetched_at)}",
        f"source_hash: {_yaml_string(posting.content_hash)}",
        "tags: [real-data, public-job-posting]",
        "---",
        "",
        f"# {posting.title}",
        "",
        f"- **Company:** {posting.company}",
        f"- **Location:** {posting.location or 'Not specified'}",
        f"- **Employment type:** {posting.employment_type or 'Not specified'}",
        f"- **Original posting:** {posting.source_url}",
        "",
        "## Job description",
        "",
        posting.description.strip(),
        "",
        "## Source and provenance",
        "",
        f"Retrieved from the public {posting.source_name} job feed on {fetched_at} UTC.",
    ]
    path = output_dir / f"{code}.md"
    path.write_text("\n".join(metadata).strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect real public job postings with provenance")
    parser.add_argument("--source", choices=("greenhouse", "lever", "jsonld"), required=True)
    parser.add_argument("--site", help="Greenhouse board token or Lever site name")
    parser.add_argument("--company", required=True)
    parser.add_argument("--url", action="append", default=[], help="Explicit JSON-LD job page URL")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--output", default="data/real_jd")
    parser.add_argument("--region", choices=("global", "eu"), default="global")
    args = parser.parse_args()

    if args.source == "greenhouse":
        if not args.site:
            parser.error("--site is required for Greenhouse")
        postings = GreenhouseSource(args.site, args.company, delay_seconds=args.delay).fetch(args.limit)
    elif args.source == "lever":
        if not args.site:
            parser.error("--site is required for Lever")
        postings = LeverSource(
            args.site, args.company, region=args.region, delay_seconds=args.delay
        ).fetch(args.limit)
    else:
        if not args.url:
            parser.error("at least one --url is required for JSON-LD")
        postings = JsonLdSource(args.company, delay_seconds=args.delay).fetch_urls(args.url, args.limit)

    paths = [write_posting(posting, PROJECT_ROOT / args.output) for posting in postings]
    print(f"Collected {len(paths)} real postings in {PROJECT_ROOT / args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
