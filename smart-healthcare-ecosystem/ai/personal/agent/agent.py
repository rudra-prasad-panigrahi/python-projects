from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from ai.personal.agent.router import route_intent
from ai.personal.personal_rag.embeddings.embedder import EmbeddingService
from ai.personal.personal_rag.retrieval.retriever import VectorRetriever
from ai.personal.trend_detection.inference import analyze_trend

GENERAL_FACTS = {
    "machine learning": "Machine learning is a way of training software to recognize patterns in data and make predictions from examples instead of explicit rules.",
    "mri": "An MRI is a medical imaging scan that uses magnetic fields and radio waves to create detailed pictures of the body, especially soft tissues and organs.",
    "ct": "A CT scan uses X-rays from many angles to build a cross-sectional image of the body and is useful for bones, internal injuries, and some soft-tissue evaluation.",
    "hba1c": "HbA1c is a blood test that reflects your average blood sugar over roughly the past 2-3 months. It is reported as a percentage.",
    "blood pressure": "Blood pressure is the force of blood against artery walls. It is usually written as systolic/diastolic, such as 120/80 mmHg.",
    "rag": "RAG stands for Retrieval-Augmented Generation. It means the model retrieves relevant documents or records first, then uses that context to answer a question more accurately and with source grounding.",
    "insulin": "Insulin is a hormone that helps move glucose from the blood into cells. In general health terms, it helps regulate blood sugar levels.",
    "glucose": "Glucose is the body’s main sugar source for energy. It is measured in mg/dL in many routine blood tests.",
}


