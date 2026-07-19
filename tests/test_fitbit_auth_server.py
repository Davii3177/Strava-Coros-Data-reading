import html
import re
import unittest
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock, patch

import fitbit_auth_server as auth_server


def make_handler(path, state_store=None):
    handler = object.__new__(auth_server.Handler)
    handler.path = path
    handler.server = SimpleNamespace(
        oauth_states=state_store or auth_server.OAuthStateStore()
    )
    handler._respond = Mock()
    return handler


def callback_path(**query):
    return "/callback?" + urllib.parse.urlencode(query)


class OAuthStateStoreTests(unittest.TestCase):
    def test_state_expires(self):
        current_time = [100.0]
        store = auth_server.OAuthStateStore(
            ttl_seconds=10,
            clock=lambda: current_time[0],
        )
        state = store.issue()

        current_time[0] = 111.0

        self.assertFalse(store.consume(state))

    def test_state_can_only_be_consumed_once_across_threads(self):
        store = auth_server.OAuthStateStore()
        state = store.issue()

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: store.consume(state), range(8)))

        self.assertEqual(results.count(True), 1)
        self.assertEqual(results.count(False), 7)


class FitbitOAuthHandlerTests(unittest.TestCase):
    def test_connection_page_issues_state_in_authorization_url(self):
        handler = make_handler("/")

        handler.do_GET()

        status, body = handler._respond.call_args.args
        self.assertEqual(status, 200)
        href_match = re.search(r'href="([^"]+)"', body)
        self.assertIsNotNone(href_match)
        authorize_url = html.unescape(href_match.group(1))
        query = urllib.parse.parse_qs(urllib.parse.urlparse(authorize_url).query)
        self.assertEqual(len(query.get("state", [])), 1)
        self.assertTrue(query["state"][0])
        self.assertTrue(handler.server.oauth_states.consume(query["state"][0]))

    def test_callback_rejects_missing_wrong_and_duplicate_state(self):
        cases = []

        missing_store = auth_server.OAuthStateStore()
        cases.append(("missing", missing_store, callback_path(code="code")))

        wrong_store = auth_server.OAuthStateStore()
        wrong_store.issue()
        cases.append(
            ("wrong", wrong_store, callback_path(code="code", state="wrong-state"))
        )

        duplicate_store = auth_server.OAuthStateStore()
        duplicate_state = duplicate_store.issue()
        duplicate_query = urllib.parse.urlencode(
            [("code", "code"), ("state", duplicate_state), ("state", duplicate_state)]
        )
        cases.append(("duplicate", duplicate_store, f"/callback?{duplicate_query}"))

        blank_duplicate_store = auth_server.OAuthStateStore()
        blank_duplicate_state = blank_duplicate_store.issue()
        blank_duplicate_query = urllib.parse.urlencode(
            [("code", "code"), ("state", blank_duplicate_state), ("state", "")]
        )
        cases.append(
            (
                "blank duplicate",
                blank_duplicate_store,
                f"/callback?{blank_duplicate_query}",
            )
        )

        for label, store, path in cases:
            with self.subTest(label=label):
                handler = make_handler(path, store)
                with (
                    patch.object(auth_server.requests, "post") as token_request,
                    patch.object(auth_server, "update_env_refresh_token") as save_token,
                ):
                    handler.do_GET()

                status, body = handler._respond.call_args.args
                self.assertEqual(status, 400)
                self.assertIn("Invalid or expired authorization request", body)
                token_request.assert_not_called()
                save_token.assert_not_called()

    def test_callback_rejects_duplicate_code_and_consumes_valid_state(self):
        store = auth_server.OAuthStateStore()
        state = store.issue()
        query = urllib.parse.urlencode(
            [("code", "authorization-code"), ("code", ""), ("state", state)]
        )
        handler = make_handler(f"/callback?{query}", store)

        with (
            patch.object(auth_server.requests, "post") as token_request,
            patch.object(auth_server, "update_env_refresh_token") as save_token,
        ):
            handler.do_GET()

        status, body = handler._respond.call_args.args
        self.assertEqual(status, 400)
        self.assertIn("Missing code", body)
        self.assertFalse(store.consume(state))
        token_request.assert_not_called()
        save_token.assert_not_called()

    def test_valid_callback_exchanges_once_and_rejects_replay(self):
        store = auth_server.OAuthStateStore()
        state = store.issue()
        path = callback_path(code="authorization-code", state=state)
        token_response = Mock()
        token_response.json.return_value = {
            "refresh_token": "refresh-token",
            "scope": "<b>health scope</b>",
        }

        first_handler = make_handler(path, store)
        replay_handler = make_handler(path, store)
        with (
            patch.object(
                auth_server.requests, "post", return_value=token_response
            ) as token_request,
            patch.object(auth_server, "update_env_refresh_token") as save_token,
            patch("builtins.print") as success_log,
        ):
            first_handler.do_GET()
            replay_handler.do_GET()

        first_status, first_body = first_handler._respond.call_args.args
        self.assertEqual(first_status, 200)
        self.assertIn("&lt;b&gt;health scope&lt;/b&gt;", first_body)
        self.assertNotIn("<b>health scope</b>", first_body)
        replay_status, replay_body = replay_handler._respond.call_args.args
        self.assertEqual(replay_status, 400)
        self.assertIn("Invalid or expired authorization request", replay_body)
        token_request.assert_called_once()
        save_token.assert_called_once_with("refresh-token")
        success_log.assert_called_once_with("Success - refresh token saved to .env.")

    def test_provider_error_is_not_reflected_and_consumes_state(self):
        store = auth_server.OAuthStateStore()
        state = store.issue()
        handler = make_handler(
            callback_path(state=state, error="<script>alert(1)</script>"),
            store,
        )

        with (
            patch.object(auth_server.requests, "post") as token_request,
            patch.object(auth_server, "update_env_refresh_token") as save_token,
        ):
            handler.do_GET()

        status, body = handler._respond.call_args.args
        self.assertEqual(status, 400)
        self.assertIn("Authorization denied", body)
        self.assertNotIn("<script>", body)
        self.assertFalse(store.consume(state))
        token_request.assert_not_called()
        save_token.assert_not_called()

    def test_token_request_failure_is_controlled_and_state_remains_consumed(self):
        store = auth_server.OAuthStateStore()
        state = store.issue()
        path = callback_path(code="authorization-code", state=state)
        handler = make_handler(path, store)

        with (
            patch.object(
                auth_server.requests,
                "post",
                side_effect=auth_server.requests.RequestException("network failed"),
            ) as token_request,
            patch.object(auth_server, "update_env_refresh_token") as save_token,
        ):
            handler.do_GET()

        status, body = handler._respond.call_args.args
        self.assertEqual(status, 502)
        self.assertIn("Token exchange failed", body)
        self.assertFalse(store.consume(state))
        token_request.assert_called_once()
        save_token.assert_not_called()


if __name__ == "__main__":
    unittest.main()
