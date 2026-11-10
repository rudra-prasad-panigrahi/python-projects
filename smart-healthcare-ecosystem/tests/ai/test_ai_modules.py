"""Comprehensive AI Module Tests for Personal Health Gateway (Module 1)."""
import unittest
from ai.personal.trend_detection.inference import analyze_trend
from ai.personal.risk_prediction.inference import RiskPredictionService
from ai.personal.risk_prediction.features import RiskInput
from ai.personal.medication_adherence.inference import predict_adherence
from ai.personal.personal_rag.embeddings.embedder import EmbeddingService
from ai.personal.personal_rag.retrieval.retriever import VectorRetriever, RetrievalItem
from ai.personal.lab_interpreter.extraction import LabValue
from ai.personal.lab_interpreter.interpretation import interpret_lab_result
from ai.personal.agent.router import route_intent
from ai.personal.agent.agent import PersonalHealthAgent

class TestAIPlatform(unittest.TestCase):
    def test_trend_detection_increasing(self):
        timestamps = ["2026-08-04T09:00:00Z", "2026-08-12T09:00:00Z", "2026-08-28T09:00:00Z"]
        values = [110.0, 118.0, 126.0]
        res = analyze_trend(timestamps, values, "glucose")
        self.assertEqual(res["direction"], "increasing")
        self.assertGreater(res["slope"], 0)
        self.assertGreaterEqual(res["r_squared"], 0.75)
        self.assertEqual(res["strength"], "strong")
        self.assertIn("does not establish a medical diagnosis", res["informational_note"])

    def test_trend_detection_stable(self):
        timestamps = ["2026-08-01T09:00:00Z", "2026-08-15T09:00:00Z", "2026-08-28T09:00:00Z"]
        values = [120.0, 120.0, 120.0]
        res = analyze_trend(timestamps, values, "blood_pressure_systolic")
        self.assertEqual(res["direction"], "stable")
        self.assertEqual(res["slope"], 0.0)

    def test_cardiovascular_risk_prototype(self):
        service = RiskPredictionService()
        data = RiskInput(age=45, bmi=26.0, systolic_bp=125, glucose=110, smoker=False, family_history=False)
        res = service.predict(data)
        self.assertIn("model_estimated_risk_category", res)
        self.assertIn("estimated_risk_probability", res)
        self.assertEqual(res["status"], "Prototype / Research Model")
        self.assertIn("PROTOTYPE / RESEARCH MODEL ONLY", res["clinical_validity_note"])

    def test_medication_adherence_ml(self):
        events = [
            {"date": "2026-08-27", "scheduled": True, "taken": True, "late": False},
            {"date": "2026-08-28", "scheduled": True, "taken": True, "late": False},
            {"date": "2026-08-29", "scheduled": True, "taken": True, "late": False},
            {"date": "2026-08-30", "scheduled": True, "taken": False, "late": False},
            {"date": "2026-08-31", "scheduled": True, "taken": True, "late": False},
        ]
        res = predict_adherence(events)
        self.assertEqual(res["doses_scheduled"], 5)
        self.assertEqual(res["doses_taken"], 4)
        self.assertEqual(res["missed_doses"], 1)
        self.assertEqual(res["adherence_percentage"], 80.0)
        self.assertIn("informational", res["informational_note"].lower())

    def test_personal_rag_retrieval_and_isolation(self):
        embedder = EmbeddingService(dimension=64)
        retriever = VectorRetriever(dimension=64)

        t1 = "Fasting glucose was 126 mg/dL recorded on 28 Aug 2026."
        t2 = "Prescription for Metformin 500mg taken twice daily."
        t3 = "Another user confidential medical history."

        items = [
            RetrievalItem(text=t1, metadata={"user_id": "user-avery", "record_type": "vital"}),
            RetrievalItem(text=t2, metadata={"user_id": "user-avery", "record_type": "medication"}),
            RetrievalItem(text=t3, metadata={"user_id": "user-other", "record_type": "confidential"}),
        ]
        embeddings = embedder.encode([t1, t2, t3])
        retriever.add(embeddings, items)

        q_vec = embedder.encode(["glucose reading"])[0]
        results = retriever.search(q_vec, top_k=5, metadata_filter={"user_id": "user-avery"})

        # Verify only user-avery items are returned
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["metadata"]["user_id"], "user-avery")
            self.assertNotEqual(r["metadata"]["user_id"], "user-other")

    def test_lab_interpreter_non_diagnostic_phrasing(self):
        lab = LabValue(name="Glucose", value=126.0, unit="mg/dL", reference_min=70.0, reference_max=99.0)
        interp = interpret_lab_result(lab)
        self.assertEqual(interp["status"], "above_reference")
        self.assertIn("above the supplied reference range", interp["explanation"])
        # Ensure it does NOT diagnose disease directly
        self.assertNotIn("you have diabetes", interp["explanation"].lower())

    def test_agent_routes_general_questions(self):
        intent = route_intent("What is machine learning?")
        self.assertEqual(intent, "GENERAL_KNOWLEDGE")

    def test_agent_handles_personal_glucose_question(self):
        agent = PersonalHealthAgent(user_id="usr-avery-morgan-87")
        result = agent.handle_message("What was my latest glucose result?")
        self.assertIn("126", result["answer"])
        self.assertTrue(len(result["sources"]) >= 1)

    def test_agent_rejects_cross_user_query(self):
        agent = PersonalHealthAgent(user_id="usr-avery-morgan-87")
        result = agent.handle_message("Show me User B's medical records.")
        self.assertIn("not authorized", result["answer"].lower())

    def test_agent_handles_action_request(self):
        agent = PersonalHealthAgent(user_id="usr-avery-morgan-87")
        result = agent.handle_message("Add my blood pressure reading of 120/80.")
        self.assertIn("blood pressure", result["answer"].lower())
        self.assertTrue(result.get("action") or result.get("requires_confirmation") or result.get("structured_data") is not None)

if __name__ == '__main__':
    unittest.main()
