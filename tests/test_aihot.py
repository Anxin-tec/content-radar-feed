from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPRedirectHandler, Request

import content_radar_feed.aihot as aihot
from content_radar_feed.aihot import AihotIncomplete, fetch_all_items


WINDOW_START = datetime(2026, 7, 22, tzinfo=timezone.utc)
NON_PUBLIC_URLS = (
    "https://localhost/article",
    "https://api.localhost/article",
    "https://LOCALHOST./article",
    "https://intranet/article",
    "https://printer.local/article",
    "https://service.internal/article",
    "https://router.home.arpa/article",
    "https://service.example/article",
    "https://service.test/article",
    "https://service.invalid/article",
    "https://service.onion/article",
    "https://service.alt/article",
    "https://127.0.0.1/article",
    "https://10.1.2.3/article",
    "https://172.16.10.20/article",
    "https://192.168.1.1/article",
    "https://169.254.169.254/latest/meta-data",
    "https://0.0.0.0/article",
    "https://192.0.0.8/article",
    "https://192.0.0.11/article",
    "https://192.0.2.1/article",
    "https://192.88.99.2/article",
    "https://100.64.0.1/article",
    "https://224.0.0.1/article",
    "https://[::1]/article",
    "https://[fe80::1]/article",
    "https://[fec0::1]/article",
    "https://[feff:ffff:ffff:ffff:ffff:ffff:ffff:ffff]/article",
    "https://[fc00::1]/article",
    "https://[ff02::1]/article",
    "https://[64:ff9b:1::1]/article",
    "https://[2001:2::1]/article",
    "https://[2002:7f00:1::]/article",
    "https://127.1/article",
    "https://2130706433/article",
    "https://0x7f000001/article",
    "https://017700000001/article",
    "https://127。0。0。1/article",
    "https://127．0．0．1/article",
    "https://127｡0｡0｡1/article",
    "https://xn--a.com/article",
    "https://xn--abc.com/article",
    "https://xn--0.com/article",
)
PUBLIC_URLS = (
    "https://www.openai.com/article",
    "https://xn--bcher-kva.de/article",
    "https://8.8.8.8/article",
    "https://192.0.0.9/article",
    "https://192.0.0.10/article",
    "https://[2001:1::1]/article",
    "https://[2001:1::2]/article",
    "https://[2001:3::1]/article",
    "https://[2001:4:112::1]/article",
    "https://[2001:20::1]/article",
    "https://[2001:30::1]/article",
    "https://[2606:4700:4700::1111]/article",
)
SENSITIVE_PARAMETER_KEYS = (
    "token",
    "access_token",
    "refresh_token",
    "id_token",
    "api_key",
    "apikey",
    "key",
    "signature",
    "x-amz-signature",
    "x-amz-credential",
    "x-amz-security-token",
    "x-goog-signature",
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
)


def item(item_id: str, published_at: str) -> dict:
    return {
        "id": item_id,
        "title": f"Title {item_id}",
        "title_en": f"English title {item_id}",
        "permalink": f"https://aihot.virxact.com/items/{item_id}",
        "url": f"https://example.com/{item_id}",
        "source": "Example",
        "publishedAt": published_at,
        "summary": f"Summary {item_id}",
        "category": "industry",
        "score": 8,
        "selected": True,
        "attribution": {
            "source": "AI HOT",
            "canonical": f"https://aihot.virxact.com/items/{item_id}",
        },
    }


def terminal_page(*items: dict) -> dict:
    return {
        "count": len(items),
        "hasNext": False,
        "nextCursor": None,
        "items": list(items),
    }


def http_error(url: str, code: int) -> HTTPError:
    return HTTPError(
        url,
        code,
        "upstream error",
        {},
        io.BytesIO(b'{"requestId":"must-not-leak"}'),
    )


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.read_sizes = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.closed = True
        return False

    def read(self, size: int) -> bytes:
        self.read_sizes.append(size)
        return self.body[:size]


