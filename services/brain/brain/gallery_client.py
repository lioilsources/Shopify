"""Read-only client for the FineTuneGallery shop export (plan 05, part A).

Contract (docs/GALLERY_EXPORT.md):
  GET /api/export/collections/{slug}?since=<cursor>&cursor=<page>
      -> {"items": [...], "next": <page cursor or null>, "until": <cursor for next run>}
  GET /api/export/img/{sha256} -> original bytes (only images present in the export)
Auth: bearer SHOP export token + Cloudflare Access service token headers.
"""

from collections.abc import Iterator
from typing import Any

import httpx

from brain.config import settings


class GalleryExport:
    def __init__(self, transport: httpx.BaseTransport | None = None, base_url: str | None = None):
        headers = {"Authorization": f"Bearer {settings.gallery_export_token}"}
        if settings.gallery_cf_client_id:
            headers["CF-Access-Client-Id"] = settings.gallery_cf_client_id
            headers["CF-Access-Client-Secret"] = settings.gallery_cf_client_secret
        self._http = httpx.Client(
            base_url=(base_url or settings.gallery_url).rstrip("/"),
            headers=headers,
            timeout=settings.gallery_timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._http.close()

    def changes(self, collection: str, since: str | None) -> Iterator[tuple[list[dict[str, Any]], str | None]]:
        """Yield (items, until) per page; `until` of the last page is the next cursor."""
        page: str | None = None
        while True:
            params = {k: v for k, v in {"since": since, "cursor": page}.items() if v}
            res = self._http.get(f"/api/export/collections/{collection}", params=params)
            res.raise_for_status()
            body = res.json()
            yield list(body.get("items") or []), body.get("until")
            page = body.get("next")
            if not page:
                return

    def image(self, sha256: str) -> bytes:
        res = self._http.get(f"/api/export/img/{sha256}")
        res.raise_for_status()
        return res.content
