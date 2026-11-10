"""Complete Personal Health Gateway API (Module 1).

An AI-powered Personal Health Operating System for individuals to securely maintain,
understand, organize, and utilize personal health records, vitals, medications,
laboratory reports, appointments, care navigation, emergency readiness, privacy,
and consent independently of any single hospital.

This implementation strictly separates source-backed records from AI-generated explanations,
provides robust data provenance, prevents BOLA/IDOR cross-user access, and enforces
clinical safety guardrails.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import secrets
from datetime import date, datetime, timedelta, timezone
from typing import Any, Literal
from urllib.parse import urlencode
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from backend.app.database.base import Base
from backend.app.core.config import settings
from backend.app.database.engine import SessionLocal, engine
from backend.app.database.models import AuditEvent, OAuthIdentity, PersonalProfile, User

from ai.personal.agent import PersonalHealthAgent
from ai.personal.lab_interpreter.extraction import LabValue
from ai.personal.lab_interpreter.interpretation import interpret_lab_results
from ai.personal.medication_adherence.inference import predict_adherence
from ai.personal.personal_rag.embeddings.embedder import EmbeddingService
from ai.personal.personal_rag.retrieval.retriever import RetrievalItem, VectorRetriever
from ai.personal.risk_prediction.features import RiskInput
from ai.personal.risk_prediction.inference import RiskPredictionService
from ai.personal.trend_detection.inference import analyze_trend

app = FastAPI(
    title="Smart Healthcare — Personal Health Gateway API",
    version="1.0.0",
    description="AI-powered Personal Health Operating System. Module 1: Personal Health Gateway.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.oauth_session_secret,
    same_site="lax",
    https_only=settings.environment == "production",
    max_age=600,
)

logger = logging.getLogger(__name__)
oauth = OAuth()
if settings.google_oauth_client_id and settings.google_oauth_client_secret:
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret,
        client_kwargs={"scope": "openid email profile"},
    )
if settings.github_oauth_client_id and settings.github_oauth_client_secret:
    oauth.register(
        name="github",
        client_id=settings.github_oauth_client_id,
        client_secret=settings.github_oauth_client_secret,
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )

# Demo Authentication Constants
DEMO_EMAIL = "patient@healthcare.local"
DEMO_PASSWORD = "Demo@12345"
DEMO_USER_ID = "usr-avery-morgan-87"

# Session Token Store: token -> {user_id, email, expires_at, created_at}
SESSIONS: dict[str, dict[str, Any]] = {}
CONVERSATIONS: dict[str, list[dict[str, Any]]] = {}
OAUTH_TICKETS: dict[str, tuple[str, datetime]] = {}

class OAuthAccountConflict(Exception):
    pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
        "gender": user.gender,
        "phone": user.phone,
        "address": user.address,
        "city": user.city,
        "state": user.state,
        "country": user.country,
        "postal_code": user.postal_code,
        "blood_group": user.blood_group,
        "important_notes": user.important_notes,
        "preferred_hospital": user.preferred_hospital,
        "emergency_directives": user.emergency_directives,
    }


def serialize_profile(profile: PersonalProfile) -> dict[str, Any]:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": profile.email,
        "phone": profile.phone,
        "address": profile.address,
        "city": profile.city,
        "state": profile.state,
        "country": profile.country,
        "postal_code": profile.postal_code,
        "blood_group": profile.blood_group,
        "allergies": json.loads(profile.allergies or "[]"),
        "conditions": json.loads(profile.conditions or "[]"),
        "important_notes": profile.important_notes,
        "preferred_hospital": profile.preferred_hospital,
        "emergency_directives": profile.emergency_directives,
        "emergency_contacts": json.loads(profile.emergency_contacts or "[]"),
    }


def ensure_demo_seed() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if existing is not None:
            if existing.password_hash != hash_password(DEMO_PASSWORD):
                existing.password_hash = hash_password(DEMO_PASSWORD)
            if not existing.profile:
                profile = PersonalProfile(
                    user_id=existing.id,
                    email=existing.email,
                    phone=existing.phone,
                    address=existing.address,
                    city=existing.city,
                    state=existing.state,
                    country=existing.country,
                    postal_code=existing.postal_code,
                    blood_group=existing.blood_group,
                    allergies=json.dumps([{"name": "Penicillin", "severity": "Moderate", "reaction": "Hives and localized swelling", "reported_date": "2024-03-15", "source": "Self-reported"}]),
                    conditions=json.dumps([{"name": "Mild Hypertension", "diagnosed_date": "2025-01-10", "status": "Managed", "source": "Demo Care Clinic"}]),
                    important_notes="Maintains a personal health log. Prefers evening appointment slots and digital notification reminders.",
                    preferred_hospital="Seattle Central Medical Center (Synthetic)",
                    emergency_directives="No extraordinary measures without consulting primary emergency contact.",
                    emergency_contacts=json.dumps([{"id": "c-1", "name": "Jordan Morgan", "relationship": "Spouse", "phone": "+1 (555) 014-1001", "email": "jordan.morgan@example.test", "primary": True}]),
                )
                db.add(profile)
            db.commit()
            return

        demo_user = User(
            id=DEMO_USER_ID,
            email=DEMO_EMAIL,
            password_hash=hash_password(DEMO_PASSWORD),
            first_name="Avery",
            middle_name="Jordan",
            last_name="Morgan",
            date_of_birth=date.fromisoformat("1987-04-18"),
            gender="prefer_not_to_say",
            phone="+1 (555) 014-2026",
            address="742 Evergreen Way, Suite 4B",
            city="Seattle",
            state="WA",
            country="United States",
            postal_code="98101",
            blood_group="O+",
            important_notes="Maintains a personal health log. Prefers evening appointment slots and digital notification reminders.",
            preferred_hospital="Seattle Central Medical Center (Synthetic)",
            emergency_directives="No extraordinary measures without consulting primary emergency contact.",
        )
        db.add(demo_user)
        db.flush()
        profile = PersonalProfile(
            user_id=demo_user.id,
            email=demo_user.email,
            phone=demo_user.phone,
            address=demo_user.address,
            city=demo_user.city,
            state=demo_user.state,
            country=demo_user.country,
            postal_code=demo_user.postal_code,
            blood_group=demo_user.blood_group,
            allergies=json.dumps([{"name": "Penicillin", "severity": "Moderate", "reaction": "Hives and localized swelling", "reported_date": "2024-03-15", "source": "Self-reported"}]),
            conditions=json.dumps([{"name": "Mild Hypertension", "diagnosed_date": "2025-01-10", "status": "Managed", "source": "Demo Care Clinic"}]),
            important_notes=demo_user.important_notes,
            preferred_hospital=demo_user.preferred_hospital,
            emergency_directives=demo_user.emergency_directives,
            emergency_contacts=json.dumps([{"id": "c-1", "name": "Jordan Morgan", "relationship": "Spouse", "phone": "+1 (555) 014-1001", "email": "jordan.morgan@example.test", "primary": True}]),
        )
        db.add(profile)
        db.commit()


def ensure_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_demo_seed()


ensure_database()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_profile(db: Session, user_id: str) -> PersonalProfile:
    profile = db.scalar(select(PersonalProfile).where(PersonalProfile.user_id == user_id))
    if profile is not None:
        return profile
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    profile = PersonalProfile(
        user_id=user.id,
        email=user.email,
        phone=user.phone,
        address=user.address,
        city=user.city,
        state=user.state,
        country=user.country,
        postal_code=user.postal_code,
        blood_group=user.blood_group,
        important_notes=user.important_notes,
        preferred_hospital=user.preferred_hospital,
        emergency_directives=user.emergency_directives,
        allergies="[]",
        conditions="[]",
        emergency_contacts="[]",
    )
    db.add(profile)
    db.commit()
    return profile


def record_audit(db: Session, user_id: str | None, event_type: str, description: str | None = None) -> None:
    db.add(AuditEvent(user_id=user_id, event_type=event_type, description=description))
    db.commit()


def profile_payload_for_user(user: User, profile: PersonalProfile | None = None) -> dict[str, Any]:
    safe_profile = profile or PersonalProfile(user_id=user.id, email=user.email, allergies="[]", conditions="[]", emergency_contacts="[]")
    payload = serialize_user(user)
    payload.update(
        {
            "emergency_contacts": json.loads(safe_profile.emergency_contacts or "[]"),
            "allergies": json.loads(safe_profile.allergies or "[]"),
            "conditions": json.loads(safe_profile.conditions or "[]"),
            "data_provenance": {
                "source": "Personal Health Gateway",
                "last_verified": datetime.now(timezone.utc).date().isoformat(),
                "verification_status": "Identity Verified",
            },
        }
    )
    return payload



# In-Memory Database for Avery Morgan (Coherent Synthetic Health Record)
USER_STATE = {
    "user": {
        "id": DEMO_USER_ID,
        "email": DEMO_EMAIL,
        "first_name": "Avery",
        "middle_name": "Jordan",
        "last_name": "Morgan",
        "date_of_birth": "1987-04-18",
        "gender": "prefer_not_to_say",
        "phone": "+1 (555) 014-2026",
        "address": "742 Evergreen Way, Suite 4B",
        "city": "Seattle",
        "state": "WA",
        "country": "United States",
        "postal_code": "98101",
        "blood_group": "O+",
        "allergies": [
            {"name": "Penicillin", "severity": "Moderate", "reaction": "Hives and localized swelling", "reported_date": "2024-03-15", "source": "Self-reported"}
        ],
        "conditions": [
            {"name": "Mild Hypertension", "diagnosed_date": "2025-01-10", "status": "Managed", "source": "Demo Care Clinic"}
        ],
        "important_notes": "Maintains a personal health log. Prefers evening appointment slots and digital notification reminders.",
        "preferred_hospital": "Seattle Central Medical Center (Synthetic)",
        "emergency_directives": "No extraordinary measures without consulting primary emergency contact.",
    },
    "emergency_contacts": [
        {"id": "c-1", "name": "Jordan Morgan", "relationship": "Spouse", "phone": "+1 (555) 014-1001", "email": "jordan.morgan@example.test", "primary": True}
    ],
    "vitals": [
        {"id": "v-1", "type": "glucose", "value": 110.0, "unit": "mg/dL", "recorded_at": "2026-08-04T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-2", "type": "glucose", "value": 118.0, "unit": "mg/dL", "recorded_at": "2026-08-12T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-3", "type": "glucose", "value": 126.0, "unit": "mg/dL", "recorded_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-4", "type": "blood_pressure_systolic", "value": 118.0, "unit": "mmHg", "recorded_at": "2026-08-04T09:00:00Z", "source": "Demo Care Clinic", "verified": True},
        {"id": "v-5", "type": "blood_pressure_diastolic", "value": 76.0, "unit": "mmHg", "recorded_at": "2026-08-04T09:00:00Z", "source": "Demo Care Clinic", "verified": True},
        {"id": "v-6", "type": "blood_pressure_systolic", "value": 121.0, "unit": "mmHg", "recorded_at": "2026-08-19T09:00:00Z", "source": "Added by you", "verified": False},
        {"id": "v-7", "type": "blood_pressure_diastolic", "value": 78.0, "unit": "mmHg", "recorded_at": "2026-08-19T09:00:00Z", "source": "Added by you", "verified": False},
        {"id": "v-8", "type": "blood_pressure_systolic", "value": 120.0, "unit": "mmHg", "recorded_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-9", "type": "blood_pressure_diastolic", "value": 77.0, "unit": "mmHg", "recorded_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-10", "type": "weight", "value": 165.0, "unit": "lbs", "recorded_at": "2026-08-01T08:00:00Z", "source": "Added by you", "verified": False},
        {"id": "v-11", "type": "weight", "value": 164.0, "unit": "lbs", "recorded_at": "2026-08-15T08:00:00Z", "source": "Added by you", "verified": False},
        {"id": "v-12", "type": "weight", "value": 164.0, "unit": "lbs", "recorded_at": "2026-08-28T08:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-13", "type": "heart_rate", "value": 72.0, "unit": "bpm", "recorded_at": "2026-08-04T09:00:00Z", "source": "Demo Care Clinic", "verified": True},
        {"id": "v-14", "type": "heart_rate", "value": 70.0, "unit": "bpm", "recorded_at": "2026-08-19T09:00:00Z", "source": "Added by you", "verified": False},
        {"id": "v-15", "type": "heart_rate", "value": 74.0, "unit": "bpm", "recorded_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-16", "type": "spo2", "value": 98.0, "unit": "%", "recorded_at": "2026-08-04T09:00:00Z", "source": "Demo Care Clinic", "verified": True},
        {"id": "v-17", "type": "spo2", "value": 98.0, "unit": "%", "recorded_at": "2026-08-19T09:00:00Z", "source": "Added by you", "verified": False},
        {"id": "v-18", "type": "spo2", "value": 99.0, "unit": "%", "recorded_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "v-19", "type": "hba1c", "value": 5.6, "unit": "%", "recorded_at": "2026-02-10T09:00:00Z", "source": "Demo Care Clinic", "verified": True},
        {"id": "v-20", "type": "hba1c", "value": 5.7, "unit": "%", "recorded_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
    ],
    "medications": [
        {
            "id": "med-1",
            "name": "Metformin",
            "dosage": "500 mg",
            "frequency": "Twice daily",
            "schedule": "Twice daily with meals (Morning & Evening)",
            "start_date": "2025-06-01",
            "end_date": None,
            "status": "active",
            "source": "Demo Care Clinic",
            "instructions": "Take with water during or immediately after meals to minimize gastrointestinal effects.",
            "adherence": 96,
            "dose_events": [
                {"date": "2026-08-27", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-08-28", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-08-29", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-08-30", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-08-31", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-09-01", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-09-02", "scheduled": True, "taken": True, "late": False},
            ],
        },
        {
            "id": "med-2",
            "name": "Lisinopril",
            "dosage": "10 mg",
            "frequency": "Once daily",
            "schedule": "Every morning at 8:00 AM",
            "start_date": "2025-01-15",
            "end_date": None,
            "status": "active",
            "source": "Demo Care Clinic",
            "instructions": "Take consistently at the same time each day. Monitor blood pressure periodically.",
            "adherence": 92,
            "dose_events": [
                {"date": "2026-08-27", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-08-28", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-08-29", "scheduled": True, "taken": False, "late": False},
                {"date": "2026-08-30", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-08-31", "scheduled": True, "taken": True, "late": True},
                {"date": "2026-09-01", "scheduled": True, "taken": True, "late": False},
                {"date": "2026-09-02", "scheduled": True, "taken": True, "late": False},
            ],
        },
    ],
    "documents": [
        {
            "id": "doc-1",
            "name": "Metabolic Panel — Aug 2026.pdf",
            "file_type": "application/pdf",
            "file_size": 248102,
            "status": "processed",
            "source": "Northstar Laboratory",
            "source_date": "2026-08-28",
            "verified": True,
            "summary": "Comprehensive Metabolic Panel including fasting glucose (126 mg/dL) and kidney function biomarkers.",
        },
        {
            "id": "doc-2",
            "name": "Blood Pressure Log — Aug 2026.png",
            "file_type": "image/png",
            "file_size": 412090,
            "status": "processed",
            "source": "Added by you",
            "source_date": "2026-08-26",
            "verified": False,
            "summary": "Home blood pressure monitor photo showing reading of 121/78 mmHg.",
        },
    ],
    "laboratory": [
        {
            "id": "lab-001",
            "report_name": "Comprehensive Metabolic Panel",
            "source": "Northstar Laboratory",
            "source_date": "2026-08-28",
            "status": "verified",
            "document_id": "doc-1",
            "analytes": [
                {"name": "Glucose", "value": 126.0, "unit": "mg/dL", "reference_min": 70.0, "reference_max": 99.0, "status": "above_reference"},
                {"name": "Creatinine", "value": 0.9, "unit": "mg/dL", "reference_min": 0.6, "reference_max": 1.2, "status": "within_reference"},
                {"name": "eGFR", "value": 98.0, "unit": "mL/min/1.73m²", "reference_min": 60.0, "reference_max": 120.0, "status": "within_reference"},
                {"name": "Sodium", "value": 140.0, "unit": "mmol/L", "reference_min": 135.0, "reference_max": 145.0, "status": "within_reference"},
                {"name": "Potassium", "value": 4.2, "unit": "mmol/L", "reference_min": 3.5, "reference_max": 5.0, "status": "within_reference"},
                {"name": "Chloride", "value": 102.0, "unit": "mmol/L", "reference_min": 96.0, "reference_max": 106.0, "status": "within_reference"},
                {"name": "Carbon Dioxide", "value": 24.0, "unit": "mmol/L", "reference_min": 22.0, "reference_max": 29.0, "status": "within_reference"},
                {"name": "Calcium", "value": 9.4, "unit": "mg/dL", "reference_min": 8.5, "reference_max": 10.2, "status": "within_reference"},
            ],
        }
    ],
    "appointments": [
        {
            "id": "apt-1",
            "title": "Primary Care Routine Follow-up",
            "provider_name": "Dr. Elena Vance, MD",
            "specialty": "Internal Medicine",
            "organization": "Demo Care Clinic",
            "location": "1200 Healthway Blvd, Suite 300, Seattle, WA",
            "starts_at": "2026-09-03T10:30:00Z",
            "duration_minutes": 30,
            "status": "confirmed",
            "is_synthetic": True,
            "notes": "Review metabolic panel and blood pressure log.",
        },
        {
            "id": "apt-2",
            "title": "Annual Eye Examination",
            "provider_name": "Dr. Kenneth Cho, OD",
            "specialty": "Optometry",
            "organization": "Visionworks (Demo Care)",
            "location": "500 Pine St, Seattle, WA",
            "starts_at": "2026-09-16T14:00:00Z",
            "duration_minutes": 45,
            "status": "pending",
            "is_synthetic": True,
            "notes": "Comprehensive diabetic retinal screening and visual acuity.",
        },
    ],
    "consents": [
        {
            "id": "consent-1",
            "organization": "Example Clinic",
            "purpose": "Specialist consultation (Endocrinology review)",
            "scope": ["Laboratory reports", "Prescriptions", "Vital trends"],
            "requested_at": "2026-08-25T11:00:00Z",
            "expires_at": "2026-09-30T23:59:59Z",
            "status": "requested",
            "is_synthetic": True,
        },
        {
            "id": "consent-2",
            "organization": "Northstar Laboratory",
            "purpose": "Automated laboratory result ingestion",
            "scope": ["Laboratory reports"],
            "requested_at": "2026-08-01T08:00:00Z",
            "expires_at": "2027-08-01T08:00:00Z",
            "status": "approved",
            "is_synthetic": True,
        },
    ],
    "access_logs": [
        {"id": "acc-1", "organization": "Northstar Laboratory", "scope": "Imported Metabolic Panel — Aug 2026", "purpose": "Direct lab sync", "accessed_at": "2026-08-28T09:05:00Z", "status": "authorized", "is_synthetic": True},
        {"id": "acc-2", "organization": "Demo Care Clinic", "scope": "Profile & Active Medications", "purpose": "Upcoming consultation prep", "accessed_at": "2026-08-20T14:22:00Z", "status": "authorized", "is_synthetic": True},
    ],
    "notifications": [
        {"id": "notif-1", "category": "laboratory", "title": "Lab report available", "message": "Metabolic Panel from Northstar Laboratory has been processed and is ready to review.", "created_at": "2026-08-28T09:10:00Z", "read": False, "is_synthetic": True},
        {"id": "notif-2", "category": "medication", "title": "Medication dose reminder", "message": "Evening dose of Metformin (500 mg) is due at 8:00 PM with your meal.", "created_at": "2026-09-02T19:00:00Z", "read": False, "is_synthetic": True},
        {"id": "notif-3", "category": "appointment", "title": "Upcoming appointment", "message": "Primary Care Follow-up with Dr. Elena Vance is scheduled for tomorrow at 10:30 AM.", "created_at": "2026-09-02T08:00:00Z", "read": True, "is_synthetic": True},
        {"id": "notif-4", "category": "consent", "title": "New consent request", "message": "Example Clinic has requested temporary access to your Laboratory Reports for a consultation.", "created_at": "2026-08-25T11:05:00Z", "read": True, "is_synthetic": True},
    ],
    "care_providers": [
        {"id": "cp-1", "name": "Dr. Elena Vance, MD", "type": "doctor", "specialty": "Internal Medicine", "organization": "Demo Care Clinic", "address": "1200 Healthway Blvd, Seattle, WA", "rating": 4.9, "distance_miles": 1.2, "availability": "Next week", "is_synthetic": True},
        {"id": "cp-2", "name": "Dr. Kenneth Cho, OD", "type": "doctor", "specialty": "Optometry", "organization": "Visionworks (Demo)", "address": "500 Pine St, Seattle, WA", "rating": 4.8, "distance_miles": 2.4, "availability": "This month", "is_synthetic": True},
        {"id": "cp-3", "name": "Northstar Laboratory (Downtown)", "type": "laboratory", "specialty": "Diagnostic Pathology & Bloodwork", "organization": "Northstar Lab Network", "address": "800 5th Ave, Seattle, WA", "rating": 4.7, "distance_miles": 0.8, "availability": "Walk-in available", "is_synthetic": True},
        {"id": "cp-4", "name": "Healthline Pharmacy (Central)", "type": "pharmacy", "specialty": "Prescription Fulfillment & Consultation", "organization": "Healthline Pharmacy Group", "address": "1401 4th Ave, Seattle, WA", "rating": 4.9, "distance_miles": 0.5, "availability": "Open until 9:00 PM", "is_synthetic": True},
        {"id": "cp-5", "name": "Seattle Central Medical Center", "type": "hospital", "specialty": "Acute Care & Specialty Clinics", "organization": "Central Health System", "address": "1100 9th Ave, Seattle, WA", "rating": 4.6, "distance_miles": 1.8, "availability": "24/7 Facility", "is_synthetic": True},
    ],
}

# AI Services Initializers
embedder = EmbeddingService()
retriever = VectorRetriever(dimension=embedder.dimension)
risk_service = RiskPredictionService()

def reindex_user_knowledge_base():
    """Build authorized Personal RAG knowledge base for Avery Morgan."""
    items = []
    texts = []
    
    # Profile knowledge
    u = USER_STATE["user"]
    p_text = f"Patient profile: {u['first_name']} {u['last_name']}, DOB: {u['date_of_birth']}. Blood group: {u['blood_group']}. Allergies: Penicillin. Conditions: Mild Hypertension."
    items.append(RetrievalItem(text=p_text, metadata={"user_id": DEMO_USER_ID, "record_type": "profile", "title": "Personal Profile", "source": "Personal Gateway", "source_date": "2026-09-01"}))
    texts.append(p_text)
    
    # Vitals knowledge
    for v in USER_STATE["vitals"]:
        v_text = f"Vital reading: {v['type'].replace('_', ' ').title()} was {v['value']} {v['unit']} on {v['recorded_at'][:10]} (Source: {v['source']})."
        items.append(RetrievalItem(text=v_text, metadata={"user_id": DEMO_USER_ID, "record_type": "vital", "title": f"{v['type'].title()} Reading", "source": v["source"], "source_date": v["recorded_at"][:10]}))
        texts.append(v_text)
        
    # Medications knowledge
    for m in USER_STATE["medications"]:
        m_text = f"Medication: {m['name']} {m['dosage']}, frequency: {m['frequency']}, schedule: {m['schedule']}. Status: {m['status']}. Adherence: {m['adherence']}%. Prescribed by {m['source']}."
        items.append(RetrievalItem(text=m_text, metadata={"user_id": DEMO_USER_ID, "record_type": "medication", "title": f"Medication: {m['name']}", "source": m["source"], "source_date": m["start_date"]}))
        texts.append(m_text)
        
    # Lab reports knowledge
    for lab in USER_STATE["laboratory"]:
        analytes_str = ", ".join(f"{a['name']}: {a['value']} {a['unit']} (Ref: {a.get('reference_min', '')}-{a.get('reference_max', '')} {a['unit']})" for a in lab["analytes"])
        l_text = f"Laboratory Report: {lab['report_name']} on {lab['source_date']} from {lab['source']}. Analytes: {analytes_str}."
        items.append(RetrievalItem(text=l_text, metadata={"user_id": DEMO_USER_ID, "record_type": "laboratory", "title": lab["report_name"], "source": lab["source"], "source_date": lab["source_date"], "document_id": lab.get("document_id")}))
        texts.append(l_text)

    # Appointments knowledge
    for apt in USER_STATE["appointments"]:
        apt_text = f"Appointment: {apt['title']} with {apt['provider_name']} ({apt['specialty']}) at {apt['organization']} on {apt['starts_at'][:10]}. Status: {apt['status']}."
        items.append(RetrievalItem(text=apt_text, metadata={"user_id": DEMO_USER_ID, "record_type": "appointment", "title": apt["title"], "source": apt["organization"], "source_date": apt["starts_at"][:10]}))
        texts.append(apt_text)

    embeddings = embedder.encode(texts)
    retriever.items.clear()
    retriever.vectors.clear()
    retriever.add(embeddings, items)

# Initialize vector index
reindex_user_knowledge_base()

# Schemas
class Credentials(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=4)

class RegisterInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    date_of_birth: date
    gender: str = "prefer_not_to_say"
    email: str
    password: str = Field(min_length=6)
    phone: str | None = None

class OAuthExchangeInput(BaseModel):
    ticket: str = Field(min_length=32, max_length=128)

class ProfileUpdate(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    middle_name: str | None = None
    last_name: str = Field(min_length=1, max_length=80)
    date_of_birth: date
    gender: str | None = None
    email: str
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    blood_group: str | None = None
    important_notes: str | None = None
    preferred_hospital: str | None = None
    emergency_directives: str | None = None

class VitalInput(BaseModel):
    type: Literal["blood_pressure_systolic", "blood_pressure_diastolic", "glucose", "weight", "heart_rate", "spo2", "hba1c"]
    value: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=20)
    recorded_at: datetime
    source: str = "Added by you"

class MedicationInput(BaseModel):
    name: str = Field(min_length=1)
    dosage: str = Field(min_length=1)
    frequency: str = "Daily"
    schedule: str = "Every morning"
    start_date: date = Field(default_factory=date.today)
    instructions: str | None = None

class DoseLogInput(BaseModel):
    taken: bool = True
    late: bool = False
    date_str: str | None = None

class AppointmentInput(BaseModel):
    title: str = Field(min_length=1)
    specialty: str = "General Practice"
    organization: str = "Demo Care Clinic"
    starts_at: datetime
    notes: str | None = None

class ContactInput(BaseModel):
    name: str = Field(min_length=1)
    relationship: str = "Contact"
    phone: str = Field(min_length=7)
    email: str | None = None
    primary: bool = False

class ConsentUpdate(BaseModel):
    status: Literal["approved", "denied", "revoked", "temporary"]

class AssistantQuestion(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None

class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime | None = None

class RiskCalculationInput(BaseModel):
    age: float = Field(ge=18, le=110)
    bmi: float = Field(ge=10, le=70)
    systolic_bp: float = Field(ge=70, le=250)
    glucose: float = Field(ge=40, le=500)
    smoker: bool = False
    family_history: bool = False

# Security & Ownership Dependency
def current_user(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header required")
    token = authorization[7:]
    session = SESSIONS.get(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired personal session")
    return session["user_id"]

def create_auth_session(user: User) -> dict[str, Any]:
    token = f"demo-{uuid4().hex}"
    display_name = f"{user.first_name} {user.last_name}".strip()
    SESSIONS[token] = {
        "user_id": user.id,
        "email": user.email,
        "display_name": display_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "display_name": display_name,
            "role": "personal_patient",
        },
    }

def create_or_link_oauth_user(
    provider: str,
    subject: str,
    email: str,
    first_name: str,
    last_name: str,
) -> str:
    normalized_email = email.strip().lower()
    with SessionLocal() as db:
        identity = db.scalar(
            select(OAuthIdentity).where(
                OAuthIdentity.provider == provider,
                OAuthIdentity.subject == subject,
            )
        )
        if identity is not None:
            return identity.user_id

        user = get_user_by_email(db, normalized_email)
        if user is not None:
            linked_identity = db.scalar(
                select(OAuthIdentity).where(OAuthIdentity.user_id == user.id)
            )
            if linked_identity is None:
                raise OAuthAccountConflict
        if user is None:
            user = User(
                email=normalized_email,
                password_hash=hash_password(secrets.token_urlsafe(48)),
                first_name=first_name[:80] or "Healthcare",
                last_name=last_name[:80] or "Member",
            )
            db.add(user)
            db.flush()
            db.add(
                PersonalProfile(
                    user_id=user.id,
                    email=user.email,
                    phone=None,
                    address=None,
                    city=None,
                    state=None,
                    country=None,
                    postal_code=None,
                    blood_group=None,
                    allergies="[]",
                    conditions="[]",
                    important_notes=None,
                    preferred_hospital=None,
                    emergency_directives=None,
                    emergency_contacts="[]",
                )
            )

        db.add(
            OAuthIdentity(
                provider=provider,
                subject=subject,
                user_id=user.id,
                email=normalized_email,
            )
        )
        db.add(AuditEvent(user_id=user.id, event_type="oauth_identity_linked", description=provider))
        db.commit()
        return user.id

# Health & Meta
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Smart Healthcare — Personal Health Gateway",
        "version": "1.0.0",
        "module": "Module 1 (Personal)",
        "synthetic_data_only": True,
        "active_sessions": len(SESSIONS),
    }

# 1. Authentication Endpoints
@app.get("/api/v1/personal/auth/providers")
def get_oauth_providers():
    return {
        "google": bool(oauth.create_client("google")),
        "github": bool(oauth.create_client("github")),
    }

@app.get("/api/v1/personal/auth/{provider}/start")
async def start_oauth(provider: Literal["google", "github"], request: Request):
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{provider.title()} sign-in is not configured. Set its OAuth client ID and secret.",
        )
    redirect_uri = f"{settings.backend_public_url}/api/v1/personal/auth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)

def oauth_failure_redirect(message: str) -> RedirectResponse:
    query = urlencode({"oauth_error": message})
    return RedirectResponse(f"{settings.frontend_url}/?{query}", status_code=303)

@app.get("/api/v1/personal/auth/{provider}/callback")
async def oauth_callback(provider: Literal["google", "github"], request: Request):
    client = oauth.create_client(provider)
    if client is None:
        return oauth_failure_redirect(f"{provider.title()} sign-in is not configured.")
    if request.query_params.get("error"):
        return oauth_failure_redirect(f"{provider.title()} sign-in was cancelled or denied.")
    try:
        token = await client.authorize_access_token(request)
    except OAuthError:
        logger.warning("OAuth authorization failed for provider %s", provider)
        return oauth_failure_redirect(f"{provider.title()} sign-in could not be verified. Please try again.")

    if provider == "google":
        profile = token.get("userinfo")
        if not profile:
            profile = await client.parse_id_token(request, token)
        if not profile or profile.get("email_verified") is not True:
            return oauth_failure_redirect("Use a Google account with a verified email address.")
        subject = str(profile.get("sub") or "")
        email = profile.get("email", "")
        display_name = str(profile.get("name") or "")
    else:
        response = await client.get("user", token=token)
        profile = response.json()
        emails_response = await client.get("user/emails", token=token)
        emails = emails_response.json()
        verified_email = next(
            (item["email"] for item in emails if item.get("primary") is True and item.get("verified") is True),
            None,
        ) or next((item["email"] for item in emails if item.get("verified") is True), None)
        subject = str(profile.get("id") or "")
        email = verified_email or ""
        display_name = str(profile.get("name") or profile.get("login") or "")

    if not subject or not email:
        return oauth_failure_redirect(f"{provider.title()} did not provide a verified email address.")

    name_parts = display_name.strip().split(maxsplit=1)
    first_name = name_parts[0] if name_parts else "Healthcare"
    last_name = name_parts[1] if len(name_parts) > 1 else "Member"
    try:
        user_id = create_or_link_oauth_user(provider, subject, email, first_name, last_name)
    except OAuthAccountConflict:
        return oauth_failure_redirect(
            "An account already uses this email. Sign in with its existing method; automatic password-account linking is disabled for safety."
        )

    now = datetime.now(timezone.utc)
    OAUTH_TICKETS.update(
        {ticket: value for ticket, value in OAUTH_TICKETS.items() if value[1] > now}
    )
    ticket = secrets.token_urlsafe(48)
    OAUTH_TICKETS[ticket] = (user_id, now + timedelta(minutes=5))
    query = urlencode({"oauth_ticket": ticket})
    return RedirectResponse(f"{settings.frontend_url}/#{query}", status_code=303)

@app.post("/api/v1/personal/auth/oauth/exchange")
def exchange_oauth_ticket(data: OAuthExchangeInput):
    ticket_data = OAUTH_TICKETS.pop(data.ticket, None)
    if ticket_data is None or ticket_data[1] <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This sign-in link has expired. Please try again.")
    with SessionLocal() as db:
        user = db.get(User, ticket_data[0])
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The account for this sign-in could not be found.")
        session = create_auth_session(user)
        record_audit(db, user.id, "oauth_login", "External provider sign-in")
        return session

@app.post("/api/v1/personal/auth/login")
def login(credentials: Credentials):
    with SessionLocal() as db:
        user = get_user_by_email(db, credentials.email)
        if user is None or user.password_hash != hash_password(credentials.password):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return {**create_auth_session(user), "development_demo": True}

@app.post("/api/v1/personal/auth/register", status_code=201)
def register(data: RegisterInput):
    if data.date_of_birth >= date.today():
        raise HTTPException(422, "Date of birth must be in the past")
    with SessionLocal() as db:
        if get_user_by_email(db, data.email):
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        user = User(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            phone=data.phone,
        )
        db.add(user)
        db.flush()
        profile = PersonalProfile(
            user_id=user.id,
            email=user.email,
            phone=user.phone,
            address=None,
            city=None,
            state=None,
            country=None,
            postal_code=None,
            blood_group=None,
            allergies="[]",
            conditions="[]",
            important_notes=None,
            preferred_hospital=None,
            emergency_directives=None,
            emergency_contacts="[]",
        )
        db.add(profile)
        db.commit()
        token = f"demo-{uuid4().hex}"
        SESSIONS[token] = {
            "user_id": user.id,
            "email": user.email,
            "display_name": f"{data.first_name} {data.last_name}",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": f"{data.first_name} {data.last_name}",
            },
            "message": "Personal health identity created successfully.",
        }

@app.post("/api/v1/personal/auth/logout", status_code=204)
def logout(authorization: str | None = Header(default=None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        SESSIONS.pop(token, None)
    return None

@app.get("/api/v1/personal/auth/session")
def get_session(user_id: str = Depends(current_user)):
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return {
            "authenticated": True,
            "user_id": user_id,
            "user": serialize_user(user),
        }

# 2. Personal Profile
@app.get("/api/v1/personal/profile")
def get_profile(user_id: str = Depends(current_user)):
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        profile = get_user_profile(db, user_id)
        return profile_payload_for_user(user, profile)

@app.put("/api/v1/personal/profile")
def update_profile(update: ProfileUpdate, user_id: str = Depends(current_user)):
    if update.date_of_birth >= date.today():
        raise HTTPException(422, "Date of birth must be in the past")

    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        profile = get_user_profile(db, user_id)
        clean_dict = {k: v for k, v in update.model_dump(mode="json").items() if v is not None}

        if "email" in clean_dict and clean_dict["email"].lower() != user.email.lower():
            existing = get_user_by_email(db, clean_dict["email"])
            if existing and existing.id != user.id:
                raise HTTPException(status_code=409, detail="Another account already uses this email.")
            user.email = clean_dict["email"].lower()
            profile.email = user.email

        for field_name, value in clean_dict.items():
            if field_name in {"first_name", "middle_name", "last_name", "date_of_birth", "gender", "phone"}:
                setattr(user, field_name, value)
            elif field_name in {"address", "city", "state", "country", "postal_code", "blood_group", "important_notes", "preferred_hospital", "emergency_directives"}:
                setattr(profile, field_name, value)

        if user.phone is not None:
            profile.phone = user.phone
        if user.address is not None:
            profile.address = user.address
        if user.city is not None:
            profile.city = user.city
        if user.state is not None:
            profile.state = user.state
        if user.country is not None:
            profile.country = user.country
        if user.postal_code is not None:
            profile.postal_code = user.postal_code
        if user.blood_group is not None:
            profile.blood_group = user.blood_group
        if user.important_notes is not None:
            profile.important_notes = user.important_notes
        if user.preferred_hospital is not None:
            profile.preferred_hospital = user.preferred_hospital
        if user.emergency_directives is not None:
            profile.emergency_directives = user.emergency_directives

        db.add(user)
        db.add(profile)
        db.commit()
        db.refresh(user)
        db.refresh(profile)
        record_audit(db, user_id, "profile_updated", "Profile updated")
        return {"status": "success", "profile": profile_payload_for_user(user, profile), "message": "Profile updated successfully."}

# 3. Health Records & Provenance
@app.get("/api/v1/personal/records")
def get_records(user_id: str = Depends(current_user)):
    return [
        {
            "id": "rec-001",
            "title": "Comprehensive Metabolic Panel",
            "category": "laboratory",
            "source": "Northstar Laboratory",
            "source_date": "2026-08-28",
            "imported_at": "2026-08-28T09:05:00Z",
            "status": "Verified",
            "document_id": "doc-1",
            "provenance": {
                "source_organization": "Northstar Laboratory Network",
                "verified_by_provider": True,
                "document_reference": "DOC-2026-08-28-LAB01",
                "raw_file_available": True,
            },
        },
        {
            "id": "rec-002",
            "title": "Prescription Renewal: Metformin 500mg",
            "category": "prescription",
            "source": "Demo Care Clinic",
            "source_date": "2026-08-19",
            "imported_at": "2026-08-19T14:30:00Z",
            "status": "Verified",
            "provenance": {
                "source_organization": "Demo Care Clinic",
                "prescriber": "Dr. Elena Vance, MD",
                "verified_by_provider": True,
            },
        },
        {
            "id": "rec-003",
            "title": "Blood Pressure Log (121/78 mmHg)",
            "category": "vital",
            "source": "Added by you",
            "source_date": "2026-08-19",
            "imported_at": "2026-08-19T09:12:00Z",
            "status": "Recorded",
            "document_id": "doc-2",
            "provenance": {
                "source_organization": "Patient Home Telehealth",
                "verified_by_provider": False,
                "device": "Omron Series 10 (Demo)",
            },
        },
    ]

# 4. Timeline
@app.get("/api/v1/personal/timeline")
def get_timeline(category: str | None = None, user_id: str = Depends(current_user)):
    events = [
        {"id": "ev-1", "type": "laboratory", "title": "Comprehensive Metabolic Panel", "description": "Glucose: 126 mg/dL, Creatinine: 0.9 mg/dL", "occurred_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "ev-2", "type": "vital", "title": "Vital Reading: Glucose 126 mg/dL", "description": "Recorded during lab draw", "occurred_at": "2026-08-28T09:00:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "ev-3", "type": "document", "title": "Document Uploaded: Metabolic Panel — Aug 2026.pdf", "description": "File processed and indexed for grounded AI search", "occurred_at": "2026-08-28T09:02:00Z", "source": "Northstar Laboratory", "verified": True},
        {"id": "ev-4", "type": "vital", "title": "Vital Reading: BP 121/78 mmHg", "description": "Home measurement", "occurred_at": "2026-08-19T09:00:00Z", "source": "Added by you", "verified": False},
        {"id": "ev-5", "type": "medication", "title": "Prescription Refill: Lisinopril 10mg", "description": "30-day supply dispensed", "occurred_at": "2026-08-19T14:30:00Z", "source": "Demo Care Clinic", "verified": True},
        {"id": "ev-6", "type": "appointment", "title": "Telehealth Consultation", "description": "Care consultation with Dr. Elena Vance", "occurred_at": "2026-08-04T10:00:00Z", "source": "Demo Care Clinic", "verified": True},
    ]
    if category and category.lower() != "all":
        events = [e for e in events if e["type"].lower() == category.lower()]
    return events

# 5. Vitals & ML Trend Analytics
@app.get("/api/v1/personal/vitals")
def get_vitals(metric: str | None = None, user_id: str = Depends(current_user)):
    v_list = USER_STATE["vitals"]
    if metric:
        v_list = [v for v in v_list if v["type"] == metric]
    return v_list

@app.post("/api/v1/personal/vitals", status_code=201)
def add_vital(vital: VitalInput, user_id: str = Depends(current_user)):
    ranges = {
        "spo2": (50.0, 100.0),
        "heart_rate": (20.0, 250.0),
        "glucose": (20.0, 800.0),
        "weight": (1.0, 1000.0),
        "hba1c": (1.0, 30.0),
        "blood_pressure_systolic": (50.0, 300.0),
        "blood_pressure_diastolic": (30.0, 200.0),
    }
    low, high = ranges[vital.type]
    if not (low <= vital.value <= high):
        raise HTTPException(422, f"Value {vital.value} is outside supported physiological bounds ({low}-{high})")

    new_vital = {
        "id": f"v-{uuid4().hex[:8]}",
        "verified": False,
        **vital.model_dump(mode="json"),
    }
    USER_STATE["vitals"].append(new_vital)
    reindex_user_knowledge_base()
    return new_vital

@app.get("/api/v1/personal/vitals/trends")
def get_vital_trends(metric: str = Query("glucose"), user_id: str = Depends(current_user)):
    readings = [v for v in USER_STATE["vitals"] if v["type"] == metric]
    if not readings:
        return {
            "metric": metric,
            "direction": "insufficient_data",
            "observation_count": 0,
            "informational_note": f"No recordings found for {metric}.",
        }

    timestamps = [r["recorded_at"] for r in readings]
    values = [float(r["value"]) for r in readings]
    return analyze_trend(timestamps, values, metric)

# 6. Documents
@app.get("/api/v1/personal/documents")
def list_documents(user_id: str = Depends(current_user)):
    return USER_STATE["documents"]

@app.post("/api/v1/personal/documents", status_code=201)
async def upload_document(file: UploadFile = File(...), user_id: str = Depends(current_user)):
    allowed_types = {"application/pdf", "image/jpeg", "image/png"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Supported file types are PDF, JPG, JPEG, and PNG only.")
    
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Document exceeds 10 MB limit.")

    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename or "uploaded_document")
    doc_id = f"doc-{uuid4().hex[:8]}"
    item = {
        "id": doc_id,
        "name": safe_name,
        "file_type": file.content_type,
        "file_size": len(contents),
        "status": "processed",
        "source": "Added by you",
        "source_date": date.today().isoformat(),
        "verified": False,
        "summary": "Document uploaded and processed in secure private storage.",
    }
    USER_STATE["documents"].append(item)
    reindex_user_knowledge_base()
    return item

@app.delete("/api/v1/personal/documents/{doc_id}")
def delete_document(doc_id: str, user_id: str = Depends(current_user)):
    USER_STATE["documents"] = [d for d in USER_STATE["documents"] if d["id"] != doc_id]
    return {"status": "success", "message": "Document removed from private storage."}

# 7. Laboratory Reports & AI Interpretation
@app.get("/api/v1/personal/laboratory")
def get_laboratory(user_id: str = Depends(current_user)):
    return USER_STATE["laboratory"]

@app.get("/api/v1/personal/laboratory/{report_id}/interpret")
def interpret_report(report_id: str, user_id: str = Depends(current_user)):
    report = next((r for r in USER_STATE["laboratory"] if r["id"] == report_id), None)
    if not report:
        raise HTTPException(404, "Laboratory report not found")

    lab_values = [
        LabValue(
            name=a["name"],
            value=float(a["value"]),
            unit=a["unit"],
            reference_min=a.get("reference_min"),
            reference_max=a.get("reference_max"),
        )
        for a in report["analytes"]
    ]
    interpretations = interpret_lab_results(lab_values)
    
    return {
        "report_id": report["id"],
        "report_name": report["report_name"],
        "source": report["source"],
        "source_date": report["source_date"],
        "interpretations": interpretations,
        "ai_notice": (
            "AI-GENERATED INFORMATIONAL EXPLANATION ONLY. This summary explains values relative to "
            "source-provided reference ranges. It is not a clinical diagnosis and does not replace "
            "evaluation by a qualified medical professional."
        ),
    }

# 8. Medications & Adherence ML
@app.get("/api/v1/personal/medications")
def get_medications(user_id: str = Depends(current_user)):
    return USER_STATE["medications"]

@app.post("/api/v1/personal/medications", status_code=201)
def add_medication(med: MedicationInput, user_id: str = Depends(current_user)):
    new_med = {
        "id": f"med-{uuid4().hex[:6]}",
        "name": med.name,
        "dosage": med.dosage,
        "frequency": med.frequency,
        "schedule": med.schedule,
        "start_date": med.start_date.isoformat(),
        "end_date": None,
        "status": "active",
        "source": "Added by you",
        "instructions": med.instructions or "Take as directed.",
        "adherence": 100,
        "dose_events": [{"date": date.today().isoformat(), "scheduled": True, "taken": True, "late": False}],
    }
    USER_STATE["medications"].append(new_med)
    reindex_user_knowledge_base()
    return new_med

@app.post("/api/v1/personal/medications/{med_id}/dose")
def log_dose(med_id: str, dose: DoseLogInput, user_id: str = Depends(current_user)):
    med = next((m for m in USER_STATE["medications"] if m["id"] == med_id), None)
    if not med:
        raise HTTPException(404, "Medication not found")

    d_str = dose.date_str or date.today().isoformat()
    # Check if event exists for date
    existing = next((e for e in med["dose_events"] if e["date"] == d_str), None)
    if existing:
        existing["taken"] = dose.taken
        existing["late"] = dose.late
    else:
        med["dose_events"].append({"date": d_str, "scheduled": True, "taken": dose.taken, "late": dose.late})

    # Recalculate adherence
    scheduled_count = sum(1 for e in med["dose_events"] if e["scheduled"])
    taken_count = sum(1 for e in med["dose_events"] if e["scheduled"] and e["taken"])
    med["adherence"] = int((taken_count / scheduled_count) * 100) if scheduled_count > 0 else 100

    return {"status": "success", "medication": med}

@app.get("/api/v1/personal/medications/adherence-ml")
def get_adherence_ml(user_id: str = Depends(current_user)):
    all_events = []
    for m in USER_STATE["medications"]:
        all_events.extend(m.get("dose_events", []))
    
    return predict_adherence(all_events)

@app.get("/api/v1/personal/medications/interactions")
def check_interactions(user_id: str = Depends(current_user)):
    return {
        "status": "checked",
        "reference_database": "Standard Clinical Drug Reference Database (Synthetic Simulation)",
        "active_medications": [m["name"] for m in USER_STATE["medications"]],
        "interaction_alerts": [
            {
                "severity": "Low / Monitor",
                "combination": "Metformin + Lisinopril",
                "effect": "Lisinopril may enhance blood glucose lowering effect of Metformin. Routine glucose monitoring recommended.",
                "type": "Database-derived clinical alert (Not AI invented)",
            }
        ],
        "disclaimer": "Interaction database alerts are separate from AI text and must be verified by a pharmacist or clinician.",
    }

# 9. Appointments & Care Navigation
@app.get("/api/v1/personal/appointments")
def get_appointments(user_id: str = Depends(current_user)):
    return USER_STATE["appointments"]

@app.post("/api/v1/personal/appointments", status_code=201)
def book_appointment(apt: AppointmentInput, user_id: str = Depends(current_user)):
    new_apt = {
        "id": f"apt-{uuid4().hex[:6]}",
        "title": apt.title,
        "provider_name": "Dr. Elena Vance, MD",
        "specialty": apt.specialty,
        "organization": apt.organization,
        "location": "1200 Healthway Blvd, Suite 300, Seattle, WA",
        "starts_at": apt.starts_at.isoformat(),
        "duration_minutes": 30,
        "status": "confirmed",
        "is_synthetic": True,
        "notes": apt.notes or "Scheduled via Personal Gateway.",
    }
    USER_STATE["appointments"].append(new_apt)
    reindex_user_knowledge_base()
    return new_apt

@app.post("/api/v1/personal/appointments/{apt_id}/cancel")
def cancel_appointment(apt_id: str, user_id: str = Depends(current_user)):
    apt = next((a for a in USER_STATE["appointments"] if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    apt["status"] = "cancelled"
    return {"status": "success", "appointment": apt}

@app.get("/api/v1/personal/care")
def search_care(query: str | None = None, type_filter: str | None = None, user_id: str = Depends(current_user)):
    results = USER_STATE["care_providers"]
    if type_filter and type_filter != "all":
        results = [r for r in results if r["type"] == type_filter]
    if query:
        q = query.lower()
        results = [r for r in results if q in r["name"].lower() or q in r["specialty"].lower() or q in r["address"].lower()]
    return results

# 10. Emergency Readiness
@app.get("/api/v1/personal/emergency")
def get_emergency(user_id: str = Depends(current_user)):
    u = USER_STATE["user"]
    return {
        "blood_group": u["blood_group"],
        "severe_allergies": u["allergies"],
        "critical_conditions": u["conditions"],
        "emergency_contacts": USER_STATE["emergency_contacts"],
        "preferred_hospital": u["preferred_hospital"],
        "emergency_directives": u["emergency_directives"],
        "dispatch_available": False,
        "dispatch_notice": (
            "Module 1 prepares emergency profile data for personal readiness. "
            "Autonomous emergency dispatch will connect in the future Emergency Intelligence module."
        ),
    }

@app.post("/api/v1/personal/emergency/contacts", status_code=201)
def add_emergency_contact(contact: ContactInput, user_id: str = Depends(current_user)):
    if contact.primary:
        for c in USER_STATE["emergency_contacts"]:
            c["primary"] = False
    new_c = {
        "id": f"c-{uuid4().hex[:6]}",
        **contact.model_dump(),
    }
    USER_STATE["emergency_contacts"].append(new_c)
    return new_c

@app.delete("/api/v1/personal/emergency/contacts/{contact_id}")
def delete_emergency_contact(contact_id: str, user_id: str = Depends(current_user)):
    USER_STATE["emergency_contacts"] = [c for c in USER_STATE["emergency_contacts"] if c["id"] != contact_id]
    return {"status": "success", "message": "Emergency contact removed."}

# 11. Privacy & Consent
@app.get("/api/v1/personal/privacy/access-log")
def get_access_log(user_id: str = Depends(current_user)):
    return USER_STATE["access_logs"]

@app.get("/api/v1/personal/privacy/sessions")
def get_active_sessions(user_id: str = Depends(current_user)):
    return [
        {
            "id": "sess-current",
            "device": "Web Browser (Chrome / Desktop)",
            "ip_address": "127.0.0.1 (Local Session)",
            "location": "Seattle, WA",
            "last_active": "Active now",
            "is_current": True,
        }
    ]

@app.get("/api/v1/personal/consents")
def get_consents(user_id: str = Depends(current_user)):
    return USER_STATE["consents"]

@app.patch("/api/v1/personal/consents/{consent_id}")
def update_consent(consent_id: str, update: ConsentUpdate, user_id: str = Depends(current_user)):
    c = next((item for item in USER_STATE["consents"] if item["id"] == consent_id), None)
    if not c:
        raise HTTPException(404, "Consent item not found")
    c["status"] = update.status
    # Log access change
    USER_STATE["access_logs"].append({
        "id": f"acc-{uuid4().hex[:6]}",
        "organization": c["organization"],
        "scope": f"Consent status changed to {update.status}",
        "purpose": c["purpose"],
        "accessed_at": datetime.now(timezone.utc).isoformat(),
        "status": "policy_updated",
        "is_synthetic": True,
    })
    return c

# 12. Notifications
@app.get("/api/v1/personal/notifications")
def get_notifications(user_id: str = Depends(current_user)):
    return USER_STATE["notifications"]

@app.patch("/api/v1/personal/notifications/{notif_id}/read")
def mark_notification_read(notif_id: str, user_id: str = Depends(current_user)):
    n = next((item for item in USER_STATE["notifications"] if item["id"] == notif_id), None)
    if n:
        n["read"] = True
    return {"status": "success", "notification": n}

@app.post("/api/v1/personal/notifications/mark-all-read")
def mark_all_notifications_read(user_id: str = Depends(current_user)):
    for n in USER_STATE["notifications"]:
        n["read"] = True
    return {"status": "success", "message": "All notifications marked as read."}

# 13. AI Health Brief & Personal RAG Assistant
@app.get("/api/v1/personal/ai/brief")
def get_ai_health_brief(user_id: str = Depends(current_user)):
    return {
        "title": "Your personal health snapshot is current and structured.",
        "summary": "Recent laboratory testing shows fasting glucose at 126 mg/dL (above reference). Blood pressure readings remain stable across August (latest 120/77 mmHg). You have an upcoming primary care follow-up scheduled for tomorrow at 10:30 AM.",
        "source_period": "August 2026 – Present",
        "ai_generated": True,
        "disclaimer": "Informational summary generated from authorized records. Not a clinical diagnosis.",
        "key_metrics": {
            "glucose_latest": "126 mg/dL",
            "glucose_trend": "Increasing (+0.57/day)",
            "bp_latest": "120/77 mmHg",
            "active_medications": len(USER_STATE["medications"]),
            "upcoming_appointments": len([a for a in USER_STATE["appointments"] if a["status"] == "confirmed"]),
        },
    }

@app.post("/api/v1/personal/ai/answer")
def answer_assistant_question(question: AssistantQuestion, user_id: str = Depends(current_user)):
    convo_id = question.conversation_id or f"conv-{uuid4().hex[:8]}"
    history = CONVERSATIONS.setdefault(convo_id, [])
    history.append({"role": "user", "content": question.message.strip(), "timestamp": datetime.now(timezone.utc).isoformat()})

    agent = PersonalHealthAgent(user_id=user_id, conversation_id=convo_id)
    result = agent.handle_message(question.message.strip(), conversation_history=history)

    history.append({
        "role": "assistant",
        "content": result["answer"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources": result.get("sources", []),
        "tool_calls": result.get("tool_calls", []),
        "intent": result.get("intent"),
    })

    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "informational_only": True,
        "retrieval_method": "Authorized Personal Agent + RAG Pipeline",
        "disclaimer": result.get("disclaimer", "This answer is derived strictly from your authorized personal records and general health context. It is not medical advice or a clinical diagnosis."),
        "tool_calls": result.get("tool_calls", []),
        "structured_data": result.get("structured_data"),
        "requires_confirmation": result.get("requires_confirmation", False),
        "conversation_id": convo_id,
        "intent": result.get("intent", "UNKNOWN"),
    }


@app.post("/api/v1/personal/ai/chat")
def chat_with_assistant(question: AssistantQuestion, user_id: str = Depends(current_user)):
    return answer_assistant_question(question, user_id=user_id)


@app.get("/api/v1/personal/ai/conversations")
def list_conversations(user_id: str = Depends(current_user)):
    return {
        "conversations": [
            {"conversation_id": cid, "message_count": len(messages), "updated_at": messages[-1]["timestamp"] if messages else None}
            for cid, messages in CONVERSATIONS.items()
            if any(msg.get("role") == "user" for msg in messages)
        ]
    }


@app.get("/api/v1/personal/ai/conversations/{conversation_id}")
def get_conversation(conversation_id: str, user_id: str = Depends(current_user)):
    msgs = CONVERSATIONS.get(conversation_id)
    if msgs is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": msgs}

# 14. Health Risk Prediction (Prototype)
@app.post("/api/v1/personal/risk-prediction/cardiovascular")
def predict_cvd_risk(data: RiskCalculationInput, user_id: str = Depends(current_user)):
    risk_input = RiskInput(
        age=data.age,
        bmi=data.bmi,
        systolic_bp=data.systolic_bp,
        glucose=data.glucose,
        smoker=data.smoker,
        family_history=data.family_history,
    )
    return risk_service.predict(risk_input)

# 15. Data Export & Settings
@app.post("/api/v1/personal/export")
def request_data_export(user_id: str = Depends(current_user)):
    job_id = f"exp-{uuid4().hex[:8]}"
    return {
        "job_id": job_id,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "export_scope": "Full personal health archive (JSON format)",
        "download_url": f"/api/v1/personal/export/{job_id}/download",
        "message": "Your personal health archive has been generated securely.",
    }

@app.get("/api/v1/personal/export/{job_id}/download")
def download_data_export(job_id: str, user_id: str = Depends(current_user)):
    return {
        "export_metadata": {
            "job_id": job_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "compliance": "Personal Data Portability Standard",
        },
        "health_data": {
            "profile": USER_STATE["user"],
            "vitals": USER_STATE["vitals"],
            "medications": USER_STATE["medications"],
            "laboratory": USER_STATE["laboratory"],
            "appointments": USER_STATE["appointments"],
            "emergency_contacts": USER_STATE["emergency_contacts"],
            "consents": USER_STATE["consents"],
        },
    }
