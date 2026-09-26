"""Offline checks for bounded, read-only status responses."""

import importlib.util
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
        self.assertEqual(result["counts"]["blocked"], 1)
        self.assertEqual(result["working_now"][0]["assignee"], "Systems Maintainer")
        self.assertEqual(result["working_now"][0]["link"], "https://paperclip.example/HOM/issues/HOM-9")
        self.assertFalse(result["truncated"])

    def test_limit_and_unexpected_response(self):
        issues = [
            {"identifier": f"HOM-{number}", "title": f"Task {number}", "status": "in_progress"}
            for number in range(100)
        ]
        result = client.summarize_status(issues, [], "https://paperclip.example")
        self.assertEqual(len(result["working_now"]), 12)
        self.assertTrue(result["truncated"])
        with self.assertRaises(client.PaperclipError):
            client.summarize_status({"error": "failed"}, [], "https://paperclip.example")


if __name__ == "__main__":
    unittest.main()
