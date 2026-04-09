import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from safety_check import check_abuse_violence, check_history_for_safety_flags


class SafetySessionModeRouteTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret"
        self.client = app.test_client()

    # ------------------------------------------------------------------
    # Detection tests
    # ------------------------------------------------------------------

    def test_detect_husband_hits_me(self):
        risk, reason = check_abuse_violence("My husband hits me")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "physical_violence")

    def test_detect_fear_of_partner(self):
        risk, reason = check_abuse_violence("I am afraid of my partner")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "fear_for_safety")

    def test_detect_coercive_control(self):
        risk, reason = check_abuse_violence("He controls my phone and my money")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "coercive_control")

    def test_detect_threats(self):
        risk, reason = check_abuse_violence("She threatens me every day")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "threats")

    def test_detect_partner_beats_me(self):
        risk, reason = check_abuse_violence("My boyfriend beats me")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "physical_violence")

    def test_detect_not_safe(self):
        risk, reason = check_abuse_violence("I don't feel safe at home")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "fear_for_safety")

    # ------------------------------------------------------------------
    # History scanning tests
    # ------------------------------------------------------------------

    def test_history_flags_abuse(self):
        history = [
            {"role": "user", "content": "My husband hits me"},
            {"role": "assistant", "content": "..."},
            {"role": "user", "content": "What should I do?"},
        ]
        self.assertTrue(check_history_for_safety_flags(history))

    def test_history_flags_threats(self):
        history = [
            {"role": "user", "content": "He threatens me"},
            {"role": "assistant", "content": "..."},
        ]
        self.assertTrue(check_history_for_safety_flags(history))

    def test_history_no_flags(self):
        history = [
            {"role": "user", "content": "We argue a lot"},
            {"role": "assistant", "content": "..."},
        ]
        self.assertFalse(check_history_for_safety_flags(history))

    def test_empty_history(self):
        self.assertFalse(check_history_for_safety_flags([]))
        self.assertFalse(check_history_for_safety_flags(None))

    # ------------------------------------------------------------------
    # Route-level session persistence tests
    # ------------------------------------------------------------------

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

    def test_safety_mode_persists_via_history_even_without_session_cookie(self):
        """Even if session cookie is lost, history-based check keeps safety mode."""
        # Use a fresh client (no session cookie from prior request).
        fresh_client = create_app().test_client()
        fresh_client.application.config["TESTING"] = True
        fresh_client.application.config["SECRET_KEY"] = "test-secret"

        # Send a follow-up that includes abuse history, but this client has no cookie.
        response = fresh_client.post(
            "/api/chat",
            json={
                "message": "Can we just go back to normal?",
                "history": [
                    {"role": "user", "content": "My husband hits me"},
                    {"role": "assistant", "content": "Your safety comes first."},
                    {"role": "user", "content": "Can we just go back to normal?"},
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))
        self.assertEqual(payload.get("detected_state"), "safety_risk")

    def test_fear_of_partner_triggers_safety_and_followup_stays(self):
        first = self.client.post(
            "/api/chat",
            json={
                "message": "I'm afraid of my partner",
                "history": [{"role": "user", "content": "I'm afraid of my partner"}],
            },
        )
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.get_json().get("safety_mode"))

        second = self.client.post(
            "/api/chat",
            json={
                "message": "Maybe I should try to talk to him calmly",
                "history": [
                    {"role": "user", "content": "I'm afraid of my partner"},
                    {
                        "role": "assistant",
                        "content": first.get_json().get("message", ""),
                    },
                    {
                        "role": "user",
                        "content": "Maybe I should try to talk to him calmly",
                    },
                ],
            },
        )
        self.assertEqual(second.status_code, 200)
        payload = second.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))

    def test_coercive_control_triggers_safety_and_followup_stays(self):
        first = self.client.post(
            "/api/chat",
            json={
                "message": "He controls my phone and money",
                "history": [
                    {"role": "user", "content": "He controls my phone and money"}
                ],
            },
        )
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.get_json().get("safety_mode"))

        second = self.client.post(
            "/api/chat",
            json={
                "message": "But he is nice sometimes",
                "history": [
                    {"role": "user", "content": "He controls my phone and money"},
                    {
                        "role": "assistant",
                        "content": first.get_json().get("message", ""),
                    },
                    {"role": "user", "content": "But he is nice sometimes"},
                ],
            },
        )
        self.assertEqual(second.status_code, 200)
        payload = second.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))

    def test_threats_trigger_safety_and_followup_stays(self):
        first = self.client.post(
            "/api/chat",
            json={
                "message": "He threatens me every day",
                "history": [{"role": "user", "content": "He threatens me every day"}],
            },
        )
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.get_json().get("safety_mode"))

        second = self.client.post(
            "/api/chat",
            json={
                "message": "I just want things to be normal again",
                "history": [
                    {"role": "user", "content": "He threatens me every day"},
                    {
                        "role": "assistant",
                        "content": first.get_json().get("message", ""),
                    },
                    {
                        "role": "user",
                        "content": "I just want things to be normal again",
                    },
                ],
            },
        )
        self.assertEqual(second.status_code, 200)
        payload = second.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))

    def test_normal_conversation_does_not_trigger_safety(self):
        """Normal messages should NOT activate safety mode."""
        response = self.client.post(
            "/api/chat",
            json={
                "message": "We had a small argument yesterday",
                "history": [
                    {"role": "user", "content": "We had a small argument yesterday"}
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertNotEqual(payload.get("risk_level"), "high")
        self.assertFalse(payload.get("safety_mode", False))


if __name__ == "__main__":
    unittest.main()
