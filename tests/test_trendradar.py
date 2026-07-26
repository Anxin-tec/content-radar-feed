from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import io
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import content_radar_feed.trendradar as trendradar
from content_radar_feed.trendradar import (
    TrendRadarIncomplete,
    extract_snapshot,
    run_trendradar,
)


SCHEMA = """
CREATE TABLE platforms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    updated_at TIMESTAMP
);
CREATE TABLE news_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    rank INTEGER NOT NULL,
    url TEXT DEFAULT '',
    mobile_url TEXT DEFAULT '',
    first_crawl_time TEXT NOT NULL,
    last_crawl_time TEXT NOT NULL,
    crawl_count INTEGER DEFAULT 1
);
CREATE TABLE crawl_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_time TEXT NOT NULL UNIQUE,
    total_items INTEGER DEFAULT 0
);
CREATE TABLE crawl_source_status (
    crawl_record_id INTEGER NOT NULL,
    platform_id TEXT NOT NULL,
    status TEXT NOT NULL,
    PRIMARY KEY (crawl_record_id, platform_id)
);
"""

OLD_CRAWL = "2026-07-23 23:30:00"
LATEST_CRAWL = "2026-07-24 00:30:00"
COLLECTED_AT = "2026-07-24T00:31:00+08:00"
TOP_LEVEL_KEYS = {
    "schema_version",
    "logical_slot",
    "collected_at",
    "source_status",
    "crawl_time",
    "row_count",
    "platform_count",
    "failed_platforms",
    "items",
}
ITEM_KEYS = {
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


class AfterRecordFetchCursor:
    def __init__(self, cursor, after_fetch) -> None:
        self.cursor = cursor
        self.after_fetch = after_fetch
        self.triggered = False

    def fetchone(self):
        row = self.cursor.fetchone()
        if not self.triggered:
            self.triggered = True
            self.after_fetch()
        return row


class AfterRecordFetchConnection:
    def __init__(self, connection, after_fetch) -> None:
        self.connection = connection
        self.after_fetch = after_fetch

    @property
    def row_factory(self):
        return self.connection.row_factory

    @row_factory.setter
    def row_factory(self, value) -> None:
        self.connection.row_factory = value

    def execute(self, statement, parameters=()):
        cursor = self.connection.execute(statement, parameters)
        if "FROM crawl_records" in statement:
            return AfterRecordFetchCursor(cursor, self.after_fetch)
        return cursor

    def rollback(self) -> None:
        self.connection.rollback()

    def close(self) -> None:
        self.connection.close()


class FailingConnection:
    def __init__(self, fail_stage: str) -> None:
        self.fail_stage = fail_stage
        self.statements = []
        self.closed = False
        self.rolled_back = False
        self.row_factory = None

    def execute(self, statement, parameters=()):
        normalized = statement.strip()
        self.statements.append(normalized)
        if normalized == "BEGIN" and self.fail_stage == "begin":
            raise sqlite3.OperationalError(
                "private begin failure /secret/database.db"
            )
        if normalized.startswith("SELECT") and self.fail_stage == "read":
            raise sqlite3.OperationalError(
                "private SELECT failure /secret/database.db"
            )
        if normalized != "BEGIN":
            raise AssertionError("BEGIN must precede every read")
        return None

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def create_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)


def add_platforms(
    connection: sqlite3.Connection,
    platform_ids: list[str],
) -> None:
    connection.executemany(
        "INSERT INTO platforms (id, name) VALUES (?, ?)",
        [
            (platform_id, f"Platform {platform_id}")
            for platform_id in platform_ids
        ],
    )


