from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import ipaddress
import json
import math
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


BASE_URL = "https://aihot.virxact.com/api/public"
USER_AGENT = "content-radar-cloud/1.0"
MAX_PAGES = 25
MAX_ITEMS = 2500
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
REQUIRED_FIELDS = {
    "id",
    "title",
    "permalink",
    "source",
    "publishedAt",
    "category",
}
PUBLIC_ITEM_KEYS = {
    "id",
    "title",
    "title_en",
    "permalink",
    "url",
    "source",
    "published_at",
    "summary",
    "category",
    "score",
    "selected",
    "attribution",
}
SENSITIVE_PARAMETER_KEYS = {
    "token",
    "access_token",
    "refresh_token",
    "id_token",
    "api_key",
    "apikey",
    "key",
    "signature",
    "x_amz_signature",
    "x_amz_credential",
    "x_amz_security_token",
    "x_goog_signature",
    "sig",
    "auth",
    "authorization",
    "client_secret",
    "secret",
    "password",
    "passwd",
    "credential",
    "session",
    "sessionid",
    "jwt",
    "awsaccesskeyid",
    "access_key_id",
}
SENSITIVE_QUERY_KEYS = SENSITIVE_PARAMETER_KEYS
NON_PUBLIC_DNS_SUFFIXES = {
    "localhost",
    "local",
    "localdomain",
    "internal",
    "intranet",
    "lan",
    "home",
    "home.arpa",
    "corp",
    "private",
    "test",
    "invalid",
    "example",
    "onion",
    "alt",
}
IPV4_NON_GLOBAL_OVERRIDES = (
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
)
IPV4_GLOBAL_EXCEPTIONS = {
    ipaddress.ip_address("192.0.0.9"),
    ipaddress.ip_address("192.0.0.10"),
}
IPV6_NON_GLOBAL_OVERRIDES = (
    ipaddress.ip_network("64:ff9b:1::/48"),
    ipaddress.ip_network("2001::/23"),
    ipaddress.ip_network("2002::/16"),
)
IPV6_GLOBAL_EXCEPTIONS = (
    ipaddress.ip_network("2001:1::1/128"),
    ipaddress.ip_network("2001:1::2/128"),
    ipaddress.ip_network("2001:3::/32"),
    ipaddress.ip_network("2001:4:112::/48"),
    ipaddress.ip_network("2001:20::/28"),
    ipaddress.ip_network("2001:30::/28"),
)


class AihotIncomplete(ValueError):
    """The upstream response could not prove a complete result."""


class _RequestFailure(AihotIncomplete):
    def __init__(self, code: str, *, retryable: bool) -> None:
        super().__init__(code)
        self.code = code
        self.retryable = retryable


class _RejectRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self,
        request,
        file_pointer,
        code,
        message,
        headers,
        new_url,
    ):
        return None


@dataclass(frozen=True)
class AihotResult:
    status: str
    page_count: int
    items: list[dict]


