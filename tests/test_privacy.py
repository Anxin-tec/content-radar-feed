from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from content_radar_feed.privacy import (
    PublicBoundaryError,
    validate_public_report,
)
from content_radar_feed.report import build_report


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schema"
    / "public-report.schema.json"
)
MAX_BYTES = 1_000_000


def _aihot_item() -> dict:
    return {
        "id": "a1",
        "title": "OpenAI 发布新模型",
        "title_en": "OpenAI releases a new model",
        "permalink": "https://aihot.virxact.com/items/a1",
        "url": "https://openai.com/news/a1",
        "source": "AI HOT",
        "published_at": "2026-07-24T00:00:00Z",
        "summary": "Summary",
        "category": "industry",
        "score": 8,
        "selected": True,
        "attribution": {
            "source": "AI HOT",
            "canonical": "https://aihot.virxact.com/items/a1",
        },
    }


def _snapshot(slot: str, collected_at: str) -> dict:
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
                "title": "DeepSeek 推理成本下降",
                "platform_id": "weibo",
                "platform": "微博",
                "rank": 2,
                "url": "https://weibo.com/hot/deepseek",
                "first_crawl_time": "2026-07-24 00:30:00",
                "last_crawl_time": "2026-07-24 06:30:00",
                "crawl_count": 1,
            }
        ],
    }


def valid_report() -> dict:
    return build_report(
        report_date="2026-07-24",
        generated_at="2026-07-24T06:35:00+08:00",
        window_start="2026-07-23T06:35:00+08:00",
        window_end="2026-07-24T06:35:00+08:00",
        run_id="run-1",
        aihot_result={
            "status": "live",
            "api_version": "1.4.0",
            "page_count": 1,
            "items": [_aihot_item()],
        },
        snapshots=[
            _snapshot("0030", "2026-07-24T00:31:00+08:00"),
            _snapshot("0400", "2026-07-24T04:01:00+08:00"),
            _snapshot("0630", "2026-07-24T06:31:00+08:00"),
        ],
    )


