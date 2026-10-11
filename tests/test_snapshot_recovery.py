from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from content_radar_feed.markdown_report import render_report
from content_radar_feed.privacy import validate_public_report
from content_radar_feed.publication import require_publishable
from content_radar_feed.report import ReportError, build_report
from test_relevance_and_report import report_arguments, snapshot, trend_item


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schema"
    / "public-report.schema.json"
)


def without_platform(value: dict, platform_id: str) -> None:
    value["items"] = [
        item for item in value["items"]
        if item["platform_id"] != platform_id
    ]
    value["row_count"] = len(value["items"])
    value["platform_count"] = len({
        item["platform_id"] for item in value["items"]
    })


def recovery_arguments() -> dict:
    arguments = report_arguments()
    first = arguments["snapshots"][0]
    first["source_status"] = "degraded"
    first["failed_platforms"] = ["zhihu"]
    without_platform(first, "zhihu")
    first["items"].append(trend_item(
        item_id=11,
        title="OpenAI 早期独有消息",
        platform_id="weibo",
        platform="微博",
        rank=10,
        url="https://weibo.example/early-only",
    ))
    first["row_count"] = len(first["items"])
    return arguments


class SnapshotRecoveryTests(unittest.TestCase):
    def assert_publishable(self, arguments: dict) -> dict:
        report = build_report(**arguments)
        self.assertEqual(
            report["source_status"]["trendradar"]["status"], "live"
        )
        validate_public_report(
            report,
            SCHEMA_PATH,
            max_bytes=1_000_000,
            expected_date=arguments["report_date"],
        )
        require_publishable(report, arguments["report_date"])
        return report

    def assert_trendradar_rejected(self, arguments: dict) -> dict:
        report = build_report(**arguments)
        self.assertNotEqual(
            report["source_status"]["trendradar"]["status"], "live"
        )
        with self.assertRaisesRegex(
            ValueError, "^publication_sources_incomplete$"
        ):
            require_publishable(report, arguments["report_date"])
        return report

    def test_later_complete_snapshot_recovers_without_erasing_history(self):
        arguments = recovery_arguments()
        original = deepcopy(arguments)

        report = self.assert_publishable(arguments)

        self.assertEqual(arguments, original)
        self.assertEqual(
            report["source_status"]["trendradar"],
            {"status": "live", "snapshot_count": 3, "platform_count": 2},
        )
        self.assertIn("trendradar_incomplete_slots", report["warnings"])
        self.assertIn("曾有部分平台采集失败", render_report(report))
        by_url = {item["url"]: item for item in report["trendradar_items"]}
        self.assertEqual(
            by_url["https://weibo.example/early-only"]["crawl_count"], 1
        )
        repeated = by_url["https://weibo.example/openai"]
        self.assertEqual(repeated["crawl_count"], 3)
        self.assertEqual(repeated["rank_change"], 7)
        self.assertEqual(
            repeated["first_crawl_time"], "2026-07-24T00:31:00+08:00"
        )
        self.assertEqual(
            by_url["https://zhihu.example/deepseek"]["crawl_count"], 2
        )

    def test_later_live_snapshot_cannot_omit_an_unrecovered_failed_platform(self):
        arguments = recovery_arguments()
        for value in arguments["snapshots"][1:]:
            without_platform(value, "zhihu")
        self.assert_trendradar_rejected(arguments)

    def test_latest_live_snapshot_cannot_omit_a_previously_successful_platform(self):
        arguments = report_arguments()
        without_platform(arguments["snapshots"][-1], "zhihu")
        self.assert_trendradar_rejected(arguments)

    def test_failure_after_recovery_blocks_publication_even_with_platform_items(self):
        arguments = recovery_arguments()
        latest = arguments["snapshots"][-1]
        latest["source_status"] = "degraded"
        latest["failed_platforms"] = ["zhihu"]
        self.assertTrue(any(
            item["platform_id"] == "zhihu" for item in latest["items"]
        ))
        self.assert_trendradar_rejected(arguments)

    def test_all_degraded_snapshots_cannot_publish(self):
        arguments = report_arguments()
        for value in arguments["snapshots"]:
            value["source_status"] = "degraded"
            value["failed_platforms"] = ["zhihu"]
        self.assert_trendradar_rejected(arguments)

    def test_no_snapshots_cannot_publish(self):
        arguments = report_arguments()
        arguments["snapshots"] = []
        report = self.assert_trendradar_rejected(arguments)
        self.assertEqual(report["source_status"]["trendradar"]["status"], "failed")

    def test_empty_live_snapshot_cannot_publish(self):
        arguments = report_arguments()
        arguments["snapshots"] = [
            snapshot("0630", "2026-07-24T06:31:00+08:00", [])
        ]
        self.assert_trendradar_rejected(arguments)

    def test_non_ai_raw_items_can_prove_platform_recovery(self):
        arguments = recovery_arguments()
        for item in arguments["snapshots"][-1]["items"]:
            if item["platform_id"] == "zhihu":
                item["title"] = "城市今日天气预报"

        report = self.assert_publishable(arguments)

        self.assertFalse(any(
            item["platform_id"] == "zhihu" for item in report["trendradar_items"]
        ))
        self.assertEqual(report["source_status"]["trendradar"]["platform_count"], 2)

    def test_live_label_with_nonempty_failure_list_cannot_publish(self):
        arguments = report_arguments()
        arguments["snapshots"][-1]["failed_platforms"] = ["zhihu"]
        self.assert_trendradar_rejected(arguments)

    def test_aihot_failure_still_blocks_an_otherwise_recovered_report(self):
        for status in ("failed", "incomplete"):
            with self.subTest(status=status):
                arguments = recovery_arguments()
                arguments["aihot_result"]["status"] = status
                report = build_report(**arguments)
                self.assertEqual(
                    report["source_status"]["trendradar"]["status"], "live"
                )
                self.assertEqual(report["aihot_items"], [])
                with self.assertRaisesRegex(
                    ValueError, "^publication_sources_incomplete$"
                ):
                    require_publishable(report, arguments["report_date"])

    def test_input_order_does_not_change_recovery_or_aggregated_items(self):
        arguments = recovery_arguments()
        expected = self.assert_publishable(arguments)
        arguments["snapshots"].reverse()
        self.assertEqual(self.assert_publishable(arguments), expected)

    def test_latest_health_uses_actual_time_not_logical_slot_or_offset_text(self):
        arguments = report_arguments()
        # A rerun of 0030 collected at 06:34 Shanghai time is later than 0630.
        arguments["snapshots"][0]["collected_at"] = "2026-07-23T22:34:00+00:00"
        arguments["snapshots"][-1]["source_status"] = "degraded"
        arguments["snapshots"][-1]["failed_platforms"] = ["zhihu"]
        arguments["snapshots"] = [
            arguments["snapshots"][2],
            arguments["snapshots"][0],
            arguments["snapshots"][1],
        ]
        report = self.assert_publishable(arguments)
        repeated = next(
            item for item in report["trendradar_items"]
            if item["url"] == "https://weibo.example/openai"
        )
        self.assertEqual(
            repeated["first_crawl_time"], "2026-07-24T04:01:00+08:00"
        )
        self.assertEqual(
            repeated["last_crawl_time"], "2026-07-23T22:34:00+00:00"
        )
        self.assertEqual(repeated["rank_change"], -4)
        self.assertEqual(repeated["rank"], 9)

    def test_equal_actual_collection_times_do_not_inflate_crawl_count(self):
        arguments = report_arguments()
        arguments["snapshots"] = arguments["snapshots"][1:]
        arguments["snapshots"][0]["collected_at"] = "2026-07-23T22:31:00+00:00"
        report = self.assert_publishable(arguments)
        self.assertTrue(all(
            item["crawl_count"] == 1 for item in report["trendradar_items"]
        ))

    def test_repeated_slot_uses_latest_actual_time(self):
        for latest_status in ("live", "degraded"):
            with self.subTest(latest_status=latest_status):
                arguments = report_arguments()
                older = deepcopy(arguments["snapshots"][0])
                newer = deepcopy(arguments["snapshots"][-1])
                older["source_status"] = (
                    "degraded" if latest_status == "live" else "live"
                )
                older["failed_platforms"] = (
                    ["zhihu"] if older["source_status"] == "degraded" else []
                )
                newer["logical_slot"] = "0030"
                newer["collected_at"] = "2026-07-23T22:31:00+00:00"
                newer["source_status"] = latest_status
                newer["failed_platforms"] = (
                    ["zhihu"] if latest_status == "degraded" else []
                )
                arguments["snapshots"] = [newer, older]
                if latest_status == "live":
                    report = self.assert_publishable(arguments)
                else:
                    report = self.assert_trendradar_rejected(arguments)
                self.assertEqual(
                    report["source_status"]["trendradar"]["snapshot_count"], 1
                )
                self.assertEqual(report["counts"]["trendradar_raw"], len(newer["items"]))
                self.assertTrue(all(
                    item["crawl_count"] == 1 for item in report["trendradar_items"]
                ))

    def test_conflicting_same_slot_at_equal_actual_time_is_rejected(self):
        arguments = report_arguments()
        healthy = deepcopy(arguments["snapshots"][-1])
        unhealthy = deepcopy(healthy)
        unhealthy["collected_at"] = "2026-07-23T22:31:00+00:00"
        unhealthy["source_status"] = "degraded"
        unhealthy["failed_platforms"] = ["zhihu"]
        for values in ([healthy, unhealthy], [unhealthy, healthy]):
            with self.subTest(first_status=values[0]["source_status"]):
                arguments["snapshots"] = values
                with self.assertRaises(ReportError):
                    build_report(**arguments)

    def test_equal_time_latest_slots_cannot_hide_an_unhealthy_snapshot(self):
        arguments = report_arguments()
        arguments["snapshots"][-1]["collected_at"] = "2026-07-24T06:31:00+08:00"
        unhealthy = arguments["snapshots"][1]
        unhealthy["collected_at"] = "2026-07-23T22:31:00+00:00"
        unhealthy["source_status"] = "degraded"
        unhealthy["failed_platforms"] = ["zhihu"]
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                if reverse:
                    arguments["snapshots"].reverse()
                self.assert_trendradar_rejected(arguments)


if __name__ == "__main__":
    unittest.main()
