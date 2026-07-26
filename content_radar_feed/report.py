from __future__ import annotations

import hashlib

from .relevance import is_ai_related


LOGICAL_SLOTS = ("0030", "0400", "0630")
SUCCESSFUL_AIHOT_STATUSES = {"live", "not_modified"}
AIHOT_ITEM_KEYS = (
    "id",
    "title",
    "title_en",
    "permalink",
    "url",
    "source",
    "published_at",
    "summary",
    "category",
    "score",
    "selected",
    "attribution",
)


class ReportError(ValueError):
    """The inputs cannot prove a safe, complete public report."""


def stable_n_id(item: dict) -> str:
    identity = item.get("url") or item["title"]
    raw = f'{item["platform_id"]}\0{identity}'.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def _public_aihot_item(value: object) -> dict:
    if not isinstance(value, dict):
        raise ReportError("aihot_contract")
    if (
        not isinstance(value.get("id"), str)
        or not value["id"].strip()
    ):
        raise ReportError("aihot_contract")
    try:
        return {key: value[key] for key in AIHOT_ITEM_KEYS}
    except KeyError:
        raise ReportError("aihot_contract") from None


def _snapshot_values(snapshots: object) -> dict[str, dict]:
    if not isinstance(snapshots, list):
        raise ReportError("snapshot_contract")
    selected: dict[str, dict] = {}
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            raise ReportError("snapshot_contract")
        slot = snapshot.get("logical_slot")
        if slot not in LOGICAL_SLOTS:
            raise ReportError("logical_slot")
        collected_at = snapshot.get("collected_at")
        if (
            not isinstance(collected_at, str)
            or not collected_at.strip()
            or snapshot.get("source_status") not in {"live", "degraded"}
            or not isinstance(snapshot.get("failed_platforms"), list)
            or not isinstance(snapshot.get("items"), list)
        ):
            raise ReportError("snapshot_contract")
        current = selected.get(slot)
        if (
            current is None
            or collected_at > current["collected_at"]
        ):
            selected[slot] = snapshot
    return selected


def _trend_item(value: object) -> dict:
    if not isinstance(value, dict):
        raise ReportError("trendradar_contract")
    required = (
        "title",
        "platform_id",
        "platform",
        "rank",
        "url",
    )
    if any(key not in value for key in required):
        raise ReportError("trendradar_contract")
    if (
        any(
            not isinstance(value[key], str) or not value[key].strip()
            for key in ("title", "platform_id", "platform")
        )
        or type(value["rank"]) is not int
        or value["rank"] <= 0
        or (
            value["url"] is not None
            and not isinstance(value["url"], str)
        )
    ):
        raise ReportError("trendradar_contract")
    return value


def _build_report(
    *,
    report_date: str,
    generated_at: str,
    window_start: str,
    window_end: str,
    run_id: str,
    aihot_result: dict,
    snapshots: list[dict],
) -> dict:
    if not isinstance(aihot_result, dict):
        raise ReportError("aihot_contract")
    aihot_status = aihot_result.get("status")
    if aihot_status not in {
        "live",
        "not_modified",
        "failed",
        "incomplete",
    }:
        raise ReportError("aihot_status")
    raw_aihot_values = aihot_result.get("items", [])
    if not isinstance(raw_aihot_values, list):
        raise ReportError("aihot_contract")
    if aihot_status in SUCCESSFUL_AIHOT_STATUSES:
        aihot_values = [
            _public_aihot_item(value)
            for value in raw_aihot_values
        ]
    else:
        aihot_values = []
    aihot_ids = [value["id"] for value in aihot_values]
    if len(aihot_ids) != len(set(aihot_ids)):
        raise ReportError("duplicate_aihot_id")
    aihot_items = [
        {"ref": f"A{index}", **value}
        for index, value in enumerate(aihot_values, start=1)
    ]

    selected = _snapshot_values(snapshots)
    groups: dict[str, list[tuple[str, dict]]] = {}
    platforms: set[str] = set()
    failed_platforms: set[str] = set()
    for slot in LOGICAL_SLOTS:
        snapshot = selected.get(slot)
        if snapshot is None:
            continue
        for failed_platform in snapshot["failed_platforms"]:
            if (
                not isinstance(failed_platform, str)
                or not failed_platform.strip()
            ):
                raise ReportError("snapshot_contract")
            failed_platforms.add(failed_platform)
        for raw_value in snapshot["items"]:
            value = _trend_item(raw_value)
            platforms.add(value["platform_id"])
            groups.setdefault(stable_n_id(value), []).append(
                (snapshot["collected_at"], value)
            )

    matched = []
    for source_id, occurrences in groups.items():
        ordered = sorted(
            occurrences,
            key=lambda pair: pair[0],
        )
        first_time, first = ordered[0]
        last_time, latest = ordered[-1]
        if not is_ai_related(latest["title"]):
            continue
        matched.append(
            {
                "id": source_id,
                "title": latest["title"],
                "platform_id": latest["platform_id"],
                "platform": latest["platform"],
                "rank": latest["rank"],
                "url": latest["url"],
                "first_crawl_time": first_time,
                "last_crawl_time": last_time,
                "crawl_count": len(
                    {pair[0] for pair in ordered}
                ),
                "rank_change": first["rank"] - latest["rank"],
            }
        )

    matched.sort(
        key=lambda value: (
            value["rank"],
            value["platform_id"],
            value["title"],
            value["id"],
        )
    )
    trendradar_items = [
        {"ref": f"N{index}", **value}
        for index, value in enumerate(matched, start=1)
    ]

    if not selected:
        trend_status = "failed"
    elif (
        set(selected) == set(LOGICAL_SLOTS)
        and not failed_platforms
        and all(
            value["source_status"] == "live"
            for value in selected.values()
        )
    ):
        trend_status = "live"
    else:
        trend_status = "degraded"

    warnings = []
    if aihot_status not in SUCCESSFUL_AIHOT_STATUSES:
        warnings.append("aihot_source_incomplete")
    if trend_status != "live":
        warnings.append("trendradar_incomplete_slots")

    return {
        "schema_version": 1,
        "run_id": run_id,
        "report_date": report_date,
        "timezone": "Asia/Shanghai",
        "generated_at": generated_at,
        "window_start": window_start,
        "window_end": window_end,
        "source_status": {
            "aihot": {
                "status": aihot_status,
                "api_version": aihot_result.get("api_version"),
                "page_count": aihot_result.get("page_count", 0),
            },
            "trendradar": {
                "status": trend_status,
                "snapshot_count": len(selected),
                "platform_count": len(platforms),
            },
        },
        "counts": {
            "aihot_upstream": len(aihot_values),
            "aihot_published": len(aihot_items),
            "trendradar_raw": len(groups),
            "trendradar_matched": len(matched),
            "trendradar_published": len(trendradar_items),
        },
        "aihot_items": aihot_items,
        "trendradar_items": trendradar_items,
        "warnings": sorted(warnings),
    }


def build_report(
    *,
    report_date: str,
    generated_at: str,
    window_start: str,
    window_end: str,
    run_id: str,
    aihot_result: dict,
    snapshots: list[dict],
) -> dict:
    try:
        return _build_report(
            report_date=report_date,
            generated_at=generated_at,
            window_start=window_start,
            window_end=window_end,
            run_id=run_id,
            aihot_result=aihot_result,
            snapshots=snapshots,
        )
    except ReportError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError):
        raise ReportError("report_contract") from None
