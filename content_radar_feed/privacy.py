from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Optional
from urllib.parse import parse_qsl, urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError


PRIVATE_KEYS = {
    "reason",
    "suggested_column",
    "urgency_hint",
    "db_path",
    "token",
    "cookie",
    "authorization",
    "secret",
    "password",
}
PRIVATE_VALUE_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"file://", re.I),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"Traceback \(most recent call last\):"),
)
SENSITIVE_QUERY_KEYS = {
    "token",
    "key",
    "signature",
    "auth",
    "authorization",
}
HTTPS_VALUE = re.compile(r"https://[^\s<>\"']+", re.I)


class PublicBoundaryError(ValueError):
    """The report is not safe for public delivery."""


def _has_sensitive_query(value: str) -> bool:
    for candidate in HTTPS_VALUE.findall(value):
        try:
            parsed = urlsplit(candidate)
            parameter_texts = [parsed.query]
            if parsed.fragment:
                parameter_texts.append(parsed.fragment)
                if "?" in parsed.fragment:
                    parameter_texts.append(
                        parsed.fragment.split("?", 1)[1]
                    )
            for parameter_text in parameter_texts:
                keys = {
                    key.strip().casefold().replace("-", "_")
                    for key, _ in parse_qsl(
                        parameter_text,
                        keep_blank_values=True,
                    )
                }
                if keys.intersection(SENSITIVE_QUERY_KEYS):
                    return True
        except ValueError:
            return True
    return False


def scan_public_value(value: object) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if (
                isinstance(key, str)
                and key.casefold() in PRIVATE_KEYS
            ):
                raise PublicBoundaryError("private_key")
            scan_public_value(nested)
        return
    if isinstance(value, list):
        for nested in value:
            scan_public_value(nested)
        return
    if isinstance(value, str):
        if any(pattern.search(value) for pattern in PRIVATE_VALUE_PATTERNS):
            raise PublicBoundaryError("private_value")
        if _has_sensitive_query(value):
            raise PublicBoundaryError("sensitive_url")


def validate_references_and_counts(report: dict) -> None:
    aihot_items = report["aihot_items"]
    trendradar_items = report["trendradar_items"]
    if [item["ref"] for item in aihot_items] != [
        f"A{index}"
        for index in range(1, len(aihot_items) + 1)
    ]:
        raise PublicBoundaryError("reference_contract")
    if [item["ref"] for item in trendradar_items] != [
        f"N{index}"
        for index in range(1, len(trendradar_items) + 1)
    ]:
        raise PublicBoundaryError("reference_contract")

    counts = report["counts"]
    if (
        counts["aihot_upstream"] != len(aihot_items)
        or counts["aihot_published"] != len(aihot_items)
        or counts["trendradar_matched"] != len(trendradar_items)
        or counts["trendradar_published"] != len(trendradar_items)
        or counts["trendradar_raw"] < len(trendradar_items)
    ):
        raise PublicBoundaryError("count_contract")

    aihot_ids = [item["id"] for item in aihot_items]
    trendradar_ids = [item["id"] for item in trendradar_items]
    if (
        len(aihot_ids) != len(set(aihot_ids))
        or len(trendradar_ids) != len(set(trendradar_ids))
    ):
        raise PublicBoundaryError("duplicate_id")


def validate_public_report(
    report: dict,
    schema_path: Path,
    *,
    max_bytes: int,
    expected_date: Optional[str] = None,
) -> None:
    try:
        schema = json.loads(
            schema_path.read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, SchemaError):
        raise PublicBoundaryError("schema_unavailable") from None

    try:
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).validate(report)
    except ValidationError:
        raise PublicBoundaryError("schema_validation") from None

    scan_public_value(report)
    validate_references_and_counts(report)
    if (
        expected_date is not None
        and report["report_date"] != expected_date
    ):
        raise PublicBoundaryError("report_date_mismatch")
    if type(max_bytes) is not int or max_bytes <= 0:
        raise PublicBoundaryError("capacity_contract")
    try:
        encoded = json.dumps(
            report,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise PublicBoundaryError("schema_validation") from None
    if len(encoded) > max_bytes:
        raise PublicBoundaryError("delivery_capacity_exceeded")
