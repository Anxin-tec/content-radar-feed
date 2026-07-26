from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime
import importlib
import os
from pathlib import Path
import sqlite3
import stat
import sys
from typing import Optional
from zoneinfo import ZoneInfo


LOGICAL_SLOTS = {"0030", "0400", "0630"}
TIMEZONE = ZoneInfo("Asia/Shanghai")

_RECORD_KEYS = {"id", "crawl_time", "total_items"}
_PLATFORM_KEYS = {"id", "is_active"}
_STATUS_KEYS = {"crawl_record_id", "platform_id", "status"}
_ROW_KEYS = {
    "id",
    "title",
    "platform_id",
    "platform",
    "rank",
    "url",
    "first_crawl_time",
    "last_crawl_time",
    "crawl_count",
}


class TrendRadarIncomplete(ValueError):
    """The local TrendRadar database cannot prove a complete snapshot."""


def _is_trendradar_module(name: str) -> bool:
    return name == "trendradar" or name.startswith("trendradar.")


def _collector_date(now: Optional[datetime]) -> str:
    current = datetime.now(TIMEZONE) if now is None else now
    if (
        not isinstance(current, datetime)
        or current.tzinfo is None
        or current.utcoffset() is None
    ):
        raise TrendRadarIncomplete("now_contract")
    try:
        return current.astimezone(TIMEZONE).strftime("%Y-%m-%d")
    except (OSError, OverflowError, ValueError):
        raise TrendRadarIncomplete("now_contract") from None


def _collector_root(value: Path) -> Path:
    try:
        root = Path(value).resolve(strict=True)
        if not root.is_dir():
            raise OSError
        return root
    except (OSError, TypeError, ValueError):
        raise TrendRadarIncomplete("root_missing") from None


def run_trendradar(
    trendradar_root: Path,
    *,
    now: Optional[datetime] = None,
) -> Path:
    """Run only the pinned TrendRadar news collector and return its database."""

    report_date = _collector_date(now)
    root = _collector_root(trendradar_root)
    root_text = str(root)
    previous_cwd = Path.cwd()
    previous_path = list(sys.path)
    previous_modules = {
        name: module
        for name, module in sys.modules.items()
        if _is_trendradar_module(name)
    }
    analyzer = None
    context = None
    database = None
    failure = None

    try:
        os.chdir(root)
        sys.path[:] = [
            root_text,
            *[entry for entry in previous_path if entry != root_text],
        ]
        for name in list(sys.modules):
            if _is_trendradar_module(name):
                del sys.modules[name]
        importlib.invalidate_caches()

        try:
            with redirect_stdout(sys.stderr):
                module = importlib.import_module("trendradar.__main__")
                load_config = getattr(module, "load_config")
                analyzer_class = getattr(module, "NewsAnalyzer")
                config = load_config()
                analyzer = analyzer_class(config=config)
                context = getattr(analyzer, "ctx")
                if context is None:
                    raise AttributeError
                analyzer._initialize_and_check_config()
                analyzer._crawl_data()
        except BaseException:
            failure = TrendRadarIncomplete("collector_failed")

        if failure is None:
            database = (
                root / "output" / "news" / f"{report_date}.db"
            )
            try:
                if not database.is_file():
                    raise OSError
            except OSError:
                failure = TrendRadarIncomplete("database_missing")
    finally:
        if analyzer is not None and context is not None:
            try:
                with redirect_stdout(sys.stderr):
                    context.cleanup()
            except BaseException:
                if failure is None:
                    failure = TrendRadarIncomplete("cleanup_failed")

        for name in list(sys.modules):
            if _is_trendradar_module(name):
                del sys.modules[name]
        sys.modules.update(previous_modules)
        sys.path[:] = previous_path
        try:
            os.chdir(previous_cwd)
        except OSError:
            if failure is None:
                failure = TrendRadarIncomplete("collector_failed")

    if failure is not None:
        raise failure from None
    if database is None:
        raise TrendRadarIncomplete("database_missing")
    return database


