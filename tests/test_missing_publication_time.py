"""A missing original timestamp must not discard the complete source feed."""
from datetime import datetime, timezone
from pathlib import Path
import unittest

from content_radar_feed.aihot import AihotIncomplete, fetch_all_items, project_public_item
from content_radar_feed.markdown_report import render_report
from content_radar_feed.privacy import PublicBoundaryError, validate_public_report
from content_radar_feed.publication import require_publishable
from content_radar_feed.report import build_report
from test_aihot import item, terminal_page
from test_relevance_and_report import report_arguments


class MissingPublicationTimeTests(unittest.TestCase):
    since = datetime(2026, 7, 23, 7, tzinfo=timezone.utc)
    until = datetime(2026, 7, 24, 7, tzinfo=timezone.utc)

    def missing_time_item(self):
        value = item("missing-time", None)
        value["discoveredAt"] = "2026-07-23T12:00:00Z"
        return value

    def test_all_items_survive_and_unknown_time_is_not_fabricated(self):
        values = [item("known", "2026-07-23T10:00:00Z"), self.missing_time_item()]
        result = fetch_all_items(lambda _: terminal_page(*values), since=self.since, until=self.until)
        args = report_arguments()
        args["aihot_result"]["items"] = [project_public_item(v) for v in result.items]
        report = build_report(**args)
        self.assertEqual([v["id"] for v in report["aihot_items"]], ["known", "missing-time"])
        self.assertIsNone(report["aihot_items"][1]["published_at"])
        self.assertEqual(report["counts"]["aihot_upstream"], 2)
        self.assertEqual(report["counts"]["aihot_published"], 2)
        self.assertIn("aihot_missing_published_at", report["warnings"])
        schema = Path(__file__).resolve().parents[1] / "schema/public-report.schema.json"
        validate_public_report(report, schema, max_bytes=2_000_000, expected_date=report["report_date"])
        require_publishable(report, report["report_date"])
        text = render_report(report)
        self.assertIn("### A2", text)
        self.assertIn("发布时间：未提供", text)
        self.assertIn("真实收录时间", text)
        report["warnings"].remove("aihot_missing_published_at")
        with self.assertRaisesRegex(PublicBoundaryError, "publication_time_warning_mismatch"):
            validate_public_report(report, schema, max_bytes=2_000_000, expected_date=report["report_date"])

    def test_missing_or_invalid_discovery_time_cannot_prove_the_window(self):
        for discovered in (None, "", "not-a-time", "2026-07-23T12:00:00", "2026-07-22T12:00:00Z", "2026-07-25T12:00:00Z"):
            with self.subTest(discovered=discovered):
                value = self.missing_time_item()
                value["discoveredAt"] = discovered
                with self.assertRaises(AihotIncomplete):
                    fetch_all_items(lambda _: terminal_page(value), since=self.since, until=self.until)

    def test_present_but_invalid_publication_time_is_not_silently_replaced(self):
        for published in ("", "not-a-time", "2026-07-22T12:00:00Z", "2026-07-25T12:00:00Z"):
            value = self.missing_time_item()
            value["publishedAt"] = published
            with self.assertRaises(AihotIncomplete):
                fetch_all_items(lambda _: terminal_page(value), since=self.since, until=self.until)
