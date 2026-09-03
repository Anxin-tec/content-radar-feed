from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Optional, Sequence
from zoneinfo import ZoneInfo

from .aihot import AihotIncomplete, fetch_aihot
from .privacy import PublicBoundaryError, validate_public_report
from .markdown_report import render_report
from .report import ReportError, build_report as build_daily_report
from .trendradar import (
    LOGICAL_SLOTS,
    TrendRadarIncomplete,
    extract_snapshot,
    run_trendradar,
)


TIMEZONE = ZoneInfo("Asia/Shanghai")
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schema"
    / "public-report.schema.json"
)
MAXIMUM_FIXTURE_MARKERS = (
    "A001-Q7X9",
    "A075-K4M8",
    "A150-P2V6",
    "N001-R8C3",
    "N050-H5T1",
    "N100-Z9D4",
)


def _report_date(value: str) -> str:
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError
        return value
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("invalid report date") from None


def _positive_integer(value: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("must be a positive integer") from None
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _encode_json(value: dict) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=str(path.parent),
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(path))
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("json_contract")
    return value


def _validate(report: dict, max_bytes: int) -> None:
    validate_public_report(
        report,
        SCHEMA_PATH,
        max_bytes=max_bytes,
        expected_date=report.get("report_date"),
    )


def _publish(report: dict, site_dir: Path, max_bytes: int) -> None:
    _validate(report, max_bytes)
    body = _encode_json(report)
    dated = site_dir / "reports" / f'{report["report_date"]}.json'
    latest = site_dir / "latest.json"
    _atomic_write(dated, body)
    _atomic_write(latest, body)
    markdown = render_report(report).encode("utf-8")
    _atomic_write(dated.with_suffix(".md"), markdown)
    _atomic_write(site_dir / "latest.md", markdown)


def _fixture_aihot_item(index: int, marker: str) -> dict:
    suffix = f" {marker}" if marker else ""
    return {
        "id": f"fixture-a-{index:03d}",
        "title": f"AI HOT capacity item {index:03d}{suffix}",
        "title_en": f"AI HOT capacity item {index:03d}{suffix}",
        "permalink": (
            f"https://aihot.example.com/items/fixture-a-{index:03d}"
        ),
        "url": f"https://news.example.com/ai/{index:03d}",
        "source": "AI HOT fixture",
        "published_at": "2026-07-24T00:00:00Z",
        "summary": f"Capacity validation item {index:03d}{suffix}",
        "category": "fixture",
        "score": index,
        "selected": True,
        "attribution": {
            "source": "AI HOT fixture",
            "canonical": (
                "https://aihot.example.com/items/"
                f"fixture-a-{index:03d}"
            ),
        },
    }


def _fixture_trend_item(index: int, marker: str) -> dict:
    suffix = f" {marker}" if marker else ""
    return {
        "id": index,
        "title": f"AI trend capacity item {index:03d}{suffix}",
        "platform_id": "fixture",
        "platform": "Capacity fixture",
        "rank": index,
        "url": f"https://trend.example.com/items/{index:03d}",
        "first_crawl_time": "2026-07-24T00:30:00+08:00",
        "last_crawl_time": "2026-07-24T06:30:00+08:00",
        "crawl_count": 1,
    }


def make_fixture(report_date: str, size: str) -> dict:
    a_count, n_count = (3, 3) if size == "small" else (150, 100)
    a_markers = {}
    n_markers = {}
    if size == "maximum":
        a_markers = {
            1: MAXIMUM_FIXTURE_MARKERS[0],
            75: MAXIMUM_FIXTURE_MARKERS[1],
            150: MAXIMUM_FIXTURE_MARKERS[2],
        }
        n_markers = {
            1: MAXIMUM_FIXTURE_MARKERS[3],
            50: MAXIMUM_FIXTURE_MARKERS[4],
            100: MAXIMUM_FIXTURE_MARKERS[5],
        }
    aihot_items = [
        _fixture_aihot_item(index, a_markers.get(index, ""))
        for index in range(1, a_count + 1)
    ]
    trend_items = [
        _fixture_trend_item(index, n_markers.get(index, ""))
        for index in range(1, n_count + 1)
    ]
    snapshots = []
    for slot, collected_at in (
        ("0030", f"{report_date}T00:30:00+08:00"),
        ("0400", f"{report_date}T04:00:00+08:00"),
        ("0630", f"{report_date}T06:30:00+08:00"),
    ):
        snapshots.append(
            {
                "schema_version": 1,
                "logical_slot": slot,
                "collected_at": collected_at,
                "source_status": "live",
                "crawl_time": collected_at,
                "row_count": len(trend_items),
                "platform_count": 1,
                "failed_platforms": [],
                "items": trend_items,
            }
        )
    generated_at = f"{report_date}T07:00:00+08:00"
    prior_date = (
        date.fromisoformat(report_date) - timedelta(days=1)
    ).isoformat()
    return build_daily_report(
        report_date=report_date,
        generated_at=generated_at,
        window_start=f"{prior_date}T07:00:00+08:00",
        window_end=generated_at,
        run_id=f"fixture-{size}-{report_date}",
        aihot_result={
            "status": "live",
            "api_version": "fixture-1",
            "page_count": (a_count + 99) // 100,
            "items": aihot_items,
        },
        snapshots=snapshots,
    )