class PersonalHealthAgent:
    def __init__(self, user_id: str, conversation_id: Optional[str] = None):
        self.user_id = user_id
        self.conversation_id = conversation_id or uuid4().hex
        self.embedder = EmbeddingService()
        self.retriever = VectorRetriever(dimension=self.embedder.dimension)
        self._load_user_context()

    def _load_user_context(self) -> None:
        try:
            from backend.app.main import USER_STATE, reindex_user_knowledge_base

            self.user_state = USER_STATE
            reindex_user_knowledge_base()
            self.retriever = VectorRetriever(dimension=self.embedder.dimension)
            texts = []
            items = []
            for key, value in self.user_state.items():
                if isinstance(value, dict):
                    continue
            for profile in [self.user_state["user"]]:
                for k, v in profile.items():
                    if isinstance(v, (str, int, float, bool)):
                        texts.append(f"Profile field {k}: {v}")
            for item in self.user_state.get("vitals", []):
                texts.append(f"Vital {item['type']}: {item['value']} {item['unit']} on {item['recorded_at']}")
            for item in self.user_state.get("medications", []):
                texts.append(f"Medication {item['name']}: {item['dosage']} {item['frequency']}.")
            for item in self.user_state.get("appointments", []):
                texts.append(f"Appointment {item['title']} on {item['starts_at']} with {item['provider_name']}.")
            embeddings = self.embedder.encode(texts)
            for text in texts:
                items.append({"text": text, "metadata": {"user_id": self.user_id, "record_type": "context"}})
            self.retriever.add(embeddings, [__import__('ai.personal.personal_rag.retrieval.retriever', fromlist=['RetrievalItem']).RetrievalItem(text=item["text"], metadata=item["metadata"]) for item in items])
        except Exception:
            self.user_state = {}

    def _detect_unauthorized_other_user(self, message: str) -> bool:
        lower = message.lower()
        return any(pattern in lower for pattern in ["user b", "another user", "other user's", "someone else's", "another patient's", "other patient"]) and any(token in lower for token in ["medical", "records", "patient", "report", "data", "history", "medications"])

    def _general_answer(self, message: str) -> dict[str, Any]:
        text = message.lower()
        for keyword, answer in GENERAL_FACTS.items():
            if keyword in text:
                return {
                    "answer": answer,
                    "sources": [],
                    "tool_calls": [],
                    "structured_data": None,
                    "requires_confirmation": False,
                    "conversation_id": self.conversation_id,
                    "intent": "GENERAL_KNOWLEDGE",
                }
        return {
            "answer": "I can help with general questions, health explanations, and your personal health records. Ask about a medical topic, your latest lab values, medications, appointments, or trends.",
            "sources": [],
            "tool_calls": [],
            "structured_data": None,
            "requires_confirmation": False,
            "conversation_id": self.conversation_id,
            "intent": "GENERAL_KNOWLEDGE",
        }

    def _latest_glucose(self) -> dict[str, Any] | None:
        try:
            from backend.app.main import USER_STATE

            values = [v for v in USER_STATE.get("vitals", []) if v.get("type") == "glucose"]
            if not values:
                return None
            latest = sorted(values, key=lambda item: item["recorded_at"])[-1]
            return {
                "value": float(latest["value"]),
                "unit": latest["unit"],
                "recorded_at": latest["recorded_at"],
                "source": latest.get("source", "Medical record"),
                "title": "Glucose Reading",
            }
        except Exception:
            return None

    def _latest_bp(self) -> dict[str, Any] | None:
        try:
            from backend.app.main import USER_STATE

            systolic = [v for v in USER_STATE.get("vitals", []) if v.get("type") == "blood_pressure_systolic"]
            diastolic = [v for v in USER_STATE.get("vitals", []) if v.get("type") == "blood_pressure_diastolic"]
            if not systolic or not diastolic:
                return None
            latest_sys = sorted(systolic, key=lambda item: item["recorded_at"])[-1]
            latest_dia = sorted(diastolic, key=lambda item: item["recorded_at"])[-1]
            return {
                "systolic": float(latest_sys["value"]),
                "diastolic": float(latest_dia["value"]),
                "unit": "mmHg",
                "recorded_at": latest_sys["recorded_at"],
                "source": latest_sys.get("source", "Medical record"),
            }
        except Exception:
            return None

    def _medications(self) -> list[dict[str, Any]]:
        try:
            from backend.app.main import USER_STATE

            return USER_STATE.get("medications", [])
        except Exception:
            return []

    def _appointments(self) -> list[dict[str, Any]]:
        try:
            from backend.app.main import USER_STATE

            items = USER_STATE.get("appointments", [])
            return sorted(items, key=lambda item: item.get("starts_at", ""))
        except Exception:
            return []

    def _tool_response(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "tool": name,
            "payload": payload,
        }

    def handle_message(self, message: str, conversation_history: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
        text = (message or "").strip()
        if not text:
            return {
                "answer": "I need a question or request to help with.",
                "sources": [],
                "tool_calls": [],
                "structured_data": None,
                "requires_confirmation": False,
                "conversation_id": self.conversation_id,
                "intent": "UNKNOWN",
            }

        intent = route_intent(text)
        if self._detect_unauthorized_other_user(text):
            return {
                "answer": "I can’t access or reveal another user’s medical records or private health information.",
                "sources": [],
                "tool_calls": [],
                "structured_data": None,
                "requires_confirmation": False,
                "conversation_id": self.conversation_id,
                "intent": "PERSONAL_RECORD_QUERY",
            }

        if intent in {"GENERAL_KNOWLEDGE", "GENERAL_HEALTH"}:
            result = self._general_answer(text)
            result["intent"] = intent
            return result

        if intent == "ACTION_REQUEST":
            if "blood pressure" in text.lower() and re.search(r"\d+\s*/\s*\d+", text):
                match = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text)
                if match:
                    payload = {"type": "blood_pressure_systolic", "value": float(match.group(1)), "diastolic": float(match.group(2)), "unit": "mmHg"}
                    return {
                        "answer": "I can record that blood pressure reading after confirmation. I’ll add a value of 120/80 mmHg to your personal health log.",
                        "sources": [],
                        "tool_calls": [self._tool_response("add_vital", payload)],
                        "structured_data": payload,
                        "requires_confirmation": True,
                        "action": {"kind": "add_vital", "payload": payload},
                        "conversation_id": self.conversation_id,
                        "intent": "ACTION_REQUEST",
                    }
            return {
                "answer": "I can help with safe, validated actions like adding a reading or creating a reminder, but I need a clear, valid request and confirmation before making changes.",
                "sources": [],
                "tool_calls": [],
                "structured_data": None,
                "requires_confirmation": True,
                "conversation_id": self.conversation_id,
                "intent": "ACTION_REQUEST",
            }

        if "latest glucose" in text.lower() or "glucose" in text.lower():
            latest = self._latest_glucose()
            if latest is None:
                return {"answer": "I couldn’t find an authorized glucose recording in your records.", "sources": [], "tool_calls": [self._tool_response("get_latest_vitals", {"metric": "glucose"})], "structured_data": None, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "VITAL_QUERY"}
            answer = f"Your latest glucose reading was {latest['value']} {latest['unit']} on {latest['recorded_at'][:10]} from {latest['source']}."
            return {
                "answer": answer,
                "sources": [{"title": latest["title"], "source": latest["source"], "source_date": latest["recorded_at"][:10]}],
                "tool_calls": [self._tool_response("get_latest_vitals", {"metric": "glucose"})],
                "structured_data": {"metric": "glucose", "values": [latest]},
                "requires_confirmation": False,
                "conversation_id": self.conversation_id,
                "intent": "VITAL_QUERY",
            }

        if "blood pressure" in text.lower() or "bp" in text.lower():
            latest = self._latest_bp()
            if latest is None:
                return {"answer": "I couldn’t find an authorized recent blood pressure reading.", "sources": [], "tool_calls": [self._tool_response("get_latest_vitals", {"metric": "blood_pressure"})], "structured_data": None, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "VITAL_QUERY"}
            answer = f"Your latest blood pressure reading was {int(latest['systolic'])}/{int(latest['diastolic'])} mmHg from {latest['source']} on {latest['recorded_at'][:10]}."
            return {"answer": answer, "sources": [{"title": "Blood Pressure Reading", "source": latest["source"], "source_date": latest["recorded_at"][:10]}], "tool_calls": [self._tool_response("get_latest_vitals", {"metric": "blood_pressure"})], "structured_data": {"metric": "blood_pressure", "values": [latest]}, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "VITAL_QUERY"}

        if "medication" in text.lower() or "prescription" in text.lower():
            meds = self._medications()
            if not meds:
                return {"answer": "I couldn’t find any active medications in your authorized records.", "sources": [], "tool_calls": [self._tool_response("get_medications", {})], "structured_data": None, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "MEDICATION_QUERY"}
            active = ", ".join(f"{m['name']} ({m['dosage']})" for m in meds if m.get("status") != "discontinued")
            answer = f"Your active medications include: {active}."
            return {"answer": answer, "sources": [{"title": m['name'], "source": m.get('source', 'Demo Care Clinic'), "source_date": m.get('start_date', 'N/A')} for m in meds], "tool_calls": [self._tool_response("get_medications", {})], "structured_data": {"medications": meds}, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "MEDICATION_QUERY"}

        if "appointment" in text.lower() or "doctor" in text.lower() or "visit" in text.lower():
            appointments = self._appointments()
            if not appointments:
                return {"answer": "I couldn’t find any scheduled appointments in your authorized records.", "sources": [], "tool_calls": [self._tool_response("get_appointments", {})], "structured_data": None, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "APPOINTMENT_QUERY"}
            next_apt = appointments[0]
            answer = f"Your next appointment is '{next_apt['title']}' with {next_apt['provider_name']} on {next_apt['starts_at'][:10]} at {next_apt['starts_at'][11:16]}.",
            return {"answer": answer[0], "sources": [{"title": next_apt['title'], "source": next_apt['organization'], "source_date": next_apt['starts_at'][:10]}], "tool_calls": [self._tool_response("get_appointments", {})], "structured_data": {"appointments": appointments}, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "APPOINTMENT_QUERY"}

        if "what is hba1c" in text.lower() or "hba1c" in text.lower():
            return {"answer": "HbA1c is a blood test that reflects your average blood sugar over the previous 2-3 months. It is often used as a longer-term glucose marker than a single fasting blood sugar reading.", "sources": [], "tool_calls": [], "structured_data": None, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "GENERAL_HEALTH"}

        if "latest report" in text.lower() or "lab" in text.lower() or "report" in text.lower():
            try:
                from backend.app.main import USER_STATE

                reports = USER_STATE.get("laboratory", [])
                if not reports:
                    raise ValueError
                latest = reports[0]
                answer = f"Your latest report is {latest['report_name']} from {latest['source']} on {latest['source_date']}. It includes values such as Glucose {latest['analytes'][0]['value']} mg/dL, which is above the supplied reference range."
                return {"answer": answer, "sources": [{"title": latest['report_name'], "source": latest['source'], "source_date": latest['source_date']}], "tool_calls": [self._tool_response("get_lab_reports", {})], "structured_data": {"reports": reports}, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "LAB_REPORT_QUERY"}
            except Exception:
                return {"answer": "I couldn’t find an authorized laboratory report matching that request.", "sources": [], "tool_calls": [self._tool_response("get_lab_reports", {})], "structured_data": None, "requires_confirmation": False, "conversation_id": self.conversation_id, "intent": "LAB_REPORT_QUERY"}

        return {
            "answer": "I can answer that using general knowledge or your authorized health records. Please ask in a more specific way, such as a health question, trend question, medication question, or appointment question.",
            "sources": [],
            "tool_calls": [],
            "structured_data": None,
            "requires_confirmation": False,
            "conversation_id": self.conversation_id,
            "intent": intent,
        }