class FakeOpener:
    def __init__(
        self,
        response: FakeResponse | None = None,
        error: BaseException | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls = []

    def open(self, request: Request, *, timeout: float):
        self.calls.append((request, timeout))
        if self.error is not None:
            raise self.error
        return self.response


class AihotPaginationTests(unittest.TestCase):
    def test_collection_limits_have_safe_defaults(self) -> None:
        self.assertEqual(aihot.MAX_PAGES, 25)
        self.assertEqual(aihot.MAX_ITEMS, 2500)

    def test_rejects_unique_cursor_pagination_beyond_page_limit(
        self,
    ) -> None:
        calls = []

        def request(cursor):
            calls.append(cursor)
            page_number = len(calls)
            return {
                "count": 1,
                "hasNext": True,
                "nextCursor": f"cursor-{page_number + 1}",
                "items": [
                    item(
                        f"a{page_number}",
                        "2026-07-23T00:00:00Z",
                    )
                ],
            }

        with self.assertRaisesRegex(AihotIncomplete, "^page_limit$"):
            fetch_all_items(
                request,
                since=WINDOW_START,
                sleep=lambda _: None,
                max_pages=3,
            )

        self.assertEqual(calls, [None, "cursor-2", "cursor-3"])

    def test_page_limit_precedes_next_cursor_validation(self) -> None:
        calls = []

        with self.assertRaisesRegex(AihotIncomplete, "^page_limit$"):
            fetch_all_items(
                lambda cursor: (
                    calls.append(cursor)
                    or {
                        "count": 0,
                        "hasNext": True,
                        "nextCursor": None,
                        "items": [],
                    }
                ),
                since=WINDOW_START,
                sleep=lambda _: None,
                max_pages=1,
            )

        self.assertEqual(calls, [None])

    def test_accepts_terminal_page_exactly_at_page_limit(self) -> None:
        calls = []

        def request(cursor):
            calls.append(cursor)
            page_number = len(calls)
            if page_number == 3:
                return terminal_page(
                    item("a3", "2026-07-23T00:00:00Z")
                )
            return {
                "count": 1,
                "hasNext": True,
                "nextCursor": f"cursor-{page_number + 1}",
                "items": [
                    item(
                        f"a{page_number}",
                        "2026-07-23T00:00:00Z",
                    )
                ],
            }

        result = fetch_all_items(
            request,
            since=WINDOW_START,
            sleep=lambda _: None,
            max_pages=3,
        )

        self.assertEqual(result.page_count, 3)
        self.assertEqual(
            [value["id"] for value in result.items],
            ["a1", "a2", "a3"],
        )
        self.assertEqual(calls, [None, "cursor-2", "cursor-3"])

    def test_rejects_items_beyond_item_limit(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "^item_limit$"):
            fetch_all_items(
                lambda cursor: terminal_page(
                    item("a1", "2026-07-23T00:00:00Z"),
                    item("a2", "2026-07-23T00:00:00Z"),
                    item("a3", "2026-07-23T00:00:00Z"),
                ),
                since=WINDOW_START,
                sleep=lambda _: None,
                max_items=2,
            )

    def test_accepts_items_exactly_at_item_limit(self) -> None:
        result = fetch_all_items(
            lambda cursor: terminal_page(
                item("a1", "2026-07-23T00:00:00Z"),
                item("a2", "2026-07-23T00:00:00Z"),
            ),
            since=WINDOW_START,
            sleep=lambda _: None,
            max_items=2,
        )

        self.assertEqual(
            [value["id"] for value in result.items],
            ["a1", "a2"],
        )

    def test_rejects_invalid_collection_limits_before_request(self) -> None:
        invalid_limits = (None, True, False, 0, -1, 1.5, "1")
        for parameter in ("max_pages", "max_items"):
            for invalid in invalid_limits:
                with self.subTest(parameter=parameter, invalid=invalid):
                    calls = []
                    limits = {parameter: invalid}

                    with self.assertRaisesRegex(
                        AihotIncomplete,
                        "^limit_contract$",
                    ):
                        fetch_all_items(
                            lambda cursor: (
                                calls.append(cursor)
                                or terminal_page()
                            ),
                            since=WINDOW_START,
                            sleep=lambda _: None,
                            **limits,
                        )

                    self.assertEqual(calls, [])

    def test_fetches_until_explicit_terminal_page(self) -> None:
        pages = {
            None: {
                "count": 2,
                "hasNext": True,
                "nextCursor": "cursor-2",
                "items": [
                    item("a1", "2026-07-23T01:00:00Z"),
                    item("a2", "2026-07-23T00:30:00Z"),
                ],
            },
            "cursor-2": terminal_page(
                item("a3", "2026-07-23T00:00:00Z")
            ),
        }
        calls = []
        sleeps = []

        def request(cursor):
            calls.append(cursor)
            return pages[cursor]

        result = fetch_all_items(
            request,
            since=WINDOW_START,
            sleep=sleeps.append,
        )

        self.assertEqual(calls, [None, "cursor-2"])
        self.assertEqual(sleeps, [1.0])
        self.assertEqual(
            [value["id"] for value in result.items],
            ["a1", "a2", "a3"],
        )
        self.assertEqual(result.page_count, 2)
        self.assertEqual(result.status, "live")

    def test_rejects_cursor_loop(self) -> None:
        def request(cursor):
            return {
                "count": 1,
                "hasNext": True,
                "nextCursor": "same",
                "items": [
                    item(
                        "a1" if cursor is None else "a2",
                        "2026-07-23T00:00:00Z",
                    )
                ],
            }

        with self.assertRaisesRegex(AihotIncomplete, "cursor_loop"):
            fetch_all_items(
                request,
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_silent_first_page_reset(self) -> None:
        first = {
            "count": 1,
            "hasNext": True,
            "nextCursor": "cursor-2",
            "items": [item("a1", "2026-07-23T00:00:00Z")],
        }

        with self.assertRaisesRegex(AihotIncomplete, "duplicate_item"):
            fetch_all_items(
                lambda cursor: first,
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_inconsistent_terminal_contract(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "terminal_contract"):
            fetch_all_items(
                lambda cursor: {
                    "count": 0,
                    "hasNext": False,
                    "nextCursor": "unexpected",
                    "items": [],
                },
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_terminal_page_missing_explicit_next_cursor(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "terminal_contract"):
            fetch_all_items(
                lambda cursor: {
                    "count": 0,
                    "hasNext": False,
                    "items": [],
                },
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_item_before_window(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "outside_window"):
            fetch_all_items(
                lambda cursor: terminal_page(
                    item("old", "2026-07-21T23:59:59Z")
                ),
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_non_list_items(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "page_contract"):
            fetch_all_items(
                lambda cursor: {
                    "count": 0,
                    "hasNext": False,
                    "nextCursor": None,
                    "items": {},
                },
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_boolean_or_mismatched_count(self) -> None:
        for count in (True, 0):
            with self.subTest(count=count):
                with self.assertRaisesRegex(
                    AihotIncomplete,
                    "page_contract",
                ):
                    fetch_all_items(
                        lambda cursor, count=count: {
                            "count": count,
                            "hasNext": False,
                            "nextCursor": None,
                            "items": [
                                item("a1", "2026-07-23T00:00:00Z")
                            ],
                        },
                        since=WINDOW_START,
                        sleep=lambda _: None,
                    )

    def test_rejects_missing_required_item_field(self) -> None:
        value = item("a1", "2026-07-23T00:00:00Z")
        del value["category"]

        with self.assertRaisesRegex(AihotIncomplete, "item_contract"):
            fetch_all_items(
                lambda cursor: terminal_page(value),
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_non_boolean_has_next(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "cursor_contract"):
            fetch_all_items(
                lambda cursor: {
                    "count": 0,
                    "hasNext": 0,
                    "nextCursor": None,
                    "items": [],
                },
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_invalid_published_time(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "time_format"):
            fetch_all_items(
                lambda cursor: terminal_page(
                    item("a1", "not-a-timestamp")
                ),
                since=WINDOW_START,
                sleep=lambda _: None,
            )

    def test_rejects_naive_since(self) -> None:
        with self.assertRaisesRegex(AihotIncomplete, "since_timezone"):
            fetch_all_items(
                lambda cursor: terminal_page(),
                since=datetime(2026, 7, 22),
                sleep=lambda _: None,
            )


class AihotRequestTests(unittest.TestCase):
    def assert_fixed_item_query(
        self,
        url: str,
        *,
        since: str = "2026-07-22T00:00:00Z",
        cursor: str | None = None,
    ) -> None:
        parsed = urlsplit(url)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "aihot.virxact.com")
        self.assertEqual(parsed.path, "/api/public/items")
        expected = {
            "mode": ["selected"],
            "since": [since],
            "take": ["100"],
        }
        if cursor is not None:
            expected["cursor"] = [cursor]
        self.assertEqual(parse_qs(parsed.query), expected)

    def test_items_request_uses_only_fixed_parameters(self) -> None:
        calls = []
        page = terminal_page(item("a1", "2026-07-23T00:00:00Z"))

        def request_json(url):
            calls.append(url)
            return page

        result = aihot.request_items_page(
            request_json,
            WINDOW_START,
            None,
            sleep=lambda _: None,
        )

        self.assertIs(result, page)
        self.assertEqual(len(calls), 1)
        self.assert_fixed_item_query(calls[0])

    def test_items_request_carries_cursor_without_relaxing_parameters(self) -> None:
        calls = []

        aihot.request_items_page(
            lambda url: calls.append(url) or terminal_page(),
            WINDOW_START,
            "cursor-2",
            sleep=lambda _: None,
        )

        self.assertEqual(len(calls), 1)
        self.assert_fixed_item_query(calls[0], cursor="cursor-2")

    def test_retries_each_5xx_once_with_the_identical_url(self) -> None:
        for code in (500, 567, 599):
            with self.subTest(code=code):
                calls = []
                sleeps = []
                page = terminal_page(
                    item("a1", "2026-07-23T00:00:00Z")
                )

                def request_json(url):
                    calls.append(url)
                    if len(calls) == 1:
                        raise http_error(url, code)
                    return page

                result = aihot.request_items_page(
                    request_json,
                    WINDOW_START,
                    None,
                    sleep=sleeps.append,
                )

                self.assertIs(result, page)
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[0], calls[1])
                self.assertEqual(sleeps, [1.0])
                self.assert_fixed_item_query(calls[0])

    def test_retries_network_failures_once_with_the_identical_url(self) -> None:
        failures = (
            lambda: TimeoutError("timed out"),
            lambda: URLError("offline"),
            lambda: OSError("socket failed"),
        )
        for make_error in failures:
            with self.subTest(error=type(make_error()).__name__):
                calls = []
                sleeps = []

                def request_json(url):
                    calls.append(url)
                    if len(calls) == 1:
                        raise make_error()
                    return {"ok": True}

                result = aihot.request_json_with_retry(
                    request_json,
                    "https://example.test/fixed?mode=selected&take=100",
                    sleep=sleeps.append,
                )

                self.assertEqual(result, {"ok": True})
                self.assertEqual(
                    calls,
                    [
                        "https://example.test/fixed?mode=selected&take=100",
                        "https://example.test/fixed?mode=selected&take=100",
                    ],
                )
                self.assertEqual(sleeps, [1.0])

    def test_continuous_retryable_failure_stops_after_two_attempts(self) -> None:
        calls = []

        def request_json(url):
            calls.append(url)
            raise TimeoutError("contains private details")

        with self.assertRaisesRegex(AihotIncomplete, "^timeout$"):
            aihot.request_json_with_retry(
                request_json,
                "https://example.test/fixed",
                sleep=lambda _: None,
            )

        self.assertEqual(
            calls,
            [
                "https://example.test/fixed",
                "https://example.test/fixed",
            ],
        )

    def test_400_and_403_fail_immediately_without_parameter_broadening(
        self,
    ) -> None:
        for code in (400, 403):
            with self.subTest(code=code):
                calls = []

                def request_json(url):
                    calls.append(url)
                    raise http_error(url, code)

                with self.assertRaisesRegex(
                    AihotIncomplete,
                    f"^http_{code}$",
                ):
                    aihot.request_items_page(
                        request_json,
                        WINDOW_START,
                        "cursor-2",
                        sleep=lambda _: None,
                    )

                self.assertEqual(len(calls), 1)
                self.assert_fixed_item_query(calls[0], cursor="cursor-2")

    def test_retry_entry_requires_a_dictionary_response(self) -> None:
        with self.assertRaisesRegex(
            AihotIncomplete,
            "^response_contract$",
        ):
            aihot.request_json_with_retry(
                lambda url: [],
                "https://example.test/fixed",
                sleep=lambda _: None,
            )

    def test_items_request_rejects_naive_since_before_request(self) -> None:
        calls = []

        with self.assertRaisesRegex(AihotIncomplete, "since_timezone"):
            aihot.request_items_page(
                lambda url: calls.append(url) or terminal_page(),
                datetime(2026, 7, 22),
                None,
                sleep=lambda _: None,
            )

        self.assertEqual(calls, [])


class RequestJsonUrlTests(unittest.TestCase):
    def test_uses_fixed_get_headers_timeout_and_utf8_json(self) -> None:
        body = json.dumps(
            {"message": "完整"},
            ensure_ascii=False,
        ).encode("utf-8")
        response = FakeResponse(body)
        opener = FakeOpener(response=response)

        with patch(
            "content_radar_feed.aihot.build_opener",
            return_value=opener,
        ) as mocked_build_opener:
            result = aihot.request_json_url(
                "https://example.test/data",
                timeout=17,
            )

        self.assertEqual(result, {"message": "完整"})
        self.assertEqual(len(opener.calls), 1)
        request, timeout = opener.calls[0]
        self.assertEqual(request.full_url, "https://example.test/data")
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(
            request.get_header("User-agent"),
            "content-radar-cloud/1.0",
        )
        self.assertEqual(
            request.get_header("Accept"),
            "application/json",
        )
        self.assertEqual(timeout, 17)
        self.assertEqual(
            response.read_sizes,
            [aihot.MAX_RESPONSE_BYTES + 1],
        )
        self.assertTrue(response.closed)

        handler = mocked_build_opener.call_args.args[0]
        self.assertIsInstance(handler, HTTPRedirectHandler)
        for code in (301, 302, 307, 308):
            with self.subTest(code=code):
                self.assertIsNone(
                    handler.redirect_request(
                        request,
                        None,
                        code,
                        "redirect",
                        {},
                        "https://internal.example/private",
                    )
                )

    def test_rejects_redirects_without_retry_and_closes_http_error(
        self,
    ) -> None:
        for code in (301, 302, 307, 308):
            with self.subTest(code=code):
                error = http_error(
                    "https://example.test/private-url",
                    code,
                )
                response_body = error.fp
                opener = FakeOpener(error=error)

                with patch(
                    "content_radar_feed.aihot.build_opener",
                    return_value=opener,
                ):
                    with self.assertRaises(AihotIncomplete) as raised:
                        aihot.request_json_with_retry(
                            aihot.request_json_url,
                            "https://example.test/data",
                            sleep=lambda _: self.fail(
                                "redirect must not retry"
                            ),
                        )

                self.assertEqual(str(raised.exception), f"http_{code}")
                self.assertEqual(len(opener.calls), 1)
                self.assertTrue(response_body.closed)
                self.assertNotIn("private-url", str(raised.exception))
                self.assertNotIn("requestId", str(raised.exception))

    def test_rejects_response_larger_than_byte_limit(self) -> None:
        secret = b"must-not-leak"
        prefix = b'{"secret":"' + secret + b'"}'
        body = prefix + b" " * (
            aihot.MAX_RESPONSE_BYTES + 1 - len(prefix)
        )
        response = FakeResponse(body)

        with patch(
            "content_radar_feed.aihot.build_opener",
            return_value=FakeOpener(response=response),
        ):
            with self.assertRaises(AihotIncomplete) as raised:
                aihot.request_json_with_retry(
                    aihot.request_json_url,
                    "https://example.test/data",
                    sleep=lambda _: self.fail(
                        "oversized response must not retry"
                    ),
                )

        self.assertEqual(str(raised.exception), "response_too_large")
        self.assertNotIn(secret.decode("ascii"), str(raised.exception))
        self.assertEqual(
            response.read_sizes,
            [aihot.MAX_RESPONSE_BYTES + 1],
        )
        self.assertTrue(response.closed)

    def test_accepts_json_response_exactly_at_byte_limit(self) -> None:
        prefix = b'{"ok":true}'
        body = prefix + b" " * (
            aihot.MAX_RESPONSE_BYTES - len(prefix)
        )
        response = FakeResponse(body)

        with patch(
            "content_radar_feed.aihot.build_opener",
            return_value=FakeOpener(response=response),
        ):
            result = aihot.request_json_url(
                "https://example.test/data"
            )

        self.assertEqual(result, {"ok": True})
        self.assertEqual(
            response.read_sizes,
            [aihot.MAX_RESPONSE_BYTES + 1],
        )

    def test_rejects_invalid_json_without_leaking_the_body(self) -> None:
        secret = "private-request-id"
        response = FakeResponse(
            f'{{"requestId":"{secret}"'.encode("utf-8")
        )

        with patch(
            "content_radar_feed.aihot.build_opener",
            return_value=FakeOpener(response=response),
        ):
            with self.assertRaises(AihotIncomplete) as raised:
                aihot.request_json_url("https://example.test/data")

        self.assertEqual(str(raised.exception), "invalid_json")
        self.assertNotIn(secret, str(raised.exception))

    def test_rejects_non_dictionary_json_response(self) -> None:
        with patch(
            "content_radar_feed.aihot.build_opener",
            return_value=FakeOpener(response=FakeResponse(b"[]")),
        ):
            with self.assertRaisesRegex(
                AihotIncomplete,
                "^response_contract$",
            ):
                aihot.request_json_url("https://example.test/data")

    def test_converts_http_error_without_leaking_response_body(self) -> None:
        error = http_error("https://example.test/data", 403)
        response_body = error.fp
        with patch(
            "content_radar_feed.aihot.build_opener",
            return_value=FakeOpener(error=error),
        ):
            with self.assertRaises(AihotIncomplete) as raised:
                aihot.request_json_url("https://example.test/data")

        self.assertEqual(str(raised.exception), "http_403")
        self.assertNotIn("requestId", str(raised.exception))
        self.assertTrue(response_body.closed)


class AihotProjectionTests(unittest.TestCase):
    def test_keeps_sensitive_query_keys_compatibility_name(self) -> None:
        self.assertEqual(
            aihot.SENSITIVE_QUERY_KEYS,
            aihot.SENSITIVE_PARAMETER_KEYS,
        )

    def test_projects_exact_public_keys_without_mutating_upstream(self) -> None:
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["private"] = "must not be published"
        upstream["attribution"]["requestId"] = "must not be published"
        original = copy.deepcopy(upstream)

        projected = aihot.project_public_item(upstream)

        expected_keys = {
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
        self.assertEqual(aihot.PUBLIC_ITEM_KEYS, expected_keys)
        self.assertEqual(set(projected), expected_keys)
        self.assertEqual(
            projected["published_at"],
            upstream["publishedAt"],
        )
        self.assertEqual(projected["url"], upstream["url"])
        self.assertEqual(
            projected["attribution"],
            {
                "source": "AI HOT",
                "canonical": "https://aihot.virxact.com/items/a1",
            },
        )
        self.assertIsNot(projected, upstream)
        self.assertIsNot(projected["attribution"], upstream["attribution"])
        self.assertEqual(upstream, original)

    def test_converts_published_time_to_utc(self) -> None:
        upstream = item("a1", "2026-07-23T08:00:00+08:00")

        projected = aihot.project_public_item(upstream)

        self.assertEqual(
            projected["published_at"],
            "2026-07-23T00:00:00Z",
        )

    def test_redacts_sensitive_query_keys_from_all_url_fields(self) -> None:
        key_variants = list(SENSITIVE_PARAMETER_KEYS)
        key_variants.extend(
            key.upper()
            for key in SENSITIVE_PARAMETER_KEYS
        )
        key_variants.extend(
            key.replace("_", "-")
            for key in SENSITIVE_PARAMETER_KEYS
            if "_" in key
        )
        key_variants.extend(
            key.replace("-", "_")
            for key in SENSITIVE_PARAMETER_KEYS
            if "-" in key
        )
        key_variants.extend(("%74oken", "%61ccess_token"))

        for key in key_variants:
            with self.subTest(key=key):
                sensitive_url = (
                    f"https://example.com/article?{key}=private-value"
                )
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["url"] = sensitive_url

                projected = aihot.project_public_item(upstream)

                self.assertEqual(projected["id"], "a1")
                self.assertIsNone(projected["url"])

                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["permalink"] = sensitive_url
                with self.assertRaises(AihotIncomplete) as raised:
                    aihot.project_public_item(upstream)
                self.assertEqual(
                    str(raised.exception),
                    "permalink_url",
                )
                self.assertNotIn(key, str(raised.exception))
                self.assertNotIn("private-value", str(raised.exception))
                self.assertNotIn(sensitive_url, str(raised.exception))

                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["attribution"]["canonical"] = sensitive_url
                projected = aihot.project_public_item(upstream)
                self.assertIsNone(
                    projected["attribution"]["canonical"]
                )

    def test_redacts_sensitive_fragment_parameters_from_all_url_fields(
        self,
    ) -> None:
        sensitive_urls = (
            "https://example.com/article#access_token=private-value",
            "https://example.com/article#/callback?api_key=private-value",
            "https://example.com/article#%61ccess_token=private-value",
        )
        for sensitive_url in sensitive_urls:
            with self.subTest(sensitive_url=sensitive_url):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["url"] = sensitive_url
                projected = aihot.project_public_item(upstream)
                self.assertIsNone(projected["url"])

                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["permalink"] = sensitive_url
                with self.assertRaises(AihotIncomplete) as raised:
                    aihot.project_public_item(upstream)
                self.assertEqual(
                    str(raised.exception),
                    "permalink_url",
                )
                self.assertNotIn("private-value", str(raised.exception))
                self.assertNotIn(sensitive_url, str(raised.exception))

                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["attribution"]["canonical"] = sensitive_url
                projected = aihot.project_public_item(upstream)
                self.assertIsNone(
                    projected["attribution"]["canonical"]
                )

    def test_redacts_sensitive_parameter_before_fragment_route_query_from_original(
        self,
    ) -> None:
        sensitive_url = (
            "https://example.com/p"
            "#access_token=secret&next=/callback?mode=ok"
        )
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["url"] = sensitive_url

        projected = aihot.project_public_item(upstream)

        self.assertIsNone(projected["url"])

    def test_rejects_sensitive_parameter_before_fragment_route_query_from_permalink(
        self,
    ) -> None:
        sensitive_url = (
            "https://example.com/p"
            "#access_token=secret&next=/callback?mode=ok"
        )
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["permalink"] = sensitive_url

        with self.assertRaises(AihotIncomplete) as raised:
            aihot.project_public_item(upstream)

        self.assertEqual(str(raised.exception), "permalink_url")
        self.assertNotIn(sensitive_url, str(raised.exception))
        self.assertNotIn("secret", str(raised.exception))
        self.assertNotIn("access_token", str(raised.exception))

    def test_redacts_sensitive_parameter_before_fragment_route_query_from_canonical(
        self,
    ) -> None:
        sensitive_url = (
            "https://example.com/p"
            "#access_token=secret&next=/callback?mode=ok"
        )
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["attribution"]["canonical"] = sensitive_url

        projected = aihot.project_public_item(upstream)

        self.assertIsNone(projected["attribution"]["canonical"])

    def test_preserves_non_sensitive_fragment_before_route_query(
        self,
    ) -> None:
        ordinary_url = (
            "https://example.com/p"
            "#section=overview&next=/callback?mode=ok"
        )
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["url"] = ordinary_url
        upstream["permalink"] = ordinary_url
        upstream["attribution"]["canonical"] = ordinary_url

        projected = aihot.project_public_item(upstream)

        self.assertEqual(projected["url"], ordinary_url)
        self.assertEqual(projected["permalink"], ordinary_url)
        self.assertEqual(
            projected["attribution"]["canonical"],
            ordinary_url,
        )

    def test_preserves_non_credential_query_and_fragment_keys(
        self,
    ) -> None:
        ordinary_urls = (
            "https://example.com/article?monkey=capuchin",
            "https://example.com/article?hockey=ice",
            "https://example.com/article?session_type=preview",
            "https://example.com/article#signature_style=compact",
            "https://example.com/article#/callback?session_type=preview",
        )
        for ordinary_url in ordinary_urls:
            with self.subTest(ordinary_url=ordinary_url):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["url"] = ordinary_url
                upstream["permalink"] = ordinary_url
                upstream["attribution"]["canonical"] = ordinary_url

                projected = aihot.project_public_item(upstream)

                self.assertEqual(projected["url"], ordinary_url)
                self.assertEqual(projected["permalink"], ordinary_url)
                self.assertEqual(
                    projected["attribution"]["canonical"],
                    ordinary_url,
                )

    def test_preserves_ordinary_https_url(self) -> None:
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["url"] = (
            "https://news.example.com/article?topic=ai&language=zh"
        )

        projected = aihot.project_public_item(upstream)

        self.assertEqual(projected["url"], upstream["url"])

    def test_redacts_http_original_url_without_dropping_item(self) -> None:
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["url"] = "http://news.example.com/article"

        projected = aihot.project_public_item(upstream)

        self.assertEqual(projected["id"], "a1")
        self.assertIsNone(projected["url"])

    def test_rejects_http_permalink_without_leaking_url(self) -> None:
        unsafe_url = "http://aihot.virxact.com/items/a1"
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["permalink"] = unsafe_url

        with self.assertRaises(AihotIncomplete) as raised:
            aihot.project_public_item(upstream)

        self.assertEqual(str(raised.exception), "permalink_url")
        self.assertNotIn(unsafe_url, str(raised.exception))

    def test_redacts_http_attribution_canonical(self) -> None:
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["attribution"]["canonical"] = (
            "http://aihot.virxact.com/items/a1"
        )

        projected = aihot.project_public_item(upstream)

        self.assertEqual(
            projected["attribution"],
            {"source": "AI HOT", "canonical": None},
        )

    def test_redacts_non_http_original_url_without_dropping_item(self) -> None:
        upstream = item("a1", "2026-07-23T00:00:00Z")
        upstream["url"] = "file:///Users/private/source"

        projected = aihot.project_public_item(upstream)

        self.assertEqual(projected["id"], "a1")
        self.assertIsNone(projected["url"])

    def test_redacts_non_public_original_hosts_without_dropping_item(
        self,
    ) -> None:
        for unsafe_url in NON_PUBLIC_URLS:
            with self.subTest(unsafe_url=unsafe_url):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["url"] = unsafe_url

                projected = aihot.project_public_item(upstream)

                self.assertEqual(projected["id"], "a1")
                self.assertIsNone(projected["url"])

    def test_rejects_non_public_permalink_hosts_without_leaking_url(
        self,
    ) -> None:
        for unsafe_url in NON_PUBLIC_URLS:
            with self.subTest(unsafe_url=unsafe_url):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["permalink"] = unsafe_url

                with self.assertRaises(AihotIncomplete) as raised:
                    aihot.project_public_item(upstream)

                self.assertEqual(str(raised.exception), "permalink_url")
                self.assertNotIn(unsafe_url, str(raised.exception))

    def test_redacts_non_public_attribution_canonical_hosts(self) -> None:
        for unsafe_url in NON_PUBLIC_URLS:
            with self.subTest(unsafe_url=unsafe_url):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["attribution"]["canonical"] = unsafe_url

                projected = aihot.project_public_item(upstream)

                self.assertEqual(projected["id"], "a1")
                self.assertEqual(
                    projected["attribution"],
                    {"source": "AI HOT", "canonical": None},
                )

    def test_preserves_public_domain_and_global_ip_hosts(self) -> None:
        for public_url in PUBLIC_URLS:
            with self.subTest(public_url=public_url):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["url"] = public_url
                upstream["permalink"] = public_url
                upstream["attribution"]["canonical"] = public_url

                projected = aihot.project_public_item(upstream)

                self.assertEqual(projected["url"], public_url)
                self.assertEqual(projected["permalink"], public_url)
                self.assertEqual(
                    projected["attribution"]["canonical"],
                    public_url,
                )

    def test_rejects_non_public_or_sensitive_permalink(self) -> None:
        invalid_values = (
            "javascript:alert(1)",
            "/relative",
            "https:///missing-host",
            "https://user:password@example.com/private",
            "https://aihot.virxact.com/items/a1?Token=private",
            "https://example.com\n.evil.test/a",
            "https://exa mple.com/a",
        )
        for permalink in invalid_values:
            with self.subTest(permalink=permalink):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream["permalink"] = permalink

                with self.assertRaisesRegex(
                    AihotIncomplete,
                    "^permalink_url$",
                ):
                    aihot.project_public_item(upstream)

    def test_rejects_invalid_optional_field_types(self) -> None:
        invalid_values = (
            ("title_en", 3),
            ("url", 3),
            ("summary", {}),
            ("score", True),
            ("selected", "true"),
            ("attribution", []),
        )
        for field, invalid in invalid_values:
            with self.subTest(field=field):
                upstream = item("a1", "2026-07-23T00:00:00Z")
                upstream[field] = invalid

                with self.assertRaisesRegex(
                    AihotIncomplete,
                    "^item_contract$",
                ):
                    aihot.project_public_item(upstream)

    def test_missing_optional_fields_project_as_null_public_fields(self) -> None:
        upstream = item("a1", "2026-07-23T00:00:00Z")
        for field in (
            "title_en",
            "url",
            "summary",
            "score",
            "selected",
            "attribution",
        ):
            del upstream[field]

        projected = aihot.project_public_item(upstream)

        self.assertEqual(set(projected), aihot.PUBLIC_ITEM_KEYS)
        self.assertIsNone(projected["title_en"])
        self.assertIsNone(projected["url"])
        self.assertIsNone(projected["summary"])
        self.assertIsNone(projected["score"])
        self.assertIsNone(projected["selected"])
        self.assertEqual(
            projected["attribution"],
            {"source": None, "canonical": None},
        )


class FetchAihotTests(unittest.TestCase):
    def test_fetches_version_once_and_all_fixed_query_pages(self) -> None:
        now = datetime(
            2026,
            7,
            24,
            8,
            30,
            tzinfo=timezone(timedelta(hours=8)),
        )
        calls = []
        sleeps = []

        def request_json(url):
            calls.append(url)
            parsed = urlsplit(url)
            if parsed.path.endswith("/version"):
                return {
                    "apiVersion": "1.4.0",
                    "requestId": "not public",
                }
            cursor = parse_qs(parsed.query).get("cursor", [None])[0]
            if cursor is None:
                return {
                    "count": 1,
                    "hasNext": True,
                    "nextCursor": "cursor-2",
                    "items": [
                        item("a1", "2026-07-23T01:00:00Z")
                    ],
                }
            self.assertEqual(cursor, "cursor-2")
            return terminal_page(
                item("a2", "2026-07-23T00:30:00Z")
            )

        result = aihot.fetch_aihot(
            now=now,
            request_json=request_json,
            sleep=sleeps.append,
        )

        version_url = f"{aihot.BASE_URL}/version"
        self.assertEqual(calls.count(version_url), 1)
        item_urls = [
            url
            for url in calls
            if urlsplit(url).path.endswith("/items")
        ]
        self.assertEqual(len(item_urls), 2)
        expected_since = "2026-07-23T00:30:00Z"
        AihotRequestTests().assert_fixed_item_query(
            item_urls[0],
            since=expected_since,
        )
        AihotRequestTests().assert_fixed_item_query(
            item_urls[1],
            since=expected_since,
            cursor="cursor-2",
        )
        self.assertEqual(sleeps, [1.0])
        self.assertEqual(result["status"], "live")
        self.assertEqual(result["api_version"], "1.4.0")
        self.assertEqual(result["page_count"], 2)
        self.assertEqual(result["window_start"], expected_since)
        self.assertEqual(
            [value["id"] for value in result["items"]],
            ["a1", "a2"],
        )
        self.assertTrue(
            all(
                set(value) == aihot.PUBLIC_ITEM_KEYS
                for value in result["items"]
            )
        )

    def test_rejects_naive_now_before_request(self) -> None:
        calls = []

        with self.assertRaisesRegex(AihotIncomplete, "^now_timezone$"):
            aihot.fetch_aihot(
                now=datetime(2026, 7, 24, 8, 30),
                request_json=lambda url: calls.append(url) or {},
                sleep=lambda _: None,
            )

        self.assertEqual(calls, [])

    def test_rejects_item_published_after_window_end(self) -> None:
        def request_json(url):
            if urlsplit(url).path.endswith("/version"):
                return {"apiVersion": "1.4.0"}
            return terminal_page(
                item("future", "2026-07-24T00:00:01Z")
            )

        with self.assertRaisesRegex(AihotIncomplete, "^outside_window$"):
            aihot.fetch_aihot(
                now=datetime(
                    2026,
                    7,
                    24,
                    tzinfo=timezone.utc,
                ),
                request_json=request_json,
                sleep=lambda _: None,
            )

    def test_requires_non_empty_string_api_version(self) -> None:
        for invalid in (None, "", True, {}):
            with self.subTest(invalid=invalid):
                calls = []

                def request_json(url):
                    calls.append(url)
                    return {"apiVersion": invalid}

                with self.assertRaisesRegex(
                    AihotIncomplete,
                    "^version_contract$",
                ):
                    aihot.fetch_aihot(
                        now=datetime(
                            2026,
                            7,
                            24,
                            tzinfo=timezone.utc,
                        ),
                        request_json=request_json,
                        sleep=lambda _: None,
                    )

                self.assertEqual(
                    calls,
                    [f"{aihot.BASE_URL}/version"],
                )


if __name__ == "__main__":
    unittest.main()
