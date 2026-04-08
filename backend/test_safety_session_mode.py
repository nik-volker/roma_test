import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app


class SafetySessionModeRouteTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret"
        self.client = app.test_client()

    def test_session_enters_safety_mode_after_abuse_and_stays_active(self):
        # 1) Trigger safety mode with abuse phrase.
        first = self.client.post(
            "/api/chat",
            json={
                "message": "My husband hits me",
                "history": [{"role": "user", "content": "My husband hits me"}],
            },
        )
        self.assertEqual(first.status_code, 200)
        payload_first = first.get_json()
        self.assertEqual(payload_first.get("risk_level"), "high")
        self.assertTrue(payload_first.get("safety_mode"))

        # 2) Non-abuse follow-up in same session should still stay in safety mode.
        second = self.client.post(
            "/api/chat",
            json={
                "message": "What should I do now?",
                "history": [
                    {"role": "user", "content": "My husband hits me"},
                    {"role": "assistant", "content": payload_first.get("message", "")},
                    {"role": "user", "content": "What should I do now?"},
                ],
            },
        )
        self.assertEqual(second.status_code, 200)
        payload_second = second.get_json()
        self.assertEqual(payload_second.get("detected_state"), "safety_risk")
        self.assertEqual(payload_second.get("risk_level"), "high")
        self.assertTrue(payload_second.get("safety_mode"))


if __name__ == "__main__":
    unittest.main()
