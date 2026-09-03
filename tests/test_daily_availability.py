from copy import deepcopy
import unittest

from content_radar_feed.publication import require_publishable
from content_radar_feed.report import build_report, ReportError
from content_radar_feed.markdown_report import render_report
from test_relevance_and_report import report_arguments


class DailyAvailabilityTests(unittest.TestCase):
    def test_plain_text_report_preserves_every_entry_in_order(self):
        report = build_report(**report_arguments())
        rendered = render_report(report)
        positions = []
        for item in report["aihot_items"] + report["trendradar_items"]:
            marker = f'### {item["ref"]}｜{item["title"]}'
            self.assertEqual(rendered.count(marker), 1)
            positions.append(rendered.index(marker))
        self.assertEqual(positions, sorted(positions))

    def test_first_real_snapshot_is_publishable_without_previous_runs(self):
        args = report_arguments()
        args["snapshots"] = args["snapshots"][:1]
        args["generated_at"] = "2026-07-24T00:35:00+08:00"
        result = build_report(**args)
        require_publishable(result, "2026-07-24")
        self.assertEqual(result["source_status"]["trendradar"]["snapshot_count"], 1)
        self.assertIn("trendradar_incomplete_slots", result["warnings"])
        self.assertTrue(all(v["crawl_count"] == 1 and v["rank_change"] == 0
                            for v in result["trendradar_items"]))

    def test_failed_refresh_cannot_replace_public_report(self):
        report = build_report(**report_arguments())
        for source in ("aihot", "trendradar"):
            for status in ("failed", "incomplete", "degraded"):
                candidate = deepcopy(report)
                candidate["source_status"][source]["status"] = status
                with self.assertRaises(ValueError):
                    require_publishable(candidate, "2026-07-24")

    def test_yesterday_and_future_snapshots_are_rejected(self):
        for timestamp in ("2026-07-23T00:31:00+08:00", "2026-07-25T00:31:00+08:00",
                          "2026-07-24T09:31:00+08:00", "2026-07-24T00:31:00"):
            args = report_arguments()
            args["snapshots"][0]["collected_at"] = timestamp
            with self.assertRaises(ReportError):
                build_report(**args)

    def test_wrong_report_date_is_rejected(self):
        with self.assertRaises(ValueError):
            require_publishable(build_report(**report_arguments()), "2026-07-25")
