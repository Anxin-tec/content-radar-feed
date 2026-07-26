from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from content_radar_feed.aihot import AihotIncomplete
from content_radar_feed import cli


MAX_BYTES = 2_000_000
REPORT_DATE = "2026-07-24"


def _snapshot(slot: str, collected_at: str, title: str) -> dict:
    return {
        "schema_version": 1,
        "logical_slot": slot,
        "collected_at": collected_at,
        "source_status": "live",
        "crawl_time": collected_at,
        "row_count": 1,
        "platform_count": 1,
        "failed_platforms": [],
        "items": [
            {
                "id": 1,
                "title": title,
                "platform_id": "test",
                "platform": "测试源",
                "rank": 1,
                "url": (
                    "https://example.com/item/"
                    + title.casefold().replace(" ", "-")
                ),
                "first_crawl_time": collected_at,
                "last_crawl_time": collected_at,
                "crawl_count": 1,
            }
        ],
    }


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False),
        encoding="utf-8",
    )


class CliTests(unittest.TestCase):
    def _fixture(self, root: Path, size: str) -> dict:
        result = cli.main(
            [
                "build-fixture",
                "--report-date",
                REPORT_DATE,
                "--size",
                size,
                "--site-dir",
                str(root),
                "--max-bytes",
                str(MAX_BYTES),
            ]
        )
        self.assertEqual(result, 0)
        return json.loads(
            (root / "reports" / f"{REPORT_DATE}.json").read_text(
                encoding="utf-8"
            )
        )

    def test_builds_small_fixture_and_latest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self._fixture(root, "small")

            self.assertEqual(len(report["aihot_items"]), 3)
            self.assertEqual(len(report["trendradar_items"]), 3)
            self.assertEqual(
                report,
                json.loads(
                    (root / "latest.json").read_text(encoding="utf-8")
                ),
            )

    def test_builds_maximum_fixture_with_capacity_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = self._fixture(Path(directory), "maximum")

            self.assertEqual(len(report["aihot_items"]), 150)
            self.assertEqual(len(report["trendradar_items"]), 100)
            marked = [
                report["aihot_items"][index]["title"]
                for index in (0, 74, 149)
            ] + [
                report["trendradar_items"][index]["title"]
                for index in (0, 49, 99)
            ]
            self.assertEqual(len(set(marked)), 6)
            for marker in cli.MAXIMUM_FIXTURE_MARKERS:
                self.assertTrue(any(marker in title for title in marked))

    def test_validate_report_accepts_valid_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root, "small")

            result = cli.main(
                [
                    "validate-report",
                    "--input",
                    str(root / "reports" / f"{REPORT_DATE}.json"),
                    "--max-bytes",
                    str(MAX_BYTES),
                ]
            )

            self.assertEqual(result, 0)

    def test_invalid_report_is_not_published(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = cli.make_fixture(REPORT_DATE, "small")
            invalid["counts"]["aihot_published"] += 1
            snapshots = root / "snapshot.json"
            _write_json(
                snapshots,
                _snapshot(
                    "0030",
                    "2026-07-24T00:31:00+08:00",
                    "OpenAI old",
                ),
            )
            with mock.patch(
                "content_radar_feed.cli.build_daily_report",
                return_value=invalid,
            ), mock.patch(
                "content_radar_feed.cli.fetch_aihot",
                return_value={
                    "status": "live",
                    "api_version": "test",
                    "page_count": 1,
                    "items": [],
                },
            ):
                result = cli.main(
                    [
                        "build-report",
                        "--report-date",
                        REPORT_DATE,
                        "--snapshot",
                        str(snapshots),
                        "--site-dir",
                        str(root / "site"),
                        "--max-bytes",
                        str(MAX_BYTES),
                    ]
                )

            self.assertNotEqual(result, 0)
            self.assertFalse((root / "site").exists())

    def test_collect_trendradar_preserves_requested_slot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "snapshot.json"
            expected = _snapshot(
                "0400",
                "2026-07-24T04:01:00+08:00",
                "OpenAI collected",
            )
            with mock.patch(
                "content_radar_feed.cli.run_trendradar",
                return_value=Path("/tmp/collector.db"),
            ), mock.patch(
                "content_radar_feed.cli.extract_snapshot",
                return_value=expected,
            ) as extract:
                result = cli.main(
                    [
                        "collect-trendradar",
                        "--trendradar-root",
                        str(Path(directory)),
                        "--logical-slot",
                        "0400",
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))[
                    "logical_slot"
                ],
                "0400",
            )
            self.assertEqual(extract.call_args.kwargs["logical_slot"], "0400")

    def test_build_report_selects_latest_repeated_slot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshots = [
                _snapshot(
                    "0030",
                    "2026-07-24T00:31:00+08:00",
                    "OpenAI OLD MARKER",
                ),
                _snapshot(
                    "0030",
                    "2026-07-24T00:32:00+08:00",
                    "OpenAI NEW MARKER",
                ),
                _snapshot(
                    "0400",
                    "2026-07-24T04:01:00+08:00",
                    "城市天气",
                ),
                _snapshot(
                    "0630",
                    "2026-07-24T06:31:00+08:00",
                    "城市天气",
                ),
            ]
            paths = []
            for index, snapshot in enumerate(snapshots):
                path = root / f"{index}.json"
                _write_json(path, snapshot)
                paths.append(path)
            arguments = [
                "build-report",
                "--report-date",
                REPORT_DATE,
            ]
            for path in paths:
                arguments.extend(["--snapshot", str(path)])
            arguments.extend(
                [
                    "--site-dir",
                    str(root / "site"),
                    "--max-bytes",
                    str(MAX_BYTES),
                ]
            )
            with mock.patch(
                "content_radar_feed.cli.fetch_aihot",
                return_value={
                    "status": "live",
                    "api_version": "test",
                    "page_count": 1,
                    "items": [],
                },
            ):
                result = cli.main(arguments)

            report = json.loads(
                (
                    root
                    / "site"
                    / "reports"
                    / f"{REPORT_DATE}.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(result, 0)
            self.assertEqual(
                [item["title"] for item in report["trendradar_items"]],
                ["OpenAI NEW MARKER"],
            )

    def test_build_report_refuses_zero_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = cli.main(
                [
                    "build-report",
                    "--report-date",
                    REPORT_DATE,
                    "--site-dir",
                    str(Path(directory) / "site"),
                    "--max-bytes",
                    str(MAX_BYTES),
                ]
            )
            self.assertNotEqual(result, 0)
            self.assertFalse((Path(directory) / "site").exists())

    def test_build_report_publishes_aihot_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "snapshot.json"
            _write_json(
                path,
                _snapshot(
                    "0030",
                    "2026-07-24T00:31:00+08:00",
                    "OpenAI item",
                ),
            )
            with mock.patch(
                "content_radar_feed.cli.fetch_aihot",
                side_effect=AihotIncomplete("cursor_loop"),
            ):
                result = cli.main(
                    [
                        "build-report",
                        "--report-date",
                        REPORT_DATE,
                        "--snapshot",
                        str(path),
                        "--site-dir",
                        str(root / "site"),
                        "--max-bytes",
                        str(MAX_BYTES),
                    ]
                )

            report = json.loads(
                (
                    root
                    / "site"
                    / "reports"
                    / f"{REPORT_DATE}.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(result, 0)
            self.assertEqual(
                report["source_status"]["aihot"]["status"],
                "incomplete",
            )
            self.assertEqual(report["aihot_items"], [])


if __name__ == "__main__":
    unittest.main()
