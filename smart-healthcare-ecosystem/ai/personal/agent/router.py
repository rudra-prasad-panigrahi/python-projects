from __future__ import annotations

import re

GENERAL_HEALTH_TOPICS = {
    "hba1c": "GENERAL_HEALTH",
    "blood pressure": "GENERAL_HEALTH",
    "mri": "GENERAL_HEALTH",
    "ct scan": "GENERAL_HEALTH",
    "ct": "GENERAL_HEALTH",
    "machine learning": "GENERAL_KNOWLEDGE",
    "rag": "GENERAL_KNOWLEDGE",
    "insulin": "GENERAL_HEALTH",
    "glucose": "GENERAL_HEALTH",
}


def route_intent(message: str) -> str:
    text = (message or "").strip().lower()
    if not text:
        return "UNKNOWN"

    if any(token in text for token in ["user b", "other user", "someone else's", "another patient", "show me user", "my partner's", "another person's"]):
        return "PERSONAL_RECORD_QUERY"

    if any(token in text for token in ["add ", "update ", "create ", "upload ", "remind ", "log ", "record ", "request "]):
        if any(token in text for token in ["blood pressure", "bp", "medication", "appointment", "document", "contact", "vital", "glucose", "weight", "heart rate"]):
            return "ACTION_REQUEST"

    if any(token in text for token in ["how has", "trend", "changed", "increasing", "decreasing", "compare", "over time", "history", "trend analysis"]):
        return "TREND_ANALYSIS"

    if any(token in text for token in ["what was my", "my latest", "my next", "when is my", "what medications", "how has my", "what happened during my", "show my", "summarize my", "compare my", "what is my", "do i have", "did i", "what are my"]):
        if any(token in text for token in ["glucose", "bp", "blood pressure", "weight", "lab", "report", "medication", "appointment", "timeline", "doctor", "visit", "vital", "hba1c", "next visit"]):
            return "PERSONAL_RECORD_QUERY"

    if any(token in text for token in ["appointment", "doctor", "provider", "visit", "consultation", "next appointment", "follow-up", "schedule"]):
        return "APPOINTMENT_QUERY"

    if any(token in text for token in ["lab", "laboratory", "report", "analyte", "cholesterol", "creatinine", "metabolic panel", "test result", "lab report"]):
        return "LAB_REPORT_QUERY"

    if any(token in text for token in ["document", "pdf", "jpg", "png", "report summary", "uploaded file", "this report", "file upload"]):
        return "DOCUMENT_QUERY"

    if any(token in text for token in ["medication", "prescription", "pill", "drug", "dose", "active medication", "take my"]):
        return "MEDICATION_QUERY"

    if any(token in text for token in ["timeline", "what happened", "recent health", "history", "sequence of events", "health summary"]):
        return "TIMELINE_QUERY"

    if any(token in text for token in ["care", "provider", "find a doctor", "nearby", "hospital", "clinic", "pharmacy"]):
        return "CARE_NAVIGATION"

    if any(token in text for token in ["emergency", "allergy", "contact", "blood type", "critical condition", "ice contact"]):
        return "EMERGENCY_PROFILE_QUERY"

    if any(token in text for token in ["glucose", "weight", "bp", "blood pressure", "heart rate", "spo2", "vital", "hba1c", "latest glucose", "latest blood pressure"]):
        return "VITAL_QUERY"

    if any(token in text for token in ["what is rag", "what is machine learning", "what is hba1c", "what is an mri", "what is insulin", "what is a ct scan", "blood pressure in simple language", "explain blood pressure", "what are blood pressure readings", "how does insulin work"]):
        return "GENERAL_HEALTH" if any(term in text for term in ["hba1c", "mri", "blood pressure", "insulin", "ct scan", "ct"]) else "GENERAL_KNOWLEDGE"

    for keyword, intent in GENERAL_HEALTH_TOPICS.items():
        if keyword in text:
            return intent

    if re.search(r"\b(my|i|mine|me)\b", text) and any(token in text for token in ["glucose", "appointment", "medication", "blood pressure", "report", "lab", "timeline", "profile", "vital"]):
        return "PERSONAL_RECORD_QUERY"

    if any(token in text for token in ["what can you do", "help me", "assistant", "agent", "you can"]):
        return "GENERAL_KNOWLEDGE"

    return "GENERAL_KNOWLEDGE"
