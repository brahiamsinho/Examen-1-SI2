# Resolución de slug de tenant desde Host (subdominio) sin consultar BD.
from __future__ import annotations

import re

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slug_from_host(host: str | None, platform_base_domain: str | None = None) -> str | None:
    """
    Extrae slug de tenant del host.
    Ej.: demo-sc.localhost → demo-sc; demo-sc.app.ejemplo.com con base app.ejemplo.com.
    """
    if not host or not str(host).strip():
        return None
    h = str(host).split(":")[0].lower().strip()
    if not h:
        return None

    if h.endswith(".localhost"):
        sub = h[: -len(".localhost")]
        if sub and "." not in sub and _SLUG_RE.match(sub):
            return sub

    base = (platform_base_domain or "").strip().lower().lstrip(".")
    if base and (h == base or h.endswith(f".{base}")):
        if h == base:
            return None
        sub = h[: -(len(base) + 1)]
        if sub and "." not in sub and _SLUG_RE.match(sub):
            return sub

    return None
