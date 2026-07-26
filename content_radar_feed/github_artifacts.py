"""Restore complete TrendRadar snapshots from GitHub Actions artifacts."""
from __future__ import annotations

import json
from pathlib import PurePosixPath
from typing import Callable, Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile
import io


ARTIFACT_PREFIX = "trendradar-snapshot"
API_ROOT = (
    "https://api.github.com/repos/Anxin-tec/"
    "content-radar-feed/actions/artifacts"
)
API_VERSION = "2026-03-10"
USER_AGENT = "content-radar-cloud/1.0"
MAX_ARCHIVE_MEMBER_BYTES = 8 * 1024 * 1024


class ArtifactError(ValueError):
    """A cloud artifact could not be proven safe and complete."""


def artifact_name(report_date: str, logical_slot: str) -> str:
    return f"{ARTIFACT_PREFIX}-{report_date}-{logical_slot}"


def select_latest_artifacts(
    artifacts: List[dict],
    *,
    report_date: str,
    logical_slots: Iterable[str],
) -> Dict[str, dict]:
    if not isinstance(artifacts, list):
        raise ArtifactError("artifact_list_contract")

    selected: Dict[str, dict] = {}
    for slot in logical_slots:
        expected = artifact_name(report_date, slot)
        candidates = []
        for value in artifacts:
            if not isinstance(value, dict):
                raise ArtifactError("artifact_contract")
            if value.get("name") != expected or value.get("expired") is not False:
                continue
            if (
                type(value.get("id")) is not int
                or value["id"] <= 0
                or not isinstance(value.get("created_at"), str)
                or not value["created_at"]
            ):
                raise ArtifactError("artifact_contract")
            candidates.append(value)
        if candidates:
            selected[slot] = max(
                candidates,
                key=lambda value: value["created_at"],
            )
    return selected


def safe_extract_json(
    zip_bytes: bytes,
    *,
    report_date: Optional[str] = None,
    logical_slot: Optional[str] = None,
) -> dict:
    if not isinstance(zip_bytes, bytes):
        raise ArtifactError("archive_contract")
    try:
        with ZipFile(io.BytesIO(zip_bytes)) as archive:
            members = archive.infolist()
            for member in members:
                path = PurePosixPath(member.filename)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or "\\" in member.filename
                ):
                    raise ArtifactError("unsafe_archive")
                if member.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    raise ArtifactError("archive_too_large")
            files = [member for member in members if not member.is_dir()]
            if len(files) != 1 or PurePosixPath(files[0].filename).suffix != ".json":
                raise ArtifactError("archive_contract")
            raw = archive.read(files[0])
    except ArtifactError:
        raise
    except (BadZipFile, KeyError, OSError) as error:
        raise ArtifactError("archive_contract") from error

    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArtifactError("snapshot_json") from error
    if not isinstance(value, dict):
        raise ArtifactError("snapshot_contract")
    if (
        not isinstance(value.get("report_date"), str)
        or not isinstance(value.get("logical_slot"), str)
    ):
        raise ArtifactError("snapshot_contract")
    if report_date is not None and value["report_date"] != report_date:
        raise ArtifactError("report_date_mismatch")
    if logical_slot is not None and value["logical_slot"] != logical_slot:
        raise ArtifactError("logical_slot_mismatch")
    return value


def _headers(token: str) -> Dict[str, str]:
    if not isinstance(token, str) or not token:
        raise ArtifactError("github_token_missing")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": USER_AGENT,
    }


def _default_request(request: Request) -> bytes:
    with urlopen(request, timeout=30) as response:
        return response.read()


def _get(
    url: str,
    token: str,
    request: Callable[[Request], bytes],
) -> bytes:
    value = Request(
        url,
        headers=_headers(token),
        method="GET",
    )
    try:
        response = request(value)
        if isinstance(response, bytes):
            return response
        return response.read()
    except (HTTPError, URLError, OSError, TimeoutError):
        raise ArtifactError("github_request_failed") from None


def download_latest_snapshots(
    token: str,
    *,
    report_date: str,
    logical_slots: Iterable[str],
    request: Callable[[Request], bytes] = _default_request,
) -> dict:
    slots = tuple(logical_slots)
    try:
        listing = json.loads(
            _get(
                f"{API_ROOT}?per_page=100",
                token,
                request,
            ).decode("utf-8")
        )
    except ArtifactError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArtifactError("github_response_contract") from error
    if not isinstance(listing, dict) or not isinstance(
        listing.get("artifacts"),
        list,
    ):
        raise ArtifactError("github_response_contract")

    selected = select_latest_artifacts(
        listing["artifacts"],
        report_date=report_date,
        logical_slots=slots,
    )
    snapshots = {}
    for slot in slots:
        artifact = selected.get(slot)
        if artifact is None:
            continue
        archive = _get(
            f"{API_ROOT}/{artifact['id']}/zip",
            token,
            request,
        )
        snapshots[slot] = safe_extract_json(
            archive,
            report_date=report_date,
            logical_slot=slot,
        )
    return {
        "snapshots": snapshots,
        "missing_slots": [
            slot for slot in slots if slot not in snapshots
        ],
    }
