import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from safety_check import (
    check_crisis,
    check_abuse_violence,
    check_fraud_financial_pressure,
    check_dangerous_partner_or_criminal_risk,
    get_crisis_response,
    get_abuse_violence_response,
    get_fraud_financial_response,
    get_dangerous_partner_response,
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

    # ------------------------------------------------------------------
    # Dangerous partner / criminal risk detection
    # ------------------------------------------------------------------

    def test_dangerous_partner_prison_murder_minimization_ru(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "Он сидит за убийство, но я уверена, что он хороший человек"
        )
        self.assertEqual(risk, "high")
        self.assertIn("minimization", reason)

    def test_dangerous_partner_rape_continue_contact_ru(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "Он изнасиловал людей, но я хочу продолжать с ним общаться"
        )
        self.assertEqual(risk, "high")
        self.assertIn("romantic_involvement", reason)

    def test_dangerous_partner_release_invite_with_children_ru(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "У меня дома дети, а он скоро выходит из тюрьмы, я хочу его пригласить"
        )
        self.assertEqual(risk, "high")
        self.assertTrue(
            "romantic_involvement" in reason or "children_present" in reason
        )

    def test_dangerous_partner_prison_murder_chance_for_happiness_en(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "He is in prison for murder but I think he is my chance for happiness"
        )
        self.assertEqual(risk, "high")
        self.assertIn("minimization", reason)

    def test_dangerous_partner_response_shape(self):
        response_en = get_dangerous_partner_response("en")
        self.assertEqual(response_en.get("detected_state"), "safety_risk")
        self.assertEqual(response_en.get("risk_level"), "high")
        self.assertTrue(response_en.get("safety_mode"))
        self.assertFalse(response_en.get("show_technique"))
        self.assertEqual(
            response_en.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )
        self.assertTrue(response_en.get("needs_specialist_support"))

        response_ru = get_dangerous_partner_response("ru")
        self.assertFalse(response_ru.get("show_technique"))
        self.assertEqual(
            response_ru.get("safety_category"), "dangerous_partner_or_criminal_risk"
        )

    # ------------------------------------------------------------------
    # Dangerous partner — false positives
    # ------------------------------------------------------------------

    def test_false_positive_movie_about_prisoner_ru(self):
        """Watching a movie about a prisoner must NOT activate safety."""
        risk, _ = check_dangerous_partner_or_criminal_risk(
            "Я смотрела фильм про человека в тюрьме"
        )
        self.assertEqual(risk, "none")

    def test_false_positive_partner_received_a_fine_ru(self):
        """A minor offence (a fine) must NOT activate dangerous-partner safety."""
        risk, _ = check_dangerous_partner_or_criminal_risk(
            "Мой партнер когда-то получил штраф"
        )
        self.assertEqual(risk, "none")

    def test_false_positive_news_about_crime_en(self):
        """Discussing news about a crime, no romantic context — no trigger."""
        risk, _ = check_dangerous_partner_or_criminal_risk(
            "I read in the news that he is in prison for murder"
        )
        self.assertEqual(risk, "none")

    def test_false_positive_normal_relationship_no_criminal_context(self):
        """No criminal context at all — no trigger even with romantic + children."""
        risk, _ = check_dangerous_partner_or_criminal_risk(
            "My boyfriend is great, I have a child and want to invite him over"
        )
        self.assertEqual(risk, "none")

    # ------------------------------------------------------------------
    # Realistic long-form scenarios that previously slipped through
    # ------------------------------------------------------------------

    def test_real_world_long_ru_case_triggers_dangerous_partner(self):
        msg = (
            "Я переписываюсь с мужчиной. Он сидит сейчас в тюрьме за убийство и "
            "изнасилование, скоро выходит на свободу. Преступления, которые он "
            "совершил, очень тяжёлые, но мне не страшно, я уверена в нём. "
            "Он уже знает мой адрес. У меня дома двое детей."
        )
        risk, reason = check_dangerous_partner_or_criminal_risk(msg)
        self.assertEqual(risk, "high")
        self.assertIn("imprisonment", reason)
        self.assertIn("serious_crime", reason)
        self.assertIn("address_knowledge", reason)
        self.assertIn("minimization", reason)
        self.assertIn("children_present", reason)

    def test_short_he_sits_for_murder_with_minimization_ru(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "Он сидит за убийство, я ему верю"
        )
        self.assertEqual(risk, "high")
        self.assertIn("minimization", reason)

    def test_short_he_raped_people_with_romantic_ru(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "Он изнасиловал людей, я хочу быть с ним"
        )
        self.assertEqual(risk, "high")
        self.assertIn("serious_crime", reason)
        self.assertIn("romantic_involvement", reason)

    def test_address_knowledge_with_imprisonment_triggers_alone_ru(self):
        """Address knowledge is a strong amplifier — triggers without other phase-2 signals."""
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "Он скоро выходит на свободу и знает мой адрес"
        )
        self.assertEqual(risk, "high")
        self.assertIn("address_knowledge", reason)

    def test_short_release_and_children_ru(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "Он выходит из тюрьмы, у меня дома двое детей"
        )
        self.assertEqual(risk, "high")
        self.assertIn("children_present", reason)

    def test_committed_murder_with_minimization_ru(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "Он совершил убийство, но он хороший человек"
        )
        self.assertEqual(risk, "high")
        self.assertIn("minimization", reason)

    def test_serving_life_sentence_with_pen_pal_en(self):
        risk, reason = check_dangerous_partner_or_criminal_risk(
            "He is serving a life sentence for murder, we are pen pals and I love him"
        )
        self.assertEqual(risk, "high")
        self.assertIn("imprisonment", reason)
        self.assertIn("romantic_involvement", reason)

    # ------------------------------------------------------------------
    # Media false positives — must NOT trigger
    # ------------------------------------------------------------------

    def test_false_positive_book_about_killer_ru(self):
        risk, _ = check_dangerous_partner_or_criminal_risk(
            "Я читала книгу про убийцу, который сидит за убийство"
        )
        self.assertEqual(risk, "none")

    def test_false_positive_series_about_prison_ru(self):
        risk, _ = check_dangerous_partner_or_criminal_risk(
            "В сериале герой сидит в тюрьме за изнасилование"
        )
        self.assertEqual(risk, "none")

    def test_false_positive_news_about_release_en(self):
        risk, _ = check_dangerous_partner_or_criminal_risk(
            "I read in the news that a convicted murderer is being released"
        )
        self.assertEqual(risk, "none")


if __name__ == "__main__":
    unittest.main()
