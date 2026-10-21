"""Shared helpers (copied verbatim from /home/claude/scrapers/_common.py on 2026-10-20 so
the pipeline directory is self-contained; keep the two in sync by hand).

Original docstring follows.

Shared helpers for the ledger scrapers.

Not a source script. It holds the few things every scraper needs to do the same way:

* ``fetch``: one HTTP call that turns "the file moved" into a clear ``SourceMovedError``
  instead of a pandas traceback. Public sites rarely return 404 for a moved file. They
  redirect to an HTML landing page, so the response is also checked against the expected
  file type (xlsx/pdf magic bytes, JSON parse, not-HTML for CSV).
* ``require_columns``: fail loudly with the columns actually found when a publisher
  renames a column. It never guesses.
* atomic, deterministic writers, so re-running a script replaces its outputs rather
  than appending, and fixture runs are byte-identical.
* ``fuel_group`` / ``is_data_centre_name``: the only two judgement calls shared
  across scripts, kept in one place so they can be audited.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

INSPECTED = "2026-10-20"  # date the source formats below were inspected via WebFetch/WebSearch
HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
DEFAULT_OUT = HERE / "out"

USER_AGENT = os.environ.get(
    "LEDGER_USER_AGENT",
    "ai-compute-footprint-ledger/0.1 (public-data research scraper)",
)


class SourceError(RuntimeError):
    """Base class for errors that should end a run with a clear message, not a traceback."""

    exit_code = 2


class SourceMovedError(SourceError):
    """The URL answered, but not with the file we expected (404/410, or an HTML page)."""

    exit_code = 3


class SourceUnreachableError(SourceError):
    """Network-level failure (DNS, TLS, proxy 403 on CONNECT, timeout)."""

    exit_code = 4


class SchemaChangedError(SourceError):
    """The file arrived but its columns/keys are not the ones this parser was written for."""

    exit_code = 5


class MissingCredentialError(SourceError):
    exit_code = 6


# --------------------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------------------

_MAGIC = {
    "xlsx": (b"PK\x03\x04",),
    "zip": (b"PK\x03\x04",),
    "pdf": (b"%PDF",),
}


def _looks_like_html(content: bytes) -> bool:
    head = content[:2048].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<html" in head[:512]


class Fetched:
    def __init__(self, url: str, final_url: str, content: bytes, headers: dict[str, str]):
        self.url = url
        self.final_url = final_url
        self.content = content
        self.headers = headers

    def text(self, encoding: str = "utf-8") -> str:
        return self.content.decode(encoding, errors="replace")

    def json(self) -> Any:
        return json.loads(self.content.decode("utf-8-sig"))


def fetch(
    url: str,
    *,
    expect: str,
    landing_page: str | None = None,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    data: Any = None,
    timeout: int = 180,
) -> Fetched:
    """Fetch ``url`` and check the payload is a ``expect`` file (xlsx|pdf|zip|json|csv|html).

    Raises SourceMovedError with a pointer to ``landing_page`` when the publisher has moved
    or renamed the file, and SourceUnreachableError when the host cannot be reached at all.
    """
    import requests  # imported lazily so --fixture runs do not need network libraries configured

    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    where = f" Check the landing page: {landing_page}" if landing_page else ""
    try:
        resp = requests.request(
            method, url, headers=hdrs, params=params, data=data, timeout=timeout, allow_redirects=True
        )
    except requests.RequestException as exc:  # DNS, TLS, proxy CONNECT denial, timeout
        raise SourceUnreachableError(f"Could not reach {url}: {exc}") from exc

    if resp.status_code in (404, 410):
        raise SourceMovedError(
            f"{url} returned HTTP {resp.status_code}: the file has probably moved or been renamed.{where} "
            "Update the URL constant at the top of the script, or download the file by hand and pass it "
            "with the script's local-file option (see --help)."
        )
    if resp.status_code in (401, 403):
        raise SourceMovedError(
            f"{url} returned HTTP {resp.status_code} (access denied). The endpoint may now need a key, "
            f"or blocks scripted access.{where}"
        )
    if resp.status_code >= 400:
        raise SourceUnreachableError(f"{url} returned HTTP {resp.status_code}: {resp.text[:300]!r}")

    content = resp.content
    moved_msg = (
        f"{url} (final URL {resp.url}) did not return a {expect} file "
        f"(Content-Type {resp.headers.get('Content-Type')!r}, {len(content)} bytes)."
        f" The file has probably moved and the old URL now redirects to a web page.{where}"
    )
    if expect in _MAGIC:
        if not content.startswith(_MAGIC[expect]):
            raise SourceMovedError(moved_msg)
    elif expect == "json":
        try:
            json.loads(content.decode("utf-8-sig"))
        except ValueError as exc:
            raise SourceMovedError(moved_msg + f" (JSON parse error: {exc})") from exc
    elif expect == "csv":
        if _looks_like_html(content) or not content.strip():
            raise SourceMovedError(moved_msg)
    elif expect == "html":
        pass
    else:
        raise ValueError(f"unknown expect={expect!r}")
    return Fetched(url, resp.url, content, dict(resp.headers))


# --------------------------------------------------------------------------------------
# Schema checks
# --------------------------------------------------------------------------------------


def require_columns(found: Iterable[str], required: Iterable[str], *, source: str, hint: str = "") -> None:
    found_list = [str(c) for c in found]
    missing = [c for c in required if c not in found_list]
    if missing:
        raise SchemaChangedError(
            f"{source}: expected column(s) {missing} not found. Columns present: {found_list}. "
            f"The publisher has changed the file layout; update the parser (do not guess). {hint}".strip()
        )


def strip_columns(df):
    df.columns = [str(c).strip() if c is not None else "" for c in df.columns]
    return df


def find_header_row(raw_rows: list[list[Any]], must_contain: Iterable[str], max_scan: int = 40) -> int:
    """Index of the first row whose stripped cell values include every name in ``must_contain``."""
    need = set(must_contain)
    for i, row in enumerate(raw_rows[:max_scan]):
        cells = {str(v).strip() for v in row if v is not None and str(v).strip() not in ("", "nan")}
        if need <= cells:
            return i
    return -1


# --------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def write_csv(df, path: Path) -> Path:
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    _atomic_write_bytes(Path(path), buf.getvalue().encode("utf-8"))
    return Path(path)


def write_json(obj: Any, path: Path) -> Path:
    text = json.dumps(obj, indent=2, ensure_ascii=False, default=_json_default) + "\n"
    _atomic_write_bytes(Path(path), text.encode("utf-8"))
    return Path(path)


def write_bytes(data: bytes, path: Path) -> Path:
    _atomic_write_bytes(Path(path), data)
    return Path(path)


def _json_default(o: Any) -> Any:
    try:
        import numpy as np  # noqa: F401

        if hasattr(o, "item"):
            return o.item()
    except ImportError:
        pass
    if isinstance(o, (_dt.date, _dt.datetime)):
        return o.isoformat()
    return str(o)


def run_meta(fixture: bool, sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Provenance block written at the top of every summary JSON."""
    return {
        "mode": "fixture" if fixture else "live",
        "fixture_warning": (
            "FIXTURE RUN: numbers come from the small sample files in fixtures/, not the full "
            "source. They test parsing only and must not be quoted as real totals."
            if fixture
            else None
        ),
        "format_inspected": INSPECTED,
        # retrieved_at is omitted in fixture mode so repeated fixture runs are byte-identical
        "retrieved_at": None if fixture else _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "sources": sources,
    }


