from __future__ import annotations

import hashlib

import html

import json

import re

import time

from dataclasses import dataclass

from datetime import datetime, timezone

from typing import Any, Iterable, Optional

from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup

USER_AGENT = (
    "SmartHireResearchBot/1.0 (public job ingestion; contact your-org@example.com)"
)


def _plain_text(value: str | None) -> str:

    if not value:

        return ""

    soup = BeautifulSoup(html.unescape(value), "html.parser")

    return re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True)).strip()


def _parse_datetime(value: Any) -> Optional[datetime]:

    if not value:

        return None

    if isinstance(value, (int, float)):

        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).replace(
            tzinfo=None
        )

    text = str(value).strip().replace("Z", "+00:00")

    try:

        parsed = datetime.fromisoformat(text)

        if parsed.tzinfo:

            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)

        return parsed

    except ValueError:

        return None


@dataclass(frozen=True)
class JobPosting:

    source_name: str

    external_id: str

    company: str

    title: str

    description: str

    source_url: str

    department: str = ""

    location: str = ""

    employment_type: str = ""

    workplace_type: str = ""

    published_at: Optional[datetime] = None

    @property
    def content_hash(self) -> str:

        payload = "\n".join(
            (self.title, self.company, self.description, self.source_url)
        )

        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class BaseSource:

    def __init__(self, company: str, *, delay_seconds: float = 0.5):

        self.company = company

        self.delay_seconds = max(0.0, delay_seconds)

        self.session = requests.Session()

        self.session.headers.update(
            {"User-Agent": USER_AGENT, "Accept": "application/json"}
        )

    def _get_json(self, url: str, **kwargs) -> Any:

        response = self.session.get(url, timeout=30, **kwargs)

        response.raise_for_status()

        time.sleep(self.delay_seconds)

        return response.json()


class GreenhouseSource(BaseSource):
    """Official Greenhouse Job Board API adapter (published jobs only)."""

    def __init__(self, board_token: str, company: str, **kwargs):

        super().__init__(company, **kwargs)

        self.board_token = board_token

    def fetch(self, limit: Optional[int] = None) -> list[JobPosting]:

        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs"

        payload = self._get_json(url, params={"content": "true"})

        jobs = payload.get("jobs", [])[:limit]

        output: list[JobPosting] = []

        for job in jobs:

            departments = job.get("departments") or []

            output.append(
                JobPosting(
                    source_name="greenhouse",
                    external_id=str(job["id"]),
                    company=self.company,
                    title=str(job.get("title") or "Untitled role"),
                    description=_plain_text(job.get("content")),
                    source_url=str(job.get("absolute_url") or ""),
                    department=", ".join(
                        str(item.get("name"))
                        for item in departments
                        if item.get("name")
                    ),
                    location=str((job.get("location") or {}).get("name") or ""),
                    published_at=_parse_datetime(job.get("updated_at")),
                )
            )

        return output


class LeverSource(BaseSource):
    """Official Lever Postings API adapter (published jobs only)."""

    def __init__(self, site: str, company: str, *, region: str = "global", **kwargs):

        super().__init__(company, **kwargs)

        self.site = site

        self.region = region

    def fetch(self, limit: Optional[int] = None) -> list[JobPosting]:

        host = "api.eu.lever.co" if self.region == "eu" else "api.lever.co"

        jobs = self._get_json(
            f"https://{host}/v0/postings/{self.site}", params={"mode": "json"}
        )[:limit]

        output: list[JobPosting] = []

        for job in jobs:

            categories = job.get("categories") or {}

            output.append(
                JobPosting(
                    source_name="lever",
                    external_id=str(job["id"]),
                    company=self.company,
                    title=str(job.get("text") or "Untitled role"),
                    description=str(
                        job.get("descriptionPlain")
                        or _plain_text(job.get("description"))
                    ),
                    source_url=str(job.get("hostedUrl") or ""),
                    department=str(
                        categories.get("department") or categories.get("team") or ""
                    ),
                    location=str(categories.get("location") or ""),
                    employment_type=str(categories.get("commitment") or ""),
                    workplace_type=str(job.get("workplaceType") or ""),
                    published_at=_parse_datetime(job.get("createdAt")),
                )
            )

        return output


class JsonLdSource(BaseSource):
    """Extract schema.org JobPosting objects from explicitly supplied career URLs."""

    def fetch_urls(
        self, urls: Iterable[str], limit: Optional[int] = None
    ) -> list[JobPosting]:

        output: list[JobPosting] = []

        for page_url in urls:

            response = self.session.get(
                page_url, timeout=30, headers={"Accept": "text/html"}
            )

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for node in soup.select('script[type="application/ld+json"]'):

                try:

                    data = json.loads(node.string or "{}")

                except json.JSONDecodeError:

                    continue

                candidates = data if isinstance(data, list) else [data]

                for item in candidates:

                    if isinstance(item, dict) and "@graph" in item:

                        candidates.extend(item["@graph"])

                        continue

                    if not isinstance(item, dict) or item.get("@type") != "JobPosting":

                        continue

                    org = item.get("hiringOrganization") or {}

                    location = item.get("jobLocation") or {}

                    if isinstance(location, list):

                        location = location[0] if location else {}

                    address = location.get("address") or {}

                    external_id = str(
                        item.get("identifier", {}).get("value")
                        or item.get("url")
                        or page_url
                    )

                    output.append(
                        JobPosting(
                            source_name="jsonld",
                            external_id=external_id,
                            company=str(org.get("name") or self.company),
                            title=str(item.get("title") or "Untitled role"),
                            description=_plain_text(item.get("description")),
                            source_url=urljoin(
                                page_url, str(item.get("url") or page_url)
                            ),
                            location=", ".join(
                                filter(
                                    None,
                                    [
                                        str(address.get("addressLocality") or ""),
                                        str(address.get("addressCountry") or ""),
                                    ],
                                )
                            ),
                            employment_type=str(item.get("employmentType") or ""),
                            published_at=_parse_datetime(item.get("datePosted")),
                        )
                    )

                    if limit and len(output) >= limit:

                        return output

            time.sleep(self.delay_seconds)

        return output