class PublicPrivacyTests(unittest.TestCase):
    def assert_rejected(
        self,
        report: dict,
        *,
        code: str,
        rejected_value: str | None = None,
        expected_date: str | None = None,
        max_bytes: int = MAX_BYTES,
    ) -> None:
        with self.assertRaises(PublicBoundaryError) as raised:
            validate_public_report(
                report,
                SCHEMA_PATH,
                max_bytes=max_bytes,
                expected_date=expected_date,
            )
        self.assertEqual(str(raised.exception), code)
        if rejected_value is not None:
            self.assertNotIn(rejected_value, str(raised.exception))

    def test_accepts_report_built_by_report_builder(self) -> None:
        validate_public_report(
            valid_report(),
            SCHEMA_PATH,
            max_bytes=MAX_BYTES,
            expected_date="2026-07-24",
        )

    def test_rejects_unknown_top_level_field(self) -> None:
        report = valid_report()
        report["private"] = "secret"
        self.assert_rejected(report, code="schema_validation")

    def test_rejects_unknown_nested_item_field(self) -> None:
        report = valid_report()
        report["aihot_items"][0]["private"] = "secret"
        self.assert_rejected(report, code="schema_validation")

    def test_rejects_private_keys(self) -> None:
        for key in (
            "reason",
            "suggested_column",
            "urgency_hint",
            "db_path",
        ):
            with self.subTest(key=key):
                report = valid_report()
                report["aihot_items"][0][key] = "secret"
                self.assert_rejected(report, code="schema_validation")

    def test_rejects_local_user_path_without_leaking_it(self) -> None:
        rejected = "/Users/macbook/private/report.db"
        report = valid_report()
        report["aihot_items"][0]["summary"] = rejected
        self.assert_rejected(
            report,
            code="private_value",
            rejected_value=rejected,
        )

    def test_rejects_file_uri_without_leaking_it(self) -> None:
        rejected = "file:///private/report.db"
        report = valid_report()
        report["aihot_items"][0]["summary"] = rejected
        self.assert_rejected(
            report,
            code="private_value",
            rejected_value=rejected,
        )

    def test_rejects_github_classic_token_without_leaking_it(self) -> None:
        rejected = "ghp_12345678901234567890"
        report = valid_report()
        report["aihot_items"][0]["summary"] = rejected
        self.assert_rejected(
            report,
            code="private_value",
            rejected_value=rejected,
        )

    def test_rejects_github_fine_grained_token_without_leaking_it(
        self,
    ) -> None:
        rejected = "github_pat_12345678901234567890"
        report = valid_report()
        report["aihot_items"][0]["summary"] = rejected
        self.assert_rejected(
            report,
            code="private_value",
            rejected_value=rejected,
        )

    def test_rejects_openai_token_without_leaking_it(self) -> None:
        rejected = "sk-12345678901234567890"
        report = valid_report()
        report["aihot_items"][0]["summary"] = rejected
        self.assert_rejected(
            report,
            code="private_value",
            rejected_value=rejected,
        )

    def test_rejects_raw_traceback_without_leaking_it(self) -> None:
        rejected = (
            "Traceback (most recent call last):\n"
            '  File "/Users/macbook/job.py", line 1'
        )
        report = valid_report()
        report["aihot_items"][0]["summary"] = rejected
        self.assert_rejected(
            report,
            code="private_value",
            rejected_value=rejected,
        )

    def test_rejects_sensitive_url_query_keys(self) -> None:
        for key in (
            "token",
            "key",
            "signature",
            "auth",
            "authorization",
        ):
            with self.subTest(key=key):
                rejected = f"https://openai.com/news?a=1&{key}=secret"
                report = valid_report()
                report["aihot_items"][0]["url"] = rejected
                self.assert_rejected(
                    report,
                    code="sensitive_url",
                    rejected_value=rejected,
                )

    def test_rejects_wrong_expected_date(self) -> None:
        self.assert_rejected(
            valid_report(),
            code="report_date_mismatch",
            expected_date="2026-07-25",
        )

    def test_rejects_wrong_timezone(self) -> None:
        report = valid_report()
        report["timezone"] = "UTC"
        self.assert_rejected(report, code="schema_validation")

    def test_rejects_non_contiguous_aihot_references(self) -> None:
        report = valid_report()
        report["aihot_items"][0]["ref"] = "A2"
        self.assert_rejected(report, code="reference_contract")

    def test_rejects_non_contiguous_trendradar_references(self) -> None:
        report = valid_report()
        report["trendradar_items"][0]["ref"] = "N2"
        self.assert_rejected(report, code="reference_contract")

    def test_rejects_declared_count_not_equal_to_array_length(self) -> None:
        report = valid_report()
        report["counts"]["aihot_published"] = 2
        self.assert_rejected(report, code="count_contract")

    def test_rejects_duplicate_aihot_id(self) -> None:
        report = valid_report()
        duplicate = copy.deepcopy(report["aihot_items"][0])
        duplicate["ref"] = "A2"
        report["aihot_items"].append(duplicate)
        report["counts"]["aihot_upstream"] = 2
        report["counts"]["aihot_published"] = 2
        self.assert_rejected(report, code="duplicate_id")

    def test_rejects_json_over_explicit_byte_ceiling(self) -> None:
        report = valid_report()
        encoded_size = len(
            json.dumps(
                report,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        self.assert_rejected(
            report,
            code="delivery_capacity_exceeded",
            max_bytes=encoded_size - 1,
        )

    def test_rejects_non_https_url(self) -> None:
        report = valid_report()
        report["trendradar_items"][0]["url"] = (
            "http://weibo.com/hot/deepseek"
        )
        self.assert_rejected(report, code="schema_validation")

    def test_rejects_unknown_status_and_warning(self) -> None:
        for path in ("status", "warning"):
            with self.subTest(path=path):
                report = valid_report()
                if path == "status":
                    report["source_status"]["aihot"]["status"] = "ok"
                else:
                    report["warnings"] = ["unknown_warning"]
                self.assert_rejected(
                    report,
                    code="schema_validation",
                )


if __name__ == "__main__":
    unittest.main()