def add_crawl(
    connection: sqlite3.Connection,
    *,
    crawl_time: str,
    count: int,
    platform_ids: list[str],
    statuses: dict[str, str] | None = None,
) -> int:
    cursor = connection.execute(
        "INSERT INTO crawl_records (crawl_time, total_items) VALUES (?, ?)",
        (crawl_time, count),
    )
    record_id = cursor.lastrowid
    assert record_id is not None

    rows = []
    for index in range(count):
        platform_id = platform_ids[(count - index - 1) % len(platform_ids)]
        rows.append(
            (
                f"{crawl_time} item {index + 1}",
                platform_id,
                (count - index - 1) // len(platform_ids) + 1,
                f"https://example.com/{record_id}/{index + 1}",
                "",
                crawl_time,
                crawl_time,
                index + 1,
            )
        )
    connection.executemany(
        """
        INSERT INTO news_items (
            title,
            platform_id,
            rank,
            url,
            mobile_url,
            first_crawl_time,
            last_crawl_time,
            crawl_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    if statuses is None:
        statuses = {
            platform_id: "success"
            for platform_id in platform_ids
        }
    connection.executemany(
        """
        INSERT INTO crawl_source_status (
            crawl_record_id,
            platform_id,
            status
        )
        VALUES (?, ?, ?)
        """,
        [
            (record_id, platform_id, status)
            for platform_id, status in statuses.items()
        ],
    )
    return record_id


class TrendRadarSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.database = Path(self.temporary_directory.name) / "trendradar.db"

    def extract(self, **overrides) -> dict:
        arguments = {
            "database": self.database,
            "logical_slot": "0030",
            "collected_at": COLLECTED_AT,
        }
        arguments.update(overrides)
        return extract_snapshot(**arguments)

    def assert_incomplete(self, code: str, **overrides) -> None:
        with self.assertRaises(TrendRadarIncomplete) as raised:
            self.extract(**overrides)
        self.assertEqual(str(raised.exception), code)

    def seed_complete_snapshot(
        self,
        *,
        latest_count: int = 30,
        statuses: dict[str, str] | None = None,
    ) -> None:
        create_database(self.database)
        latest_platforms = [f"p{number}" for number in range(1, 7)]
        with sqlite3.connect(self.database) as connection:
            add_platforms(
                connection,
                ["old-platform", *latest_platforms, "z-extra"],
            )
            connection.execute(
                """
                UPDATE platforms
                SET is_active = 0
                WHERE id IN ('old-platform', 'z-extra')
                """
            )
            add_crawl(
                connection,
                crawl_time=OLD_CRAWL,
                count=5,
                platform_ids=["old-platform"],
            )
            add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=latest_count,
                platform_ids=latest_platforms,
                statuses=statuses,
            )

    def test_exports_only_the_complete_latest_logical_snapshot(self) -> None:
        self.seed_complete_snapshot()

        result = self.extract()

        self.assertEqual(set(result), TOP_LEVEL_KEYS)
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["logical_slot"], "0030")
        self.assertEqual(result["collected_at"], COLLECTED_AT)
        self.assertEqual(result["source_status"], "live")
        self.assertEqual(result["crawl_time"], LATEST_CRAWL)
        self.assertEqual(result["row_count"], 30)
        self.assertEqual(len(result["items"]), 30)
        self.assertEqual(result["platform_count"], 6)
        self.assertEqual(result["failed_platforms"], [])
        self.assertNotIn("db_path", result)
        self.assertNotIn(str(self.database.resolve()), repr(result))

        items = result["items"]
        self.assertTrue(all(set(item) == ITEM_KEYS for item in items))
        self.assertTrue(
            all(item["last_crawl_time"] == LATEST_CRAWL for item in items)
        )
        self.assertFalse(
            any(item["platform_id"] == "old-platform" for item in items)
        )
        ordering = [
            (item["platform_id"], item["rank"], item["id"])
            for item in items
        ]
        self.assertEqual(ordering, sorted(ordering))

    def test_exports_all_130_rows_without_a_query_limit(self) -> None:
        self.seed_complete_snapshot(latest_count=130)

        result = self.extract()

        self.assertEqual(result["row_count"], 130)
        self.assertEqual(len(result["items"]), 130)
        self.assertEqual(
            len({item["id"] for item in result["items"]}),
            130,
        )

    def test_preserves_null_and_empty_urls_in_a_complete_snapshot(
        self,
    ) -> None:
        self.seed_complete_snapshot()
        with sqlite3.connect(self.database) as connection:
            latest_ids = [
                row[0]
                for row in connection.execute(
                    """
                    SELECT id
                    FROM news_items
                    WHERE last_crawl_time = ?
                    ORDER BY id
                    LIMIT 2
                    """,
                    (LATEST_CRAWL,),
                )
            ]
            connection.execute(
                "UPDATE news_items SET url = NULL WHERE id = ?",
                (latest_ids[0],),
            )
            connection.execute(
                "UPDATE news_items SET url = '' WHERE id = ?",
                (latest_ids[1],),
            )

        result = self.extract()

        items_by_id = {
            item["id"]: item
            for item in result["items"]
        }
        self.assertEqual(result["row_count"], 30)
        self.assertEqual(len(result["items"]), 30)
        self.assertIsNone(items_by_id[latest_ids[0]]["url"])
        self.assertEqual(items_by_id[latest_ids[1]]["url"], "")

    def test_rejects_record_count_that_does_not_match_exported_rows(
        self,
    ) -> None:
        self.seed_complete_snapshot()
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """
                UPDATE crawl_records
                SET total_items = 31
                WHERE crawl_time = ?
                """,
                (LATEST_CRAWL,),
            )

        self.assert_incomplete("row_count_mismatch")

    def test_reports_failed_platforms_as_a_sorted_degraded_snapshot(
        self,
    ) -> None:
        self.seed_complete_snapshot(
            statuses={
                "p1": "success",
                "p2": "failed",
                "p3": "success",
                "p4": "failed",
                "p5": "success",
                "p6": "success",
                "z-extra": "failed",
            }
        )

        result = self.extract()

        self.assertEqual(result["source_status"], "degraded")
        self.assertEqual(
            result["failed_platforms"],
            ["p2", "p4", "z-extra"],
        )
        self.assertEqual(len(result["items"]), 30)

    def test_missing_database_uses_a_stable_non_leaking_error(self) -> None:
        missing = Path(self.temporary_directory.name) / "secret missing.db"

        with self.assertRaises(TrendRadarIncomplete) as raised:
            self.extract(database=missing)

        self.assertEqual(str(raised.exception), "database_missing")
        self.assertNotIn(str(missing), str(raised.exception))

    def test_logical_slot_is_allowlisted(self) -> None:
        for invalid in ("", "030", "1200", None, 30, []):
            with self.subTest(invalid=invalid):
                self.assert_incomplete(
                    "logical_slot",
                    logical_slot=invalid,
                )

    def test_requires_a_latest_crawl_record(self) -> None:
        create_database(self.database)

        self.assert_incomplete("crawl_record_missing")

    def test_collected_at_requires_timezone_aware_iso_8601(self) -> None:
        for invalid in (
            "",
            "not-a-time",
            "2026-07-24T00:31:00",
            None,
            123,
        ):
            with self.subTest(invalid=invalid):
                self.assert_incomplete(
                    "collected_at_contract",
                    collected_at=invalid,
                )

    def test_collected_at_is_normalized_to_shanghai_seconds(self) -> None:
        self.seed_complete_snapshot()

        result = self.extract(
            logical_slot="0400",
            collected_at="2026-07-23T16:31:00.987654Z",
        )

        self.assertEqual(result["logical_slot"], "0400")
        self.assertEqual(
            result["collected_at"],
            "2026-07-24T00:31:00+08:00",
        )

    def test_accepts_database_paths_with_uri_reserved_and_unicode_text(
        self,
    ) -> None:
        self.database = (
            Path(self.temporary_directory.name)
            / "快照 ? number#1.db"
        )
        self.seed_complete_snapshot()

        result = self.extract(logical_slot="0630")

        self.assertEqual(result["row_count"], 30)

    def test_reads_record_statuses_platforms_and_items_from_one_wal_snapshot(
        self,
    ) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            journal_mode = connection.execute(
                "PRAGMA journal_mode=WAL"
            ).fetchone()[0]
            add_platforms(connection, ["p1"])
            record_id = add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=1,
                platform_ids=["p1"],
            )
        self.assertEqual(journal_mode.lower(), "wal")

        real_connect = sqlite3.connect

        def commit_concurrent_change() -> None:
            with real_connect(self.database, timeout=1) as writer:
                writer.execute(
                    """
                    INSERT INTO news_items (
                        title,
                        platform_id,
                        rank,
                        url,
                        mobile_url,
                        first_crawl_time,
                        last_crawl_time,
                        crawl_count
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "concurrent private item",
                        "p1",
                        2,
                        "",
                        "",
                        LATEST_CRAWL,
                        LATEST_CRAWL,
                        1,
                    ),
                )
                writer.execute(
                    """
                    UPDATE crawl_source_status
                    SET status = 'failed'
                    WHERE crawl_record_id = ? AND platform_id = 'p1'
                    """,
                    (record_id,),
                )

        triggered_connections = []

        def connect_with_writer_hook(database, *args, **kwargs):
            connection = real_connect(database, *args, **kwargs)
            wrapped = AfterRecordFetchConnection(
                connection,
                commit_concurrent_change,
            )
            triggered_connections.append(wrapped)
            return wrapped

        with patch.object(
            trendradar.sqlite3,
            "connect",
            side_effect=connect_with_writer_hook,
        ):
            result = self.extract()

        self.assertEqual(len(triggered_connections), 1)
        self.assertEqual(result["source_status"], "live")
        self.assertEqual(result["row_count"], 1)
        self.assertEqual(len(result["items"]), 1)

    def test_read_transaction_failures_close_connection_without_leaks(
        self,
    ) -> None:
        create_database(self.database)

        for fail_stage in ("begin", "read"):
            with self.subTest(fail_stage=fail_stage):
                connection = FailingConnection(fail_stage)
                with patch.object(
                    trendradar.sqlite3,
                    "connect",
                    return_value=connection,
                ):
                    self.assert_incomplete("database_contract")

                self.assertEqual(connection.statements[0], "BEGIN")
                self.assertTrue(connection.rolled_back)
                self.assertTrue(connection.closed)

    def test_opens_database_with_a_read_only_sqlite_uri(self) -> None:
        self.seed_complete_snapshot()
        real_connect = sqlite3.connect
        calls = []

        def recording_connect(database, *args, **kwargs):
            calls.append((database, args, kwargs))
            return real_connect(database, *args, **kwargs)

        with patch.object(
            trendradar.sqlite3,
            "connect",
            side_effect=recording_connect,
        ):
            result = self.extract()

        self.assertEqual(result["row_count"], 30)
        self.assertEqual(len(calls), 1)
        database_uri, positional, keywords = calls[0]
        self.assertEqual(positional, ())
        self.assertEqual(keywords, {"uri": True})
        self.assertEqual(urlsplit(database_uri).scheme, "file")
        self.assertEqual(urlsplit(database_uri).query, "mode=ro")
        with real_connect(database_uri, uri=True) as connection:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute(
                    "CREATE TABLE must_not_be_written (id INTEGER)"
                )

    def test_missing_table_is_a_non_leaking_database_contract_error(
        self,
    ) -> None:
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """
                CREATE TABLE crawl_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crawl_time TEXT NOT NULL UNIQUE,
                    total_items INTEGER DEFAULT 0
                )
                """
            )
            connection.execute(
                """
                INSERT INTO crawl_records (crawl_time, total_items)
                VALUES (?, 0)
                """,
                (LATEST_CRAWL,),
            )

        self.assert_incomplete("database_contract")

    def test_corrupt_database_is_a_non_leaking_database_contract_error(
        self,
    ) -> None:
        self.database.write_bytes(b"private invalid sqlite content")

        self.assert_incomplete("database_contract")

    def test_rejects_invalid_item_types_without_leaking_values(self) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            add_platforms(connection, ["p1"])
            record_id = add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=1,
                platform_ids=["p1"],
            )
            connection.execute(
                """
                UPDATE news_items
                SET rank = 'private-bad-rank'
                WHERE last_crawl_time = ?
                """,
                (LATEST_CRAWL,),
            )
            self.assertGreater(record_id, 0)

        self.assert_incomplete("item_contract")

    def test_rejects_non_positive_item_integer_fields(self) -> None:
        for column in ("id", "rank", "crawl_count"):
            with self.subTest(column=column):
                self.database = (
                    Path(self.temporary_directory.name)
                    / f"invalid-{column}.db"
                )
                create_database(self.database)
                with sqlite3.connect(self.database) as connection:
                    add_platforms(connection, ["p1"])
                    add_crawl(
                        connection,
                        crawl_time=LATEST_CRAWL,
                        count=1,
                        platform_ids=["p1"],
                    )
                    connection.execute(
                        f"UPDATE news_items SET {column} = 0"
                    )

                self.assert_incomplete("item_contract")

    def test_rejects_empty_required_item_strings(self) -> None:
        for column in (
            "title",
            "platform_id",
            "first_crawl_time",
            "last_crawl_time",
        ):
            with self.subTest(column=column):
                self.database = (
                    Path(self.temporary_directory.name)
                    / f"empty-{column}.db"
                )
                create_database(self.database)
                with sqlite3.connect(self.database) as connection:
                    add_platforms(connection, ["p1"])
                    add_crawl(
                        connection,
                        crawl_time=LATEST_CRAWL,
                        count=1,
                        platform_ids=["p1"],
                    )
                    connection.execute(
                        f"UPDATE news_items SET {column} = ''"
                    )

                expected = (
                    "row_count_mismatch"
                    if column == "last_crawl_time"
                    else "item_contract"
                )
                self.assert_incomplete(expected)

    def test_rejects_empty_platform_join(self) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=1,
                platform_ids=["missing-platform"],
            )

        self.assert_incomplete("item_contract")

    def test_rejects_invalid_latest_crawl_record_fields(self) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """
                INSERT INTO crawl_records (crawl_time, total_items)
                VALUES ('', -1)
                """
            )

        self.assert_incomplete("database_contract")

    def test_requires_status_for_every_exported_platform(self) -> None:
        self.seed_complete_snapshot(
            statuses={
                "p1": "success",
                "p2": "success",
                "p3": "success",
                "p4": "success",
                "p5": "success",
            }
        )

        self.assert_incomplete("status_contract")

    def test_requires_status_for_every_active_platform(self) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            add_platforms(connection, ["p1", "p2"])
            add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=1,
                platform_ids=["p1"],
                statuses={"p1": "success"},
            )

        self.assert_incomplete("status_contract")

    def test_rejects_empty_snapshot_with_complete_success_status(
        self,
    ) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            add_platforms(connection, ["p1"])
            add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=0,
                platform_ids=["p1"],
                statuses={"p1": "success"},
            )

        self.assert_incomplete("status_contract")

    def test_rejects_empty_snapshot_with_all_failed_statuses(
        self,
    ) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            add_platforms(connection, ["p1", "p2"])
            add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=0,
                platform_ids=["p1", "p2"],
                statuses={
                    "p1": "failed",
                    "p2": "failed",
                },
            )

        self.assert_incomplete("status_contract")

    def test_allows_failed_active_platform_without_items(self) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            add_platforms(connection, ["p1", "p2"])
            add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=1,
                platform_ids=["p1"],
                statuses={
                    "p1": "success",
                    "p2": "failed",
                },
            )

        result = self.extract()

        self.assertEqual(result["source_status"], "degraded")
        self.assertEqual(result["failed_platforms"], ["p2"])
        self.assertEqual(result["platform_count"], 1)

    def test_rejects_invalid_platform_contract_without_leaking_value(
        self,
    ) -> None:
        for platform_id, is_active in (
            ("p1", 2),
            ("private-empty-id", "private-invalid-active"),
        ):
            with self.subTest(
                platform_id=platform_id,
                is_active=is_active,
            ):
                self.database = (
                    Path(self.temporary_directory.name)
                    / f"invalid-platform-{len(str(is_active))}.db"
                )
                create_database(self.database)
                with sqlite3.connect(self.database) as connection:
                    add_platforms(connection, [platform_id])
                    connection.execute(
                        """
                        UPDATE platforms
                        SET id = ?, is_active = ?
                        """,
                        (
                            "" if platform_id == "private-empty-id"
                            else platform_id,
                            is_active,
                        ),
                    )
                    add_crawl(
                        connection,
                        crawl_time=LATEST_CRAWL,
                        count=1,
                        platform_ids=[
                            ""
                            if platform_id == "private-empty-id"
                            else platform_id
                        ],
                    )

                with self.assertRaises(TrendRadarIncomplete) as raised:
                    self.extract()
                self.assertEqual(
                    str(raised.exception),
                    "database_contract",
                )
                self.assertNotIn(
                    "private",
                    str(raised.exception),
                )

    def test_rejects_items_from_an_inactive_platform(self) -> None:
        create_database(self.database)
        with sqlite3.connect(self.database) as connection:
            add_platforms(connection, ["p1", "p2"])
            connection.execute(
                "UPDATE platforms SET is_active = 0 WHERE id = 'p1'"
            )
            add_crawl(
                connection,
                crawl_time=LATEST_CRAWL,
                count=1,
                platform_ids=["p1"],
                statuses={
                    "p1": "success",
                    "p2": "success",
                },
            )

        self.assert_incomplete("status_contract")

    def test_rejects_unknown_status(self) -> None:
        self.seed_complete_snapshot(
            statuses={
                "p1": "success",
                "p2": "success",
                "p3": "success",
                "p4": "success",
                "p5": "success",
                "p6": "partial-private-value",
            }
        )

        self.assert_incomplete("status_contract")


