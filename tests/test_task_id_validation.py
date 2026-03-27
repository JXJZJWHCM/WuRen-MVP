import unittest
import asyncio
import json

from starlette.requests import Request

from src.api import server


class TaskIdValidationTests(unittest.TestCase):
    def _request(self, method: str = "GET", path: str = "/"):
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "path": path,
            "headers": [],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        return Request(scope)

    def _response_json(self, resp):
        return json.loads(resp.body.decode("utf-8"))

    def test_sanitize_task_id_allows_safe_value(self):
        value = "task-01_A.b:c"
        self.assertEqual(server._sanitize_task_id(value), value)

    def test_sanitize_task_id_rejects_dangerous_values(self):
        bad_values = [
            "",
            "   ",
            "..",
            "../x",
            "..\\x",
            "a/b",
            "a\\b",
            "a" * 81,
            "task with space",
        ]
        for value in bad_values:
            with self.subTest(value=value):
                self.assertIsNone(server._sanitize_task_id(value))

    def test_create_task_rejects_invalid_task_id(self):
        req = server.TaskCreateRequest(task_id="../x", goal="test")
        resp = server.create_task(self._request(method="POST", path="/api/tasks"), req)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self._response_json(resp).get("error"), "invalid_task_id")

    def test_delete_task_rejects_invalid_task_id(self):
        resp = asyncio.run(server.delete_task(self._request(method="DELETE", path="/api/tasks/.."), ".."))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self._response_json(resp).get("error"), "invalid_task_id")

    def test_task_events_rejects_invalid_task_id(self):
        resp = server.get_task_events("../x")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self._response_json(resp).get("error"), "invalid_task_id")

    def test_list_vulns_rejects_invalid_task_id_filter(self):
        resp = server.list_vulns(task_id="../x", limit=200)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self._response_json(resp).get("error"), "invalid_task_id")

    def test_upsert_vuln_rejects_invalid_task_id(self):
        req = server.VulnRequest(
            task_id="../x",
            target="127.0.0.1",
            title="test",
            severity="高危",
            status="open",
            details={},
        )
        resp = server.upsert_vuln(self._request(method="POST", path="/api/vulns"), req)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self._response_json(resp).get("error"), "invalid_task_id")

    def test_ensure_task_started_rejects_invalid_task_id(self):
        with self.assertRaises(ValueError):
            server._ensure_task_started("../x", "test")


if __name__ == "__main__":
    unittest.main()
