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

    # ------------------------------------------------------------------
    # show_technique flag — backend tells frontend whether to render technique
    # ------------------------------------------------------------------

    def test_suicidal_crisis_route_hides_technique(self):
        response = self.client.post(
            "/api/chat",
            json={
                "message": "I do not want to live",
                "history": [{"role": "user", "content": "I do not want to live"}],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(payload.get("safety_category"), "crisis")

    def test_physical_abuse_route_hides_technique(self):
        response = self.client.post(
            "/api/chat",
            json={
                "message": "My husband hits me",
                "history": [{"role": "user", "content": "My husband hits me"}],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload.get("safety_mode"))
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(payload.get("safety_category"), "abuse_violence")

    def test_fraud_take_loan_route_hides_technique(self):
        response = self.client.post(
            "/api/chat",
            json={
                "message": "He asked me to take a loan for him",
                "history": [
                    {
                        "role": "user",
                        "content": "He asked me to take a loan for him",
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(
            payload.get("safety_category"),
            "fraud_blackmail_financial_pressure",
        )

    def test_fraud_blackmail_route_hides_technique_ru(self):
        response = self.client.post(
            "/api/chat",
            json={
                "message": "Он шантажирует меня и требует деньги",
                "history": [
                    {
                        "role": "user",
                        "content": "Он шантажирует меня и требует деньги",
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload.get("safety_mode"))
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(
            payload.get("safety_category"),
            "fraud_blackmail_financial_pressure",
        )

    def test_normal_finance_topic_does_not_trigger_fraud_safety(self):
        """False-positive guard: normal financial discussions stay in normal flow."""
        response = self.client.post(
            "/api/chat",
            json={
                "message": "We share expenses and sometimes argue about it",
                "history": [
                    {
                        "role": "user",
                        "content": "We share expenses and sometimes argue about it",
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload.get("safety_mode", False))
        self.assertNotEqual(
            payload.get("safety_category"),
            "fraud_blackmail_financial_pressure",
        )
        # show_technique must not be False — either True (new clients) or absent (legacy parity).
        self.assertNotEqual(payload.get("show_technique"), False)

    def test_normal_family_budget_does_not_trigger_fraud_safety_ru(self):
        response = self.client.post(
            "/api/chat",
            json={
                "message": "Мы обсуждаем семейный бюджет",
                "history": [
                    {"role": "user", "content": "Мы обсуждаем семейный бюджет"}
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload.get("safety_mode", False))
        self.assertNotEqual(payload.get("show_technique"), False)

    # ------------------------------------------------------------------
    # Dangerous partner / criminal risk — route-level
    # ------------------------------------------------------------------

    def test_dangerous_partner_murder_minimization_route_ru(self):
        msg = "Он сидит за убийство, но я уверена, что он хороший человек"
        response = self.client.post(
            "/api/chat",
            json={"message": msg, "history": [{"role": "user", "content": msg}]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(
            payload.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )

    def test_dangerous_partner_rape_continue_contact_route_ru(self):
        msg = "Он изнасиловал людей, но я хочу продолжать с ним общаться"
        response = self.client.post(
            "/api/chat",
            json={"message": msg, "history": [{"role": "user", "content": msg}]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(
            payload.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )

    def test_dangerous_partner_release_with_children_route_ru(self):
        msg = (
            "У меня дома дети, а он скоро выходит из тюрьмы, я хочу его пригласить"
        )
        response = self.client.post(
            "/api/chat",
            json={"message": msg, "history": [{"role": "user", "content": msg}]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(
            payload.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )

    def test_dangerous_partner_chance_for_happiness_route_en(self):
        msg = "He is in prison for murder but I think he is my chance for happiness"
        response = self.client.post(
            "/api/chat",
            json={"message": msg, "history": [{"role": "user", "content": msg}]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(
            payload.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )

    def test_movie_about_prisoner_does_not_trigger_dangerous_partner_ru(self):
        msg = "Я смотрела фильм про человека в тюрьме"
        response = self.client.post(
            "/api/chat",
            json={"message": msg, "history": [{"role": "user", "content": msg}]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertNotEqual(
            payload.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )

    def test_partner_received_a_fine_does_not_trigger_dangerous_partner_ru(self):
        msg = "Мой партнер когда-то получил штраф"
        response = self.client.post(
            "/api/chat",
            json={"message": msg, "history": [{"role": "user", "content": msg}]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertNotEqual(
            payload.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )

    def test_real_long_ru_dangerous_partner_route(self):
        """Free-form long Russian message that previously slipped through."""
        msg = (
            "Я переписываюсь с мужчиной. Он сидит сейчас в тюрьме за убийство и "
            "изнасилование, скоро выходит на свободу. Преступления, которые он "
            "совершил, очень тяжёлые, но мне не страшно, я уверена в нём. "
            "Он уже знает мой адрес. У меня дома двое детей."
        )
        response = self.client.post(
            "/api/chat",
            json={"message": msg, "history": [{"role": "user", "content": msg}]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("risk_level"), "high")
        self.assertTrue(payload.get("safety_mode"))
        self.assertFalse(payload.get("show_technique"))
        self.assertEqual(
            payload.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )


if __name__ == "__main__":
    unittest.main()