def _collect_trendradar(arguments: argparse.Namespace) -> None:
    now = datetime.now(TIMEZONE)
    database = run_trendradar(arguments.trendradar_root, now=now)
    snapshot = extract_snapshot(
        database,
        logical_slot=arguments.logical_slot,
        collected_at=now.isoformat(timespec="seconds"),
    )
    _atomic_write(arguments.output, _encode_json(snapshot))


def _build_report(arguments: argparse.Namespace) -> None:
    if not arguments.snapshot:
        raise ReportError("snapshot_contract")
    snapshots = [_load_json(path) for path in arguments.snapshot]
    now = datetime.now(TIMEZONE)
    try:
        aihot_result = fetch_aihot(now=now)
    except AihotIncomplete:
        aihot_result = {
            "status": "incomplete",
            "api_version": None,
            "page_count": 0,
            "items": [],
        }
    generated_at = now.isoformat(timespec="seconds")
    report = build_daily_report(
        report_date=arguments.report_date,
        generated_at=generated_at,
        window_start=(now - timedelta(hours=24)).isoformat(
            timespec="seconds"
        ),
        window_end=generated_at,
        run_id=now.strftime("%Y%m%dT%H%M%S%z"),
        aihot_result=aihot_result,
        snapshots=snapshots,
    )
    _publish(report, arguments.site_dir, arguments.max_bytes)


def _validate_report(arguments: argparse.Namespace) -> None:
    _validate(_load_json(arguments.input), arguments.max_bytes)


def _build_fixture(arguments: argparse.Namespace) -> None:
    report = make_fixture(arguments.report_date, arguments.size)
    _publish(report, arguments.site_dir, arguments.max_bytes)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="content-radar-feed")
    commands = parser.add_subparsers(dest="command", required=True)

    collect = commands.add_parser("collect-trendradar")
    collect.add_argument(
        "--trendradar-root",
        type=Path,
        required=True,
    )
    collect.add_argument(
        "--logical-slot",
        choices=sorted(LOGICAL_SLOTS),
        required=True,
    )
    collect.add_argument("--output", type=Path, required=True)
    collect.set_defaults(handler=_collect_trendradar)

    build = commands.add_parser("build-report")
    build.add_argument(
        "--report-date",
        type=_report_date,
        required=True,
    )
    build.add_argument(
        "--snapshot",
        type=Path,
        action="append",
        default=[],
    )
    build.add_argument("--site-dir", type=Path, required=True)
    build.add_argument(
        "--max-bytes",
        type=_positive_integer,
        required=True,
    )
    build.set_defaults(handler=_build_report)

    validate = commands.add_parser("validate-report")
    validate.add_argument("--input", type=Path, required=True)
    validate.add_argument(
        "--max-bytes",
        type=_positive_integer,
        required=True,
    )
    validate.set_defaults(handler=_validate_report)

    fixture = commands.add_parser("build-fixture")
    fixture.add_argument(
        "--report-date",
        type=_report_date,
        required=True,
    )
    fixture.add_argument(
        "--size",
        choices=("small", "maximum"),
        required=True,
    )
    fixture.add_argument("--site-dir", type=Path, required=True)
    fixture.add_argument(
        "--max-bytes",
        type=_positive_integer,
        required=True,
    )
    fixture.set_defaults(handler=_build_fixture)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        arguments.handler(arguments)
    except (
        AihotIncomplete,
        json.JSONDecodeError,
        OSError,
        PublicBoundaryError,
        ReportError,
        TrendRadarIncomplete,
        TypeError,
        ValueError,
    ) as error:
        print(str(error) or "command_failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
