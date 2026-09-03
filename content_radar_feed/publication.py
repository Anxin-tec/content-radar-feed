"""Reject unhealthy refreshes before modifying any public feed files."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def require_publishable(report: dict, report_date: str) -> None:
    if report.get("report_date") != report_date:
        raise ValueError("publication_date_mismatch")
    generated = datetime.fromisoformat(report["generated_at"])
    if (generated.tzinfo is None or
            generated.astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat() != report_date):
        raise ValueError("publication_date_mismatch")
    statuses = report["source_status"]
    if (statuses["aihot"]["status"] not in {"live", "not_modified"}
            or statuses["trendradar"]["status"] != "live"
            or statuses["trendradar"]["snapshot_count"] < 1):
        raise ValueError("publication_sources_incomplete")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    args = parser.parse_args()
    require_publishable(json.loads(args.candidate.read_text()), args.report_date)


if __name__ == "__main__":
    main()