def _normalize_collected_at(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrendRadarIncomplete("collected_at_contract")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError
        return parsed.astimezone(TIMEZONE).isoformat(timespec="seconds")
    except (OSError, OverflowError, ValueError):
        raise TrendRadarIncomplete("collected_at_contract") from None


def _database_uri(database: Path) -> str:
    try:
        resolved = Path(database).resolve(strict=True)
        if not stat.S_ISREG(resolved.stat().st_mode):
            raise OSError
        return resolved.as_uri() + "?mode=ro"
    except (OSError, TypeError, ValueError):
        raise TrendRadarIncomplete("database_missing") from None


def _read_snapshot(
    database_uri: str,
) -> tuple[
    sqlite3.Row | None,
    list[sqlite3.Row],
    list[sqlite3.Row],
    list[sqlite3.Row],
]:
    connection = None
    failure = None
    record = None
    platforms = []
    statuses = []
    rows = []
    try:
        connection = sqlite3.connect(database_uri, uri=True)
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN")
        record = connection.execute(
            """
            SELECT id, crawl_time, total_items
            FROM crawl_records
            ORDER BY crawl_time DESC, id DESC
            LIMIT 1
            """
        ).fetchone()
        if record is not None:
            platforms = connection.execute(
                """
                SELECT id, is_active
                FROM platforms
                ORDER BY id
                """
            ).fetchall()
            statuses = connection.execute(
                """
                SELECT crawl_record_id, platform_id, status
                FROM crawl_source_status
                WHERE crawl_record_id = ?
                ORDER BY platform_id
                """,
                (record["id"],),
            ).fetchall()
            rows = connection.execute(
                """
                SELECT
                    n.id,
                    n.title,
                    n.platform_id,
                    p.name AS platform,
                    n.rank,
                    n.url,
                    n.first_crawl_time,
                    n.last_crawl_time,
                    n.crawl_count
                FROM news_items AS n
                LEFT JOIN platforms AS p ON p.id = n.platform_id
                WHERE n.last_crawl_time = ?
                ORDER BY n.platform_id, n.rank, n.id
                """,
                (record["crawl_time"],),
            ).fetchall()
    except sqlite3.Error:
        failure = TrendRadarIncomplete("database_contract")
    finally:
        if connection is not None:
            try:
                connection.rollback()
            except sqlite3.Error:
                if failure is None:
                    failure = TrendRadarIncomplete("database_contract")
            try:
                connection.close()
            except sqlite3.Error:
                if failure is None:
                    failure = TrendRadarIncomplete("database_contract")

    if failure is not None:
        raise failure from None
    return record, platforms, statuses, rows


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_record(record: sqlite3.Row | None) -> dict:
    if record is None:
        raise TrendRadarIncomplete("crawl_record_missing")
    value = dict(record)
    if (
        set(value) != _RECORD_KEYS
        or type(value["id"]) is not int
        or value["id"] <= 0
        or not _is_nonempty_string(value["crawl_time"])
        or type(value["total_items"]) is not int
        or value["total_items"] < 0
    ):
        raise TrendRadarIncomplete("database_contract")
    return value


def _validate_platforms(rows: list[sqlite3.Row]) -> set[str]:
    platform_ids = set()
    active_platforms = set()
    for row in rows:
        value = dict(row)
        if (
            set(value) != _PLATFORM_KEYS
            or not _is_nonempty_string(value["id"])
            or type(value["is_active"]) is not int
            or value["is_active"] not in {0, 1}
            or value["id"] in platform_ids
        ):
            raise TrendRadarIncomplete("database_contract")
        platform_ids.add(value["id"])
        if value["is_active"] == 1:
            active_platforms.add(value["id"])
    return active_platforms


def _validate_statuses(
    rows: list[sqlite3.Row],
    *,
    record_id: int,
) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for row in rows:
        value = dict(row)
        if (
            set(value) != _STATUS_KEYS
            or type(value["crawl_record_id"]) is not int
            or value["crawl_record_id"] != record_id
            or not _is_nonempty_string(value["platform_id"])
            or value["status"] not in {"success", "failed"}
            or value["platform_id"] in statuses
        ):
            raise TrendRadarIncomplete("status_contract")
        statuses[value["platform_id"]] = value["status"]
    return statuses


def _validate_items(rows: list[sqlite3.Row]) -> list[dict]:
    items = []
    for row in rows:
        value = dict(row)
        if (
            set(value) != _ROW_KEYS
            or any(
                type(value[field]) is not int or value[field] <= 0
                for field in ("id", "rank", "crawl_count")
            )
            or any(
                not _is_nonempty_string(value[field])
                for field in (
                    "title",
                    "platform_id",
                    "platform",
                    "first_crawl_time",
                    "last_crawl_time",
                )
            )
            or (
                value["url"] is not None
                and not isinstance(value["url"], str)
            )
        ):
            raise TrendRadarIncomplete("item_contract")
        items.append(value)
    return items


def extract_snapshot(
    database: Path,
    *,
    logical_slot: str,
    collected_at: str,
) -> dict:
    if not isinstance(logical_slot, str) or logical_slot not in LOGICAL_SLOTS:
        raise TrendRadarIncomplete("logical_slot")
    normalized_collected_at = _normalize_collected_at(collected_at)
    database_uri = _database_uri(database)

    (
        raw_record,
        raw_platforms,
        raw_statuses,
        raw_rows,
    ) = _read_snapshot(database_uri)
    record = _validate_record(raw_record)
    active_platforms = _validate_platforms(raw_platforms)
    statuses = _validate_statuses(
        raw_statuses,
        record_id=record["id"],
    )
    items = _validate_items(raw_rows)

    if record["total_items"] != len(items):
        raise TrendRadarIncomplete("row_count_mismatch")
    item_platforms = {item["platform_id"] for item in items}
    if (
        not items
        or not active_platforms
        or not active_platforms.issubset(statuses)
        or not item_platforms.issubset(active_platforms)
        or not item_platforms.issubset(statuses)
    ):
        raise TrendRadarIncomplete("status_contract")

    failed_platforms = sorted(
        platform_id
        for platform_id, status_value in statuses.items()
        if status_value == "failed"
    )
    return {
        "schema_version": 1,
        "logical_slot": logical_slot,
        "collected_at": normalized_collected_at,
        "source_status": "degraded" if failed_platforms else "live",
        "crawl_time": record["crawl_time"],
        "row_count": len(items),
        "platform_count": len(item_platforms),
        "failed_platforms": failed_platforms,
        "items": items,
    }
