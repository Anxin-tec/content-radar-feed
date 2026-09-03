from __future__ import annotations

import unittest

from content_radar_feed.relevance import is_ai_related
from content_radar_feed.report import ReportError, build_report


def aihot_item(item_id: str, **extra: object) -> dict:
    value = {
        "id": item_id,
        "title": f"AI HOT {item_id}",
        "title_en": f"English {item_id}",
        "permalink": f"https://aihot.example/items/{item_id}",
        "url": f"https://news.example/{item_id}",
        "source": "AI HOT",
        "published_at": "2026-07-24T00:00:00Z",
        "summary": f"Summary {item_id}",
        "category": "industry",
        "score": 8,
        "selected": True,
        "attribution": {
            "source": "AI HOT",
            "canonical": f"https://aihot.example/items/{item_id}",
        },
    }
    value.update(extra)
    return value


def trend_item(
    *,
    item_id: int,
    title: str,
    platform_id: str,
    platform: str,
    rank: int,
    url: str | None,
) -> dict:
    return {
        "id": item_id,
        "title": title,
        "platform_id": platform_id,
        "platform": platform,
        "rank": rank,
        "url": url,
        "first_crawl_time": "2026-07-24 00:30:00",
        "last_crawl_time": "2026-07-24 06:30:00",
        "crawl_count": 1,
    }


def snapshot(
    slot: str,
    collected_at: str,
    items: list[dict],
    *,
    source_status: str = "live",
    failed_platforms: list[str] | None = None,
) -> dict:
    return {
        "schema_version": 1,
        "logical_slot": slot,
        "collected_at": collected_at,
        "source_status": source_status,
        "crawl_time": collected_at,
        "row_count": len(items),
        "platform_count": len(
            {value["platform_id"] for value in items}
        ),
        "failed_platforms": list(failed_platforms or []),
        "items": items,
    }


def report_arguments() -> dict:
    common = dict(
        title="OpenAI 新模型",
        platform_id="weibo",
        platform="微博",
        url="https://weibo.example/openai",
    )
    same_title = "DeepSeek 推理成本再下降"
    return {
        "report_date": "2026-07-24",
        "generated_at": "2026-07-24T06:35:00+08:00",
        "window_start": "2026-07-23T06:35:00+08:00",
        "window_end": "2026-07-24T06:35:00+08:00",
        "run_id": "run-1",
        "aihot_result": {
            "status": "live",
            "api_version": "1.4.0",
            "page_count": 2,
            "items": [
                aihot_item("a1", reason="private"),
                aihot_item("a2", urgency_hint="private"),
                aihot_item("a3", suggested_column="private"),
            ],
        },
        "snapshots": [
            snapshot(
                "0030",
                "2026-07-24T00:31:00+08:00",
                [
                    trend_item(item_id=1, rank=9, **common),
                    trend_item(
                        item_id=2,
                        title=same_title,
                        platform_id="weibo",
                        platform="微博",
                        rank=4,
                        url="https://weibo.example/deepseek",
                    ),
                    trend_item(
                        item_id=3,
                        title=same_title,
                        platform_id="zhihu",
                        platform="知乎",
                        rank=7,
                        url="https://zhihu.example/deepseek",
                    ),
                    trend_item(
                        item_id=4,
                        title="城市今日天气预报",
                        platform_id="weibo",
                        platform="微博",
                        rank=1,
                        url="https://weibo.example/weather",
                    ),
                ],
            ),
            snapshot(
                "0400",
                "2026-07-24T04:01:00+08:00",
                [
                    trend_item(item_id=5, rank=5, **common),
                    trend_item(
                        item_id=6,
                        title=same_title,
                        platform_id="weibo",
                        platform="微博",
                        rank=3,
                        url="https://weibo.example/deepseek",
                    ),
                    trend_item(
                        item_id=7,
                        title=same_title,
                        platform_id="zhihu",
                        platform="知乎",
                        rank=6,
                        url="https://zhihu.example/deepseek",
                    ),
                ],
            ),
            snapshot(
                "0630",
                "2026-07-24T06:31:00+08:00",
                [
                    trend_item(item_id=8, rank=2, **common),
                    trend_item(
                        item_id=9,
                        title=same_title,
                        platform_id="weibo",
                        platform="微博",
                        rank=2,
                        url="https://weibo.example/deepseek",
                    ),
                    trend_item(
                        item_id=10,
                        title=same_title,
                        platform_id="zhihu",
                        platform="知乎",
                        rank=5,
                        url="https://zhihu.example/deepseek",
                    ),
                ],
            ),
        ],
    }


class RelevanceTests(unittest.TestCase):
    def test_matches_expected_ai_terms(self) -> None:
        self.assertTrue(is_ai_related("OpenAI 发布新模型"))
        self.assertTrue(is_ai_related("DeepSeek 推理成本再下降"))
        self.assertTrue(is_ai_related("英伟达发布新一代 AI 芯片"))

    def test_rejects_unrelated_titles(self) -> None:
        self.assertFalse(is_ai_related("明星参加综艺节目"))
        self.assertFalse(is_ai_related("城市今日天气预报"))

    def test_returns_only_a_boolean(self) -> None:
        self.assertIs(type(is_ai_related("ChatGPT 更新")), bool)


