from __future__ import annotations

import io
import json
import traceback
import unittest
from urllib.error import HTTPError
from zipfile import ZIP_DEFLATED, ZipFile

from content_radar_feed.github_artifacts import (
    API_VERSION,
    ArtifactError,
    USER_AGENT,
    artifact_name,
    download_latest_snapshots,
    safe_extract_json,
    select_latest_artifacts,
)


REPORT_DATE = "2026-07-24"
SLOTS = ("0030", "0400", "0630")


def _artifact(
    artifact_id: int,
    slot: str,
    created_at: str,
    *,
    report_date: str = REPORT_DATE,
    expired: bool = False,
    name: str | None = None,
) -> dict:
    return {
        "id": artifact_id,
        "name": name or artifact_name(report_date, slot),
        "created_at": created_at,
        "expired": expired,
    }


def _archive(value: object, filename: str = "snapshot.json") -> bytes:
    output = io.BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            filename,
            json.dumps(value, ensure_ascii=False).encode("utf-8"),
        )
    return output.getvalue()


def _snapshot(slot: str, report_date: str = REPORT_DATE) -> dict:
    return {
        "report_date": report_date,
        "logical_slot": slot,
        "items": [],
    }


class SelectionTests(unittest.TestCase):
    def test_selects_latest_unexpired_exact_name_for_each_slot(self) -> None:
        artifacts = [
            _artifact(101, "0030", "2026-07-23T16:31:00Z"),
            _artifact(202, "0400", "2026-07-23T20:01:00Z"),
            _artifact(303, "0630", "2026-07-23T22:31:00Z"),
            _artifact(304, "0630", "2026-07-23T23:21:00Z"),
            _artifact(
                305,
                "0630",
                "2026-07-23T23:22:00Z",
                expired=True,
            ),
            _artifact(
                306,
                "0630",
                "2026-07-23T23:23:00Z",
                report_date="2026-07-23",
            ),
            _artifact(
                307,
                "0630",
                "2026-07-23T23:24:00Z",
                name=f"trendradar-snapshot-{REPORT_DATE}-06300",
            ),
        ]

        selected = select_latest_artifacts(
            artifacts,
            report_date=REPORT_DATE,
            logical_slots=SLOTS,
        )

        self.assertEqual(selected["0030"]["id"], 101)
        self.assertEqual(selected["0400"]["id"], 202)
        self.assertEqual(selected["0630"]["id"], 304)

    def test_rejects_malformed_candidate_metadata(self) -> None:
        with self.assertRaisesRegex(ArtifactError, "^artifact_contract$"):
            select_latest_artifacts(
                [_artifact(1, "0030", "")],
                report_date=REPORT_DATE,
                logical_slots=("0030",),
            )


class ArchiveTests(unittest.TestCase):
    def test_rejects_path_traversal_before_reading_json(self) -> None:
        with self.assertRaisesRegex(ArtifactError, "^unsafe_archive$"):
            safe_extract_json(_archive(_snapshot("0030"), "../../secret"))

    def test_rejects_embedded_slot_mismatch(self) -> None:
        with self.assertRaisesRegex(ArtifactError, "^logical_slot_mismatch$"):
            safe_extract_json(
                _archive(_snapshot("0400")),
                report_date=REPORT_DATE,
                logical_slot="0030",
            )

    def test_rejects_embedded_report_date_mismatch(self) -> None:
        with self.assertRaisesRegex(ArtifactError, "^report_date_mismatch$"):
            safe_extract_json(
                _archive(_snapshot("0030", "2026-07-23")),
                report_date=REPORT_DATE,
                logical_slot="0030",
            )

    def test_rejects_non_dictionary_json(self) -> None:
        with self.assertRaisesRegex(ArtifactError, "^snapshot_contract$"):
            safe_extract_json(
                _archive([]),
                report_date=REPORT_DATE,
                logical_slot="0030",
            )


class RetrievalTests(unittest.TestCase):
    def test_returns_snapshots_and_explicit_missing_slots(self) -> None:
        artifacts = [
            _artifact(101, "0030", "2026-07-23T16:31:00Z"),
            _artifact(304, "0630", "2026-07-23T23:21:00Z"),
        ]
        responses = {
            (
                "https://api.github.com/repos/Anxin-tec/"
                "content-radar-feed/actions/artifacts?per_page=100"
            ): json.dumps({"artifacts": artifacts}).encode("utf-8"),
            (
                "https://api.github.com/repos/Anxin-tec/"
                "content-radar-feed/actions/artifacts/101/zip"
            ): _archive(_snapshot("0030")),
            (
                "https://api.github.com/repos/Anxin-tec/"
                "content-radar-feed/actions/artifacts/304/zip"
            ): _archive(_snapshot("0630")),
        }
        requests = []

        def request(value):
            requests.append(value)
            return responses[value.full_url]

        restored = download_latest_snapshots(
            "test-token",
            report_date=REPORT_DATE,
            logical_slots=SLOTS,
            request=request,
        )

        self.assertEqual(
            set(restored["snapshots"]),
            {"0030", "0630"},
        )
        self.assertEqual(restored["missing_slots"], ["0400"])
        self.assertEqual(len(requests), 3)
        for value in requests:
            self.assertEqual(value.method, "GET")
            self.assertEqual(
                value.get_header("Accept"),
                "application/vnd.github+json",
            )
            self.assertEqual(
                value.get_header("Authorization"),
                "Bearer test-token",
            )
            self.assertEqual(
                value.get_header("X-github-api-version"),
                API_VERSION,
            )
            self.assertEqual(value.get_header("User-agent"), USER_AGENT)

    def test_request_failure_does_not_leak_token(self) -> None:
        token = "super-secret-token"

        def fail(value):
            raise HTTPError(
                value.full_url,
                403,
                f"denied {token}",
                hdrs=None,
                fp=None,
            )

        with self.assertRaises(ArtifactError) as raised:
            download_latest_snapshots(
                token,
                report_date=REPORT_DATE,
                logical_slots=SLOTS,
                request=fail,
            )

        self.assertEqual(str(raised.exception), "github_request_failed")
        rendered = "".join(
            traceback.format_exception(
                type(raised.exception),
                raised.exception,
                raised.exception.__traceback__,
            )
        )
        self.assertNotIn(token, rendered)


if __name__ == "__main__":
    unittest.main()
