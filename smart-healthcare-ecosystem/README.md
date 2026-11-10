# dmpm_lab

# Smart Healthcare Ecosystem

## Module 1 — Personal Health Gateway

An AI-powered Personal Health Operating System that allows individuals to securely manage, understand, and use their health information from a single platform.

> **Current implementation:** The authenticated application is the Module 1 Personal Health Gateway. The public website also includes prototype previews for Clinical Intelligence and Emergency Intelligence to demonstrate the proposed connected-care journey. Those previews use illustrative data and are not connected to clinical systems, sensors, hospitals, or emergency services.

---

## 1. Vision

The Personal Health Gateway is designed around the individual rather than a single hospital.

It allows a user to:

* maintain a personal health profile
* store and organize medical records
* upload health documents
* track vital-sign trends
* manage medications
* manage appointments
* maintain emergency information
* control consent and privacy
* interact with a personal health AI assistant
* receive proactive health insights
* connect authorized healthcare data sources in future versions

The platform is the personal-facing layer of a broader Smart Healthcare Ecosystem. The public ecosystem overview describes the proposed module boundaries, data flow, privacy principles, research evaluation and incremental roadmap.

### Prototype boundaries

* The Personal Health Gateway is the existing interactive application and uses the configured demo/backend services.
* Clinical and Emergency workspaces are frontend demonstrations with fictional sample data; they do not manage real patients, dispatch ambulances, or provide clinical decision support.
* Do not use the website for medical decisions or emergency response. Contact local emergency services for urgent help.

---

## 2. Current Module

### Module 1 — Personal Health Gateway

Core domains:

1. Personal identity and authentication
2. Personal health profile
3. Personal health records
4. Health timeline
5. Vital tracking
6. Health trend analytics
7. Medical document management
8. Laboratory report management
9. Medication management
10. Appointment management
11. Care navigation
12. AI health assistant
13. Emergency profile
14. Privacy and consent
15. Notifications
16. Personal dashboard
17. AI/ML health intelligence

---

## 3. Architecture

```text
                         PERSONAL HEALTH GATEWAY
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
        PERSONAL DATA         AI HEALTH          USER ACTIONS
              │                   │                   │
       Profile / Records      Summaries          Appointments
       Documents / Vitals     Trends             Medications
       Timeline / Labs        Risk Models        Care Navigation
              │               RAG / Assistant     Emergency
              └───────────────────┼───────────────────┘
                                  ▼
                         PRIVACY & CONSENT
                                  │
                         DATA PROVENANCE
                                  │
                                  ▼
                           SECURE BACKEND
                                  │
                   ┌──────────────┼──────────────┐
                   ▼              ▼              ▼
              PostgreSQL      Object Storage   AI Services
```

---

## 4. Technology Stack

### Frontend

* React
* TypeScript
* Tailwind CSS
* React Router
* TanStack Query
* React Hook Form
* Zod
* Recharts
* MSW for frontend-first API mocking

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic

### Data

* PostgreSQL
* Redis where required
* Object storage for uploaded documents

### AI/ML

* Python
* Scikit-learn
* PyTorch/TensorFlow where appropriate
* OCR/document extraction
* RAG
* Vector retrieval
* Model evaluation and monitoring

### Infrastructure

* Docker
* Docker Compose
* NGINX
* CI/CD readiness
* Monitoring readiness

---

## 5. Repository Structure

```text
frontend/
backend/
ai/
data/
storage/
tests/
scripts/
security/
deployment/
docs/
```

See:

`docs/module-1-personal/`

for detailed architecture documentation.

---

## 6. Environment Setup

### Prerequisites

Install:

* Git
* Docker Desktop
* Node.js
* Python
* npm

Verify:

```bash
git --version
docker --version
node --version
npm --version
python --version
```

---

## 7. Environment Variables

Create a local environment file from:

```text
.env.example
```

Never commit real secrets.

Example development command:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### Google and GitHub sign-in

The sign-in and account-creation screens support Google and GitHub OAuth. Configure either or both providers in the backend environment; the buttons remain unavailable until the provider credentials are set. Keep client secrets on the backend and never place them in `VITE_*` variables.