class DailyReportTests(unittest.TestCase):
    def test_builds_complete_stable_lists_and_counts(self) -> None:
        report = build_report(**report_arguments())

        self.assertEqual(
            [value["id"] for value in report["aihot_items"]],
            ["a1", "a2", "a3"],
        )
        self.assertEqual(
            [value["ref"] for value in report["aihot_items"]],
            ["A1", "A2", "A3"],
        )
        self.assertEqual(
            [value["ref"] for value in report["trendradar_items"]],
            ["N1", "N2", "N3"],
        )
        self.assertEqual(
            report["counts"],
            {
                "aihot_upstream": 3,
                "aihot_published": 3,
                "trendradar_raw": 4,
                "trendradar_matched": 3,
                "trendradar_published": 3,
            },
        )
        self.assertEqual(
            report["source_status"]["trendradar"],
            {
                "status": "live",
                "snapshot_count": 3,
                "platform_count": 2,
            },
        )
        self.assertEqual(report["warnings"], [])

        by_platform = {
            (value["platform_id"], value["url"]): value
            for value in report["trendradar_items"]
        }
        repeated = by_platform[
            ("weibo", "https://weibo.example/openai")
        ]
        self.assertEqual(repeated["crawl_count"], 3)
        self.assertEqual(repeated["rank_change"], 7)
        self.assertEqual(
            {
                value["platform_id"]
                for value in report["trendradar_items"]
                if value["title"] == "DeepSeek 推理成本再下降"
            },
            {"weibo", "zhihu"},
        )
        for value in (
            report["aihot_items"] + report["trendradar_items"]
        ):
            self.assertTrue(
                {"reason", "suggested_column", "urgency_hint"}.isdisjoint(
                    value
                )
            )

    def test_reference_order_is_stable_for_same_inputs(self) -> None:
        first = build_report(**report_arguments())
        second = build_report(**report_arguments())

        self.assertEqual(
            first["trendradar_items"],
            second["trendradar_items"],
        )

    def test_missing_history_does_not_hide_live_source(self) -> None:
        arguments = report_arguments()
        arguments["snapshots"] = [
            value
            for value in arguments["snapshots"]
            if value["logical_slot"] != "0400"
        ]

        report = build_report(**arguments)

        self.assertEqual(
            report["source_status"]["trendradar"]["status"],
            "live",
        )
        self.assertEqual(
            report["warnings"],
            ["trendradar_incomplete_slots"],
        )

    def test_no_snapshots_marks_trendradar_failed(self) -> None:
        arguments = report_arguments()
        arguments["snapshots"] = []

        report = build_report(**arguments)

        self.assertEqual(report["trendradar_items"], [])
        self.assertEqual(
            report["source_status"]["trendradar"],
            {
                "status": "failed",
                "snapshot_count": 0,
                "platform_count": 0,
            },
        )
        self.assertEqual(
            report["warnings"],
            ["trendradar_incomplete_slots"],
        )

    def test_failed_or_incomplete_aihot_never_publishes_partial_items(
        self,
    ) -> None:
        for status in ("failed", "incomplete"):
            with self.subTest(status=status):
                arguments = report_arguments()
                arguments["aihot_result"] = {
                    "status": status,
                    "api_version": None,
                    "page_count": 1,
                    "items": [aihot_item("partial")],
                }

                report = build_report(**arguments)

                self.assertEqual(report["aihot_items"], [])
                self.assertEqual(report["counts"]["aihot_upstream"], 0)
                self.assertEqual(report["counts"]["aihot_published"], 0)
                self.assertEqual(
                    report["source_status"]["aihot"]["status"],
                    status,
                )
                self.assertEqual(
                    report["warnings"],
                    ["aihot_source_incomplete"],
                )

    def test_both_sources_failed_is_diagnostic_not_successful(self) -> None:
        arguments = report_arguments()
        arguments["aihot_result"] = {
            "status": "failed",
            "items": [],
        }
        arguments["snapshots"] = []

        report = build_report(**arguments)

        self.assertNotIn("status", report)
        self.assertEqual(report["aihot_items"], [])
        self.assertEqual(report["trendradar_items"], [])
        self.assertEqual(
            report["warnings"],
            [
                "aihot_source_incomplete",
                "trendradar_incomplete_slots",
            ],
        )

    def test_invalid_input_raises_only_an_allowlisted_error_code(self) -> None:
        arguments = report_arguments()
        arguments["snapshots"][0]["logical_slot"] = (
            "/Users/private/secret.db"
        )

        with self.assertRaises(ReportError) as raised:
            build_report(**arguments)

        self.assertEqual(str(raised.exception), "logical_slot")
        self.assertNotIn("private", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