def round_mw(x: Any, nd: int = 1) -> Any:
    try:
        return round(float(x), nd)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------------------
# Shared judgement calls (kept here so they can be audited in one place)
# --------------------------------------------------------------------------------------

# Conservative: only explicit wording. Many data centres hide behind SPV names; this flag is a
# lower bound, never a census.
DC_NAME_RE = re.compile(r"data[\s_-]?cent(?:er|re)s?|datacent(?:er|re)|hyperscale", re.IGNORECASE)


def is_data_centre_name(name: Any) -> bool:
    return bool(name) and bool(DC_NAME_RE.search(str(name)))


_GAS_RE = re.compile(
    r"natural\s*gas|\bgas\b|\bng\b|\bctg\b|combined[\s-]*cycle|combustion\s*turbine|"
    r"\bcc\b|\bct\b|\bcc-|\bct-|-ng\b|dual\s*fuel|\breciprocating\b",
    re.IGNORECASE,
)


def fuel_group(raw: Any) -> str:
    """Map an ISO's free-text fuel/technology label to a small set of groups.

    The raw label is always kept next to the group in every output. Dual-fuel (gas/oil)
    units are grouped as gas. Multi-technology labels (e.g. 'Solar/Storage') are 'hybrid'.
    """
    s = "" if raw is None else str(raw).strip()
    if not s or s.lower() in {"nan", "none", "not specified", "unknown", "tbd"}:
        return "unknown"
    low = s.lower()
    kinds = set()
    if re.search(r"solar|photovoltaic|\bpv\b", low):
        kinds.add("solar")
    if re.search(r"wind", low):
        kinds.add("wind")
    if re.search(r"storage|batter|\bbess\b|flywheel", low):
        kinds.add("storage")
    if _GAS_RE.search(low):
        kinds.add("gas")
    if "hybrid" in low or len(kinds) >= 2:
        return "hybrid"
    if kinds:
        return kinds.pop()
    if "nuclear" in low:
        return "nuclear"
    if "hydro" in low or "pumped" in low:
        return "hydro"
    if "coal" in low:
        return "coal"
    if re.search(r"transmission|\bac\b|\bdc\b", low):
        return "transmission"
    if low in {"load", "l"}:
        return "load"
    return "other"


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def base_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"output directory (default: {DEFAULT_OUT}). Files are overwritten, never appended.",
    )
    p.add_argument(
        "--fixture",
        action="store_true",
        help="parse the sample files in fixtures/ instead of downloading (offline parser test)",
    )
    return p


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def run_main(fn) -> None:
    """Run ``fn`` and turn SourceError into a one-paragraph message plus a non-zero exit code."""
    try:
        fn()
    except SourceError as exc:
        log(f"ERROR ({type(exc).__name__}): {exc}")
        sys.exit(exc.exit_code)
