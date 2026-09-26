"""Offline checks for bounded, read-only status responses."""

import importlib.util
import asyncio
from pathlib import Path
import sys
import types
import unittest


aiohttp = types.ModuleType("aiohttp")
aiohttp.ClientError = type("ClientError", (Exception,), {})
aiohttp.ClientResponseError = type("ClientResponseError", (aiohttp.ClientError,), {})
sys.modules["aiohttp"] = aiohttp
sys.modules["homeassistant"] = types.ModuleType("homeassistant")
sys.modules["homeassistant.helpers"] = types.ModuleType("homeassistant.helpers")
client_module = types.ModuleType("homeassistant.helpers.aiohttp_client")
client_module.async_get_clientsession = lambda hass: None
sys.modules["homeassistant.helpers.aiohttp_client"] = client_module

source = Path(__file__).resolve().parents[1] / "custom_components/paperclip_voice/client.py"
spec = importlib.util.spec_from_file_location("paperclip_voice_client", source)
client = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = client
spec.loader.exec_module(client)


class StatusSummaryTests(unittest.TestCase):
    def test_assignee_status_and_link(self):
        result = client.summarize_status(
            [
                {"identifier": "HOM-9", "title": "Check backup", "status": "in_progress", "assigneeAgentId": "agent-1"},
                {"identifier": "HOM-10", "title": "Await window", "status": "blocked"},
            ],
            [{"id": "agent-1", "name": "Systems Maintainer"}],
            "https://paperclip.example",
        )
        self.assertEqual(result["first_page_counts"]["blocked"], 1)
        self.assertEqual(result["working_now"][0]["assignee"], "Systems Maintainer")
        self.assertEqual(result["working_now"][0]["link"], "https://paperclip.example/HOM/issues/HOM-9")
        self.assertFalse(result["more_pages_possible"])

    def test_limit_and_unexpected_response(self):
        issues = [
            {"identifier": f"HOM-{number}", "title": f"Task {number}", "status": "in_progress"}
            for number in range(100)
        ]
        result = client.summarize_status(issues, [], "https://paperclip.example")
        self.assertEqual(len(result["working_now"]), 12)
        self.assertTrue(result["more_pages_possible"])
        self.assertEqual(result["first_page_counts"]["in_progress"], 100)
        self.assertEqual(result["first_page_working_now"], 100)
        with self.assertRaises(client.PaperclipError):
            client.summarize_status({"error": "failed"}, [], "https://paperclip.example")

    def test_wrong_origin_rejected_before_request(self):
        config = client.PaperclipConfig("http://paperclip.nyvej.it", "company", "secret")
        with self.assertRaisesRegex(client.PaperclipError, "settings are invalid"):
            asyncio.run(client._get_json(None, config, "companies/company/agents"))

    def test_redirect_rejected_without_following(self):
        class Response:
            status = 302

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

        class Session:
            def get(self, url, **kwargs):
                self.url = url
                self.kwargs = kwargs
                return Response()

        session = Session()
        client.async_get_clientsession = lambda hass: session
        config = client.PaperclipConfig(client.PAPERCLIP_ORIGIN, "company", "secret")
        with self.assertRaisesRegex(client.PaperclipError, "could not provide"):
            asyncio.run(client._get_json(None, config, "companies/company/agents"))
        self.assertEqual(session.url, "https://paperclip.nyvej.it/api/companies/company/agents")
        self.assertFalse(session.kwargs["allow_redirects"])

    def test_authentication_failure_redacts_credential(self):
        class Unauthorized(client.ClientResponseError):
            status = 401

        class Response:
            status = 401

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            def raise_for_status(self):
                raise Unauthorized("credential-must-not-appear")

        class Session:
            def get(self, url, **kwargs):
                return Response()

        client.async_get_clientsession = lambda hass: Session()
        config = client.PaperclipConfig(client.PAPERCLIP_ORIGIN, "company", "credential-must-not-appear")
        with self.assertRaises(client.PaperclipError) as raised:
            asyncio.run(client._get_json(None, config, "companies/company/agents"))
        self.assertNotIn(config.token, str(raised.exception))
        self.assertIn("credential", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