class TrendRadarCollectorTests(unittest.TestCase):
    NOW = datetime(2026, 7, 23, 16, 1, tzinfo=timezone.utc)

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            dir=Path.cwd()
        )
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "collector-root"
        self.events_file = self.root / "events.log"

    def write_collector(
        self,
        *,
        fail_stage: str = "",
        create_database: bool = True,
        database_is_directory: bool = False,
    ) -> Path:
        package = self.root / "trendradar"
        package.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(package / "__pycache__", ignore_errors=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "__main__.py").write_text(
            "from pathlib import Path\n"
            "import sys\n"
            f"EVENTS = Path({str(self.events_file)!r})\n"
            f"ROOT = {str(self.root.resolve())!r}\n"
            f"FAIL_STAGE = {fail_stage!r}\n"
            "\n"
            "def event(name):\n"
            "    if str(Path.cwd()) != ROOT:\n"
            "        raise AssertionError('collector did not run from its root')\n"
            "    with EVENTS.open('a', encoding='utf-8') as stream:\n"
            "        stream.write(name + '\\n')\n"
            "\n"
            "event('import')\n"
            "print('collector import stdout')\n"
            "if sys.path[0] != ROOT:\n"
            "    raise AssertionError('collector root was not pinned first')\n"
            "if FAIL_STAGE == 'import':\n"
            "    raise RuntimeError('private import failure /secret/path')\n"
            "\n"
            "def load_config():\n"
            "    event('load_config')\n"
            "    print('load config stdout')\n"
            "    if FAIL_STAGE == 'load_config':\n"
            "        raise RuntimeError('private config failure token=secret')\n"
            "    return {'private': 'config'}\n"
            "\n"
            "class Context:\n"
            "    def cleanup(self):\n"
            "        event('cleanup')\n"
            "        print('cleanup stdout')\n"
            "        if FAIL_STAGE == 'cleanup':\n"
            "            raise RuntimeError('private cleanup failure /secret')\n"
            "        if FAIL_STAGE == 'crawl_cleanup':\n"
            "            raise RuntimeError('private cleanup after crawl')\n"
            "        if FAIL_STAGE == 'database_cleanup':\n"
            "            raise RuntimeError('private cleanup after database')\n"
            "\n"
            "class NewsAnalyzer:\n"
            "    def __init__(self, *, config):\n"
            "        event('NewsAnalyzer')\n"
            "        print('analyzer stdout')\n"
            "        if config != {'private': 'config'}:\n"
            "            raise AssertionError('wrong config')\n"
            "        if FAIL_STAGE == 'constructor':\n"
            "            raise RuntimeError('private constructor failure')\n"
            "        self.ctx = Context()\n"
            "\n"
            "    def _initialize_and_check_config(self):\n"
            "        event('_initialize_and_check_config')\n"
            "        print('initialize stdout')\n"
            "        if FAIL_STAGE == 'initialize':\n"
            "            raise RuntimeError('private initialize failure')\n"
            "\n"
            "    def _crawl_data(self):\n"
            "        event('_crawl_data')\n"
            "        print('crawl stdout')\n"
            "        if FAIL_STAGE in {'crawl', 'crawl_cleanup'}:\n"
            "            raise RuntimeError('private crawl failure')\n"
            "        return ({'p1': []}, {}, [])\n"
            "\n"
            "    def main(self):\n"
            "        event('forbidden:main')\n"
            "        raise AssertionError('main must not run')\n"
            "\n"
            "    def generate_html(self):\n"
            "        event('forbidden:html')\n"
            "        raise AssertionError('HTML must not run')\n"
            "\n"
            "    def fetch_rss(self):\n"
            "        event('forbidden:rss')\n"
            "        raise AssertionError('RSS must not run')\n"
            "\n"
            "    def send_notification(self):\n"
            "        event('forbidden:notification')\n"
            "        raise AssertionError('notifications must not run')\n"
            "\n"
            "    def open_browser(self):\n"
            "        event('forbidden:browser')\n"
            "        raise AssertionError('browser must not run')\n"
            "\n"
            "def main():\n"
            "    event('forbidden:module-main')\n"
            "    raise AssertionError('module main must not run')\n",
            encoding="utf-8",
        )
        database = (
            self.root / "output" / "news" / "2026-07-24.db"
        )
        if create_database:
            database.parent.mkdir(parents=True, exist_ok=True)
            if database_is_directory:
                database.mkdir()
            else:
                database.write_bytes(b"collector output")
        return database

    def events(self) -> list[str]:
        if not self.events_file.exists():
            return []
        return self.events_file.read_text(encoding="utf-8").splitlines()

    def capture_run(self, root=None, *, now=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        arguments = {}
        if now is not None:
            arguments["now"] = now
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = run_trendradar(
                self.root if root is None else root,
                **arguments,
            )
        return result, stdout.getvalue(), stderr.getvalue()

    def assert_error(self, code: str, *, root=None, now=None) -> str:
        stdout = io.StringIO()
        stderr = io.StringIO()
        arguments = {}
        if now is not None:
            arguments["now"] = now
        with redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(TrendRadarIncomplete) as raised:
                run_trendradar(
                    self.root if root is None else root,
                    **arguments,
                )
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(str(raised.exception), code)
        self.assertNotIn("private", str(raised.exception))
        self.assertNotIn("secret", str(raised.exception))
        return stderr.getvalue()

    def test_runs_only_the_pinned_collector_calls_and_returns_database(
        self,
    ) -> None:
        expected = self.write_collector()

        with patch.object(
            trendradar,
            "extract_snapshot",
            side_effect=AssertionError("extractor must not run"),
        ):
            result, stdout, stderr = self.capture_run(now=self.NOW)

        self.assertEqual(result, expected.resolve())
        self.assertEqual(stdout, "")
        self.assertEqual(
            self.events(),
            [
                "import",
                "load_config",
                "NewsAnalyzer",
                "_initialize_and_check_config",
                "_crawl_data",
                "cleanup",
            ],
        )
        for marker in (
            "collector import stdout",
            "load config stdout",
            "analyzer stdout",
            "initialize stdout",
            "crawl stdout",
            "cleanup stdout",
        ):
            self.assertIn(marker, stderr)
        self.assertFalse(
            any(event.startswith("forbidden:") for event in self.events())
        )

    def test_uses_shanghai_date_across_the_utc_day_boundary(self) -> None:
        expected = self.write_collector()

        result, _, _ = self.capture_run(now=self.NOW)

        self.assertEqual(result.name, "2026-07-24.db")
        self.assertEqual(result, expected.resolve())

    def test_rejects_naive_or_non_datetime_now_before_import(self) -> None:
        self.write_collector()

        for invalid in (
            datetime(2026, 7, 24, 0, 1),
            "2026-07-24T00:01:00+08:00",
        ):
            with self.subTest(invalid=invalid):
                self.assert_error("now_contract", now=invalid)
                self.assertEqual(self.events(), [])

    def test_accepts_relative_root_and_does_not_change_cwd(self) -> None:
        expected = self.write_collector()
        previous_cwd = Path.cwd()
        relative_root = Path(os.path.relpath(self.root, previous_cwd))

        result, _, _ = self.capture_run(
            root=relative_root,
            now=self.NOW,
        )

        self.assertEqual(result, expected.resolve())
        self.assertEqual(Path.cwd(), previous_cwd)

    def test_missing_or_non_directory_root_is_stable_and_non_leaking(
        self,
    ) -> None:
        missing = self.root / "private-secret-missing"
        non_directory = self.root / "private-secret-file"
        self.root.mkdir()
        non_directory.write_text("secret", encoding="utf-8")

        for invalid in (missing, non_directory):
            with self.subTest(invalid=invalid):
                self.assert_error(
                    "root_missing",
                    root=invalid,
                    now=self.NOW,
                )

    def test_missing_or_non_file_database_is_stable_and_cleans_up(
        self,
    ) -> None:
        for database_is_directory in (False, True):
            with self.subTest(database_is_directory=database_is_directory):
                self.write_collector(
                    create_database=database_is_directory,
                    database_is_directory=database_is_directory,
                )
                self.assert_error("database_missing", now=self.NOW)
                self.assertEqual(self.events().count("cleanup"), 1)
                self.events_file.unlink()
                database = (
                    self.root / "output" / "news" / "2026-07-24.db"
                )
                if database.is_dir():
                    database.rmdir()

    def test_import_initialize_and_crawl_errors_are_non_leaking(
        self,
    ) -> None:
        for stage, expected_cleanup_count in (
            ("import", 0),
            ("load_config", 0),
            ("constructor", 0),
            ("initialize", 1),
            ("crawl", 1),
        ):
            with self.subTest(stage=stage):
                self.write_collector(fail_stage=stage)
                self.assert_error("collector_failed", now=self.NOW)
                self.assertEqual(
                    self.events().count("cleanup"),
                    expected_cleanup_count,
                )
                self.events_file.unlink()

    def test_cleanup_failure_has_its_own_non_leaking_error(self) -> None:
        self.write_collector(fail_stage="cleanup")

        self.assert_error("cleanup_failed", now=self.NOW)

        self.assertEqual(self.events().count("cleanup"), 1)

    def test_cleanup_failure_does_not_replace_a_collector_error(self) -> None:
        self.write_collector(fail_stage="crawl_cleanup")

        self.assert_error("collector_failed", now=self.NOW)

        self.assertEqual(self.events().count("cleanup"), 1)

    def test_cleanup_failure_does_not_replace_a_database_error(self) -> None:
        self.write_collector(
            fail_stage="database_cleanup",
            create_database=False,
        )

        self.assert_error("database_missing", now=self.NOW)

        self.assertEqual(self.events().count("cleanup"), 1)

    def test_restores_sys_path_cwd_and_cached_trendradar_modules(
        self,
    ) -> None:
        self.write_collector()
        prior_package = types.ModuleType("trendradar")
        prior_main = types.ModuleType("trendradar.__main__")
        prior_nested = types.ModuleType("trendradar.cached")

        def cached_bomb():
            raise AssertionError("cached collector must not be used")

        prior_main.load_config = cached_bomb
        saved_modules = {
            "trendradar": sys.modules.get("trendradar"),
            "trendradar.__main__": sys.modules.get("trendradar.__main__"),
            "trendradar.cached": sys.modules.get("trendradar.cached"),
        }
        sys.modules["trendradar"] = prior_package
        sys.modules["trendradar.__main__"] = prior_main
        sys.modules["trendradar.cached"] = prior_nested
        saved_path = list(sys.path)
        saved_cwd = Path.cwd()
        try:
            result, _, _ = self.capture_run(now=self.NOW)

            self.assertEqual(result.name, "2026-07-24.db")
            self.assertEqual(sys.path, saved_path)
            self.assertEqual(Path.cwd(), saved_cwd)
            self.assertIs(sys.modules["trendradar"], prior_package)
            self.assertIs(sys.modules["trendradar.__main__"], prior_main)
            self.assertIs(sys.modules["trendradar.cached"], prior_nested)
            self.assertEqual(
                {
                    name
                    for name in sys.modules
                    if (
                        name == "trendradar"
                        or name.startswith("trendradar.")
                    )
                },
                set(saved_modules),
            )
            self.assertEqual(self.events()[0], "import")
        finally:
            for name, module in saved_modules.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module

    def test_restores_process_and_import_state_after_failure(self) -> None:
        self.write_collector(fail_stage="crawl")
        saved_path = list(sys.path)
        saved_cwd = Path.cwd()
        saved_modules = {
            name: module
            for name, module in sys.modules.items()
            if name == "trendradar" or name.startswith("trendradar.")
        }

        self.assert_error("collector_failed", now=self.NOW)

        self.assertEqual(sys.path, saved_path)
        self.assertEqual(Path.cwd(), saved_cwd)
        self.assertEqual(
            {
                name: module
                for name, module in sys.modules.items()
                if name == "trendradar" or name.startswith("trendradar.")
            },
            saved_modules,
        )


if __name__ == "__main__":
    unittest.main()
