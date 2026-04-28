import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from safety_check import (
    check_crisis,
    check_abuse_violence,
    check_fraud_financial_pressure,
    get_crisis_response,
    get_abuse_violence_response,
    get_fraud_financial_response,
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
        self.assertFalse(response.get("show_technique"))
        self.assertEqual(response.get("safety_category"), "abuse_violence")

    def test_crisis_response_hides_technique(self):
        response = get_crisis_response("en")
        self.assertFalse(response.get("show_technique"))
        self.assertEqual(response.get("safety_category"), "crisis")

    # ------------------------------------------------------------------
    # Fraud / blackmail / financial pressure detection
    # ------------------------------------------------------------------

    def test_request_to_take_loan_en(self):
        risk, reason = check_fraud_financial_pressure(
            "He asked me to take a loan for him"
        )
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "request_to_take_loan")

    def test_request_to_take_loan_ru(self):
        risk, reason = check_fraud_financial_pressure(
            "Он просит меня взять кредит для него"
        )
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "request_to_take_loan")

    def test_blackmail_detection_en(self):
        risk, reason = check_fraud_financial_pressure("He is blackmailing me")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "blackmail")

    def test_extortion_detection_ru(self):
        risk, reason = check_fraud_financial_pressure("Он вымогает у меня деньги")
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "extortion")

    def test_money_transfer_pressure_ru(self):
        risk, reason = check_fraud_financial_pressure(
            "Он требует переведи ему деньги срочно"
        )
        self.assertEqual(risk, "high")
        self.assertIn(
            reason, {"money_transfer_pressure", "urgent_money_request"}
        )

    def test_credential_request_en(self):
        risk, reason = check_fraud_financial_pressure(
            "He asks me for my verification code"
        )
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "credential_or_document_request")

    def test_prison_money_pressure_ru(self):
        risk, reason = check_fraud_financial_pressure(
            "Он в тюрьме и просит денег на залог"
        )
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "prison_money_pressure")

    def test_scam_detection_ru(self):
        risk, reason = check_fraud_financial_pressure(
            "Кажется, он мошенник и разводит меня"
        )
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "scam")

    def test_fraud_response_shape(self):
        response_en = get_fraud_financial_response("en")
        self.assertEqual(response_en.get("detected_state"), "safety_risk")
        self.assertEqual(response_en.get("risk_level"), "high")
        self.assertTrue(response_en.get("safety_mode"))
        self.assertFalse(response_en.get("show_technique"))
        self.assertEqual(
            response_en.get("safety_category"),
            "fraud_blackmail_financial_pressure",
        )
        self.assertTrue(response_en.get("needs_specialist_support"))

        response_ru = get_fraud_financial_response("ru")
        self.assertFalse(response_ru.get("show_technique"))
        self.assertEqual(
            response_ru.get("safety_category"),
            "fraud_blackmail_financial_pressure",
        )

    # ------------------------------------------------------------------
    # False positives — normal financial discussions must NOT trigger
    # ------------------------------------------------------------------

    def test_false_positive_we_share_expenses(self):
        risk, _ = check_fraud_financial_pressure("We share expenses")
        self.assertEqual(risk, "none")

    def test_false_positive_family_budget_ru(self):
        risk, _ = check_fraud_financial_pressure("Мы обсуждаем семейный бюджет")
        self.assertEqual(risk, "none")

    def test_false_positive_partner_asks_to_discuss_expenses_ru(self):
        risk, _ = check_fraud_financial_pressure("Он просит обсудить расходы")
        self.assertEqual(risk, "none")

    def test_false_positive_normal_argument(self):
        risk, _ = check_fraud_financial_pressure(
            "We had an argument about money last night"
        )
        self.assertEqual(risk, "none")

    def test_false_positive_he_earns_more_ru(self):
        risk, _ = check_fraud_financial_pressure(
            "Он зарабатывает больше меня и это иногда напрягает"
        )
        self.assertEqual(risk, "none")


if __name__ == "__main__":
    unittest.main()