def _utc_datetime(value: datetime, error_code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise AihotIncomplete(error_code)
    try:
        if value.utcoffset() is None:
            raise AihotIncomplete(error_code)
        return value.astimezone(timezone.utc)
    except (OverflowError, ValueError) as error:
        raise AihotIncomplete(error_code) from error


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise AihotIncomplete("time_format")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise AihotIncomplete("time_format") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AihotIncomplete("time_format")
    return parsed.astimezone(timezone.utc)


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace(
        "+00:00",
        "Z",
    )


def _validate_item(value: object) -> dict:
    if not isinstance(value, dict) or not REQUIRED_FIELDS.issubset(value):
        raise AihotIncomplete("item_contract")
    if any(
        not isinstance(value[field], str)
        or not value[field].strip()
        for field in REQUIRED_FIELDS
    ):
        raise AihotIncomplete("item_contract")
    return value


def fetch_all_items(
    request_page: Callable[[str | None], dict],
    *,
    since: datetime,
    until: datetime | None = None,
    sleep: Callable[[float], None] = time.sleep,
    max_pages: int = MAX_PAGES,
    max_items: int = MAX_ITEMS,
) -> AihotResult:
    if (
        type(max_pages) is not int
        or max_pages <= 0
        or type(max_items) is not int
        or max_items <= 0
    ):
        raise AihotIncomplete("limit_contract")
    since_utc = _utc_datetime(since, "since_timezone")
    until_utc = (
        _utc_datetime(until, "until_timezone")
        if until is not None
        else None
    )
    if until_utc is not None and until_utc < since_utc:
        raise AihotIncomplete("window_contract")
    cursor = None
    seen_cursors: set[str] = set()
    seen_ids: set[str] = set()
    all_items: list[dict] = []
    page_count = 0

    while True:
        payload = request_page(cursor)
        page_count += 1
        if not isinstance(payload, dict):
            raise AihotIncomplete("page_contract")
        items = payload.get("items")
        count = payload.get("count")
        if (
            not isinstance(items, list)
            or type(count) is not int
            or count != len(items)
        ):
            raise AihotIncomplete("page_contract")
        if len(all_items) + len(items) > max_items:
            raise AihotIncomplete("item_limit")

        for value in items:
            value = _validate_item(value)

            item_id = value["id"]
            if item_id in seen_ids:
                raise AihotIncomplete("duplicate_item")
            published_at = parse_time(value["publishedAt"])
            if (
                published_at < since_utc
                or (
                    until_utc is not None
                    and published_at > until_utc
                )
            ):
                raise AihotIncomplete("outside_window")
            seen_ids.add(item_id)
            all_items.append(value)

        has_next = payload.get("hasNext")
        next_cursor = payload.get("nextCursor")
        if has_next is False:
            if "nextCursor" not in payload or next_cursor is not None:
                raise AihotIncomplete("terminal_contract")
            break
        if has_next is True and page_count >= max_pages:
            raise AihotIncomplete("page_limit")
        if (
            has_next is not True
            or not isinstance(next_cursor, str)
            or not next_cursor.strip()
        ):
            raise AihotIncomplete("cursor_contract")
        if next_cursor in seen_cursors:
            raise AihotIncomplete("cursor_loop")

        seen_cursors.add(next_cursor)
        cursor = next_cursor
        sleep(1.0)

    return AihotResult(
        status="live",
        page_count=page_count,
        items=all_items,
    )


def request_json_url(url: str, timeout: float = 30) -> dict:
    if not isinstance(url, str) or not url:
        raise AihotIncomplete("request_contract")
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        method="GET",
    )
    opener = build_opener(_RejectRedirectHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        code = error.code
        error.close()
        raise _RequestFailure(
            f"http_{code}",
            retryable=type(code) is int and 500 <= code < 600,
        ) from None
    except TimeoutError:
        raise _RequestFailure("timeout", retryable=True) from None
    except URLError:
        raise _RequestFailure("url_error", retryable=True) from None
    except OSError:
        raise _RequestFailure("os_error", retryable=True) from None

    if not isinstance(body, bytes):
        raise AihotIncomplete("response_encoding")
    if len(body) > MAX_RESPONSE_BYTES:
        raise AihotIncomplete("response_too_large")
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        raise AihotIncomplete("response_encoding") from None
    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        raise AihotIncomplete("invalid_json") from None
    if not isinstance(payload, dict):
        raise AihotIncomplete("response_contract")
    return payload


def _request_failure_details(error: BaseException) -> tuple[str, bool]:
    if isinstance(error, _RequestFailure):
        return error.code, error.retryable
    if isinstance(error, HTTPError):
        code = error.code
        error.close()
        return (
            f"http_{code}",
            type(code) is int and 500 <= code < 600,
        )
    if isinstance(error, TimeoutError):
        return "timeout", True
    if isinstance(error, URLError):
        return "url_error", True
    if isinstance(error, OSError):
        return "os_error", True
    if isinstance(error, json.JSONDecodeError):
        return "invalid_json", False
    if isinstance(error, AihotIncomplete):
        code = str(error)
        if code.startswith("http_"):
            try:
                status = int(code.removeprefix("http_"))
            except ValueError:
                return "request_failed", False
            return code, 500 <= status < 600
        if code in {"timeout", "url_error", "os_error", "network_error"}:
            return code, True
        if code in {
            "invalid_json",
            "request_contract",
            "response_contract",
            "response_encoding",
            "response_too_large",
        }:
            return code, False
    return "request_failed", False


def request_json_with_retry(
    request_json: Callable[[str], dict],
    url: str,
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    if not callable(request_json) or not isinstance(url, str) or not url:
        raise AihotIncomplete("request_contract")

    for attempt in range(2):
        try:
            payload = request_json(url)
        except (
            AihotIncomplete,
            HTTPError,
            TimeoutError,
            URLError,
            OSError,
            json.JSONDecodeError,
        ) as error:
            code, retryable = _request_failure_details(error)
            if retryable and attempt == 0:
                sleep(1.0)
                continue
            raise AihotIncomplete(code) from None

        if not isinstance(payload, dict):
            raise AihotIncomplete("response_contract")
        return payload

    raise AihotIncomplete("request_failed")


def request_items_page(
    request_json: Callable[[str], dict],
    since: datetime,
    cursor: str | None,
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    since_utc = _utc_datetime(since, "since_timezone")
    if cursor is not None and (
        not isinstance(cursor, str) or not cursor.strip()
    ):
        raise AihotIncomplete("cursor_contract")

    parameters = [
        ("mode", "selected"),
        ("since", _format_utc(since_utc)),
        ("take", "100"),
    ]
    if cursor is not None:
        parameters.append(("cursor", cursor))
    url = f"{BASE_URL}/items?{urlencode(parameters)}"
    return request_json_with_retry(
        request_json,
        url,
        sleep=sleep,
    )


def _parse_ipv4_component(value: str) -> int:
    lowered = value.casefold()
    if lowered.startswith("0x"):
        digits = value[2:]
        if (
            not digits
            or len(digits) > 8
            or any(
                character not in "0123456789abcdefABCDEF"
                for character in digits
            )
        ):
            raise ValueError
        return int(digits, 16)
    if len(value) > 1 and value.startswith("0"):
        digits = value[1:]
        if (
            len(digits) > 11
            or any(character not in "01234567" for character in digits)
        ):
            raise ValueError
        return int(digits or "0", 8)
    if (
        not value
        or len(value) > 10
        or any(character not in "0123456789" for character in value)
    ):
        raise ValueError
    return int(value, 10)


def _parse_legacy_ipv4(
    hostname: str,
) -> tuple[bool, ipaddress.IPv4Address | None]:
    parts = hostname.split(".")
    looks_numeric = bool(parts) and all(
        part.isascii()
        and (
            part.isdigit()
            or part.casefold().startswith("0x")
        )
        for part in parts
    )
    if not looks_numeric:
        return False, None
    if not 1 <= len(parts) <= 4:
        return True, None

    try:
        numbers = [_parse_ipv4_component(part) for part in parts]
    except ValueError:
        return True, None

    limits = {
        1: (0xFFFFFFFF,),
        2: (0xFF, 0xFFFFFF),
        3: (0xFF, 0xFF, 0xFFFF),
        4: (0xFF, 0xFF, 0xFF, 0xFF),
    }[len(numbers)]
    if any(number > limit for number, limit in zip(numbers, limits)):
        return True, None

    if len(numbers) == 1:
        encoded = numbers[0]
    elif len(numbers) == 2:
        encoded = (numbers[0] << 24) | numbers[1]
    elif len(numbers) == 3:
        encoded = (
            (numbers[0] << 24)
            | (numbers[1] << 16)
            | numbers[2]
        )
    else:
        encoded = (
            (numbers[0] << 24)
            | (numbers[1] << 16)
            | (numbers[2] << 8)
            | numbers[3]
        )
    return True, ipaddress.IPv4Address(encoded)


def _classify_ip_hostname(
    hostname: str,
) -> tuple[bool, ipaddress.IPv4Address | ipaddress.IPv6Address | None]:
    try:
        return True, ipaddress.ip_address(hostname)
    except ValueError:
        return _parse_legacy_ipv4(hostname)


def _is_public_ip_address(
    address: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> bool:
    if isinstance(address, ipaddress.IPv4Address):
        if (
            any(
                address in network
                for network in IPV4_NON_GLOBAL_OVERRIDES
            )
            and address not in IPV4_GLOBAL_EXCEPTIONS
        ):
            return False
    else:
        if address.is_site_local:
            return False
        if any(
            address in network
            for network in IPV6_GLOBAL_EXCEPTIONS
        ):
            return True
        if any(
            address in network
            for network in IPV6_NON_GLOBAL_OVERRIDES
        ):
            return False
    return (
        address.is_global
        and not address.is_multicast
        and not address.is_loopback
        and not address.is_link_local
        and not address.is_unspecified
        and not address.is_private
        and not address.is_reserved
    )


def _is_public_dns_hostname(hostname: str) -> bool:
    try:
        ascii_hostname = hostname.encode("idna").decode("ascii").casefold()
    except UnicodeError:
        return False
    labels = ascii_hostname.split(".")
    if (
        len(labels) < 2
        or len(ascii_hostname) > 253
        or any(
            not label
            or len(label) > 63
            or label.startswith("-")
            or label.endswith("-")
            or any(
                not character.isalnum() and character != "-"
                for character in label
            )
            for label in labels
        )
    ):
        return False
    for label in labels:
        if not label.startswith("xn--"):
            continue
        try:
            decoded = label.encode("ascii").decode("idna")
            round_trip = decoded.encode("idna").decode("ascii").casefold()
        except UnicodeError:
            return False
        if round_trip != label:
            return False
    return not any(
        ascii_hostname == suffix
        or ascii_hostname.endswith(f".{suffix}")
        for suffix in NON_PUBLIC_DNS_SUFFIXES
    )


def _split_public_https_url(value: str):
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or any(
            character.isspace()
            or ord(character) < 0x20
            or ord(character) == 0x7F
            for character in value
        )
    ):
        return None
    try:
        parsed = urlsplit(value)
        parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme.casefold() != "https"
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or "\\" in parsed.netloc
    ):
        return None

    try:
        hostname = (
            parsed.hostname.encode("idna")
            .decode("ascii")
            .casefold()
            .removesuffix(".")
        )
    except UnicodeError:
        return None
    is_ip, address = _classify_ip_hostname(hostname)
    if is_ip:
        if address is None or not _is_public_ip_address(address):
            return None
    elif not _is_public_dns_hostname(hostname):
        return None
    return parsed


def _has_sensitive_parameters(parsed) -> bool:
    parameter_strings = [parsed.query]
    if parsed.fragment:
        parameter_strings.append(parsed.fragment)
        if "?" in parsed.fragment:
            parameter_strings.append(
                parsed.fragment.split("?", 1)[1]
            )

    for parameter_string in parameter_strings:
        try:
            pairs = parse_qsl(
                parameter_string,
                keep_blank_values=True,
            )
        except ValueError:
            return True
        keys = {
            key.strip().casefold().replace("-", "_")
            for key, _ in pairs
        }
        if keys.intersection(SENSITIVE_PARAMETER_KEYS):
            return True
    return False


def _project_original_url(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise AihotIncomplete("item_contract")
    parsed = _split_public_https_url(value)
    if parsed is None or _has_sensitive_parameters(parsed):
        return None
    return value


def _project_attribution(value: object) -> dict:
    if value is None:
        return {"source": None, "canonical": None}
    if not isinstance(value, dict):
        raise AihotIncomplete("item_contract")

    source = value.get("source")
    canonical = value.get("canonical")
    if source is not None and not isinstance(source, str):
        raise AihotIncomplete("item_contract")
    if canonical is not None and not isinstance(canonical, str):
        raise AihotIncomplete("item_contract")
    if canonical is not None:
        parsed = _split_public_https_url(canonical)
        if parsed is None or _has_sensitive_parameters(parsed):
            canonical = None
    return {
        "source": source,
        "canonical": canonical,
    }


def project_public_item(value: dict) -> dict:
    upstream = _validate_item(value)

    title_en = upstream.get("title_en")
    summary = upstream.get("summary")
    score = upstream.get("score")
    selected = upstream.get("selected")
    if title_en is not None and not isinstance(title_en, str):
        raise AihotIncomplete("item_contract")
    if summary is not None and not isinstance(summary, str):
        raise AihotIncomplete("item_contract")
    if score is not None and (
        type(score) not in {int, float}
        or not math.isfinite(score)
    ):
        raise AihotIncomplete("item_contract")
    if selected is not None and type(selected) is not bool:
        raise AihotIncomplete("item_contract")

    permalink = upstream["permalink"]
    parsed_permalink = _split_public_https_url(permalink)
    if (
        parsed_permalink is None
        or _has_sensitive_parameters(parsed_permalink)
    ):
        raise AihotIncomplete("permalink_url")

    return {
        "id": upstream["id"],
        "title": upstream["title"],
        "title_en": title_en,
        "permalink": permalink,
        "url": _project_original_url(upstream.get("url")),
        "source": upstream["source"],
        "published_at": _format_utc(
            parse_time(upstream["publishedAt"])
        ),
        "summary": summary,
        "category": upstream["category"],
        "score": score,
        "selected": selected,
        "attribution": _project_attribution(
            upstream.get("attribution")
        ),
    }


def fetch_aihot(
    *,
    now: datetime,
    request_json: Callable[[str], dict] = request_json_url,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    now_utc = _utc_datetime(now, "now_timezone")
    since = now_utc - timedelta(hours=24)
    version = request_json_with_retry(
        request_json,
        f"{BASE_URL}/version",
        sleep=sleep,
    )
    api_version = version.get("apiVersion")
    if not isinstance(api_version, str) or not api_version.strip():
        raise AihotIncomplete("version_contract")

    result = fetch_all_items(
        lambda cursor: request_items_page(
            request_json,
            since,
            cursor,
            sleep=sleep,
        ),
        since=since,
        until=now_utc,
        sleep=sleep,
    )
    return {
        "status": result.status,
        "api_version": api_version,
        "page_count": result.page_count,
        "window_start": _format_utc(since),
        "items": [
            project_public_item(value)
            for value in result.items
        ],
    }