Set `FRONTEND_URL`, `BACKEND_PUBLIC_URL`, `OAUTH_SESSION_SECRET`, and the selected provider's client ID and secret. Register these exact callback URLs with each OAuth provider:

```text
http://localhost:8000/api/v1/personal/auth/google/callback
http://localhost:8000/api/v1/personal/auth/github/callback
```

In production, use HTTPS URLs and a unique, long `OAUTH_SESSION_SECRET`. OAuth accounts require a verified email. Verified providers can be linked to an account already created through another OAuth provider; password-only accounts are not automatically linked, to avoid taking over unverified email accounts. New OAuth accounts receive a Personal Health identity without requiring a password. This remains a prototype integration: sessions are in memory and health data is synthetic/demo data, so do not use it with real patient accounts or data until sessions and health records are persisted and isolated per user.

Docker Compose passes values from the repository-root `.env` file to the backend. When starting Uvicorn directly, set these variables in the backend process environment; the application does not automatically load `.env` files.

---

## 8. Frontend-First Development

During early frontend development, MSW can simulate backend APIs.

This allows UI development before the live backend is ready.

The mock layer is strictly for development/testing.

It must not replace real backend authentication or authorization in production.

---

## 9. Run the development demo

The current implementation uses synthetic data only. It must never be connected to
real patient information or used for clinical decision-making.

Start the API in one terminal:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Start the web application in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local Vite URL (normally `http://localhost:5173`). The supplied demo
account is `patient@healthcare.local` / `Demo@12345`.

The frontend reads `VITE_API_BASE_URL` when it is set; otherwise it connects to
`http://localhost:8000/api/v1/personal`.

---

## 9. Docker Development

Start development infrastructure:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Stop:

```bash
docker compose -f docker-compose.dev.yml down
```

---

## 10. Production

Production deployment must use:

* real authentication
* secure secrets
* HTTPS/TLS
* real database
* persistent object storage
* secure configuration
* monitoring
* backups
* audit logging

Do not use development mock authentication or mock APIs in production.

---

## 11. Security Principles

This project handles potentially sensitive health information.

Core principles:

* least privilege
* secure authentication
* authorization at the backend
* data minimization
* audit logging
* encryption in transit
* encryption at rest where applicable
* secure document access
* no real patient data in development datasets

The system must never rely solely on frontend route protection.

---

## 12. AI Safety Principles

AI features are intended to provide:

* summarization
* extraction
* trend analysis
* decision support
* information retrieval
* recommendations for appropriate follow-up

AI must not be treated as an autonomous medical authority.

Medical outputs must clearly distinguish:

* source data
* calculated metrics
* model predictions
* generated explanations

AI-generated information must be traceable to its source where possible.

---

## 13. Data Development

Development uses synthetic data only.

Synthetic data must be clearly separated from production data.

Example:

```text
data/synthetic/
data/samples/
```

Never place real patient information in Git.

---

## 14. Testing

The project is intended to support:

* unit tests
* integration tests
* API tests
* security tests
* frontend tests
* end-to-end tests
* AI evaluation tests
* performance tests

A feature is not considered complete simply because its source files exist.

It must be verified.

---

## 15. Development Principle

Build incrementally.

Recommended sequence:

```text
Foundation
    ↓
Authentication
    ↓
Personal Profile
    ↓
Health Records
    ↓
Vitals & Timeline
    ↓
Documents & Labs
    ↓
Medications
    ↓
Appointments
    ↓
AI Health Intelligence
    ↓
Privacy & Consent
    ↓
Dashboard Integration
    ↓
Testing & Hardening
```

Do not implement the Organizational Gateway inside this module.

---

## 16. Future Integration

Module 1 is designed to eventually connect with:

* healthcare organizations
* hospitals
* clinics
* laboratories
* pharmacies
* emergency services
* healthcare interoperability services

Those integrations must be implemented through explicit APIs, consent controls, and provenance tracking.

---

## 17. Development Status

Current module:

**Module 1 — Personal Health Gateway**

Status:

**Under active development**

---

## 18. License

See `LICENSE`.
