import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from safety_check import (
    check_crisis,
    check_abuse_violence,
    get_crisis_response,
    get_abuse_violence_response,
)


class SafetyChecksTestCase(unittest.TestCase):
    def test_suicidal_crisis_detection(self):
        risk_en, reason_en = check_crisis("I do not want to live anymore")
        self.assertEqual(risk_en, "high")
        self.assertIsNotNone(reason_en)

        risk_ru, reason_ru = check_crisis("Я не хочу жить")
        self.assertEqual(risk_ru, "high")
        self.assertIsNotNone(reason_ru)

        response = get_crisis_response("ru")
        self.assertEqual(response.get("risk_level"), "high")
        self.assertTrue(response.get("safety_mode"))
        self.assertTrue(response.get("needs_specialist_support"))

    def test_husband_hits_me_detection(self):
        risk, reason = check_abuse_violence("My husband hits me")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "physical_violence")

    def test_fear_of_partner_detection(self):
        risk, reason = check_abuse_violence("I am afraid of my partner")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "fear_for_safety")

    def test_coercive_control_and_threats_detection(self):
        risk, reason = check_abuse_violence(
            "He controls my phone and money and threatens me"
        )
        self.assertEqual(risk, "high")
        self.assertIn(reason, {"coercive_control", "threats"})

    def test_abuse_response_shape(self):
        response = get_abuse_violence_response("en")
        self.assertEqual(response.get("detected_state"), "safety_risk")
        self.assertEqual(response.get("risk_level"), "high")
        self.assertTrue(response.get("safety_mode"))
        self.assertTrue(response.get("needs_specialist_support"))


if __name__ == "__main__":
    unittest.main()
