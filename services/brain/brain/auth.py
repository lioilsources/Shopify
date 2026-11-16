"""Shared-secret guard for write endpoints (/ingest, /admin/*).

The token lives only on the server side (brain + web BFF); browsers and the
mobile app never see it (plan 02, invariant 2). Without ADMIN_TOKEN the
endpoints are closed, not open.
"""

import hmac

from fastapi import Header, HTTPException

from brain.config import settings


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not settings.admin_token:
        raise HTTPException(503, "Admin je vypnutý: chybí ADMIN_TOKEN.")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, settings.admin_token):
        raise HTTPException(401, "Neplatný admin token.")
