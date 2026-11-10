# Backend Architecture

## 1. Purpose

The backend exposes secure APIs for the Personal Health Gateway and provides a stable foundation for future integration with organizational healthcare systems.

## 2. Layering

```text
HTTP Router
    ↓
Schema Validation
    ↓
Application Service
    ↓
Repository
    ↓
Database / Object Storage
```

AI-specific processing should be invoked through service boundaries rather than embedded directly in route handlers.

## 3. Structure

```text
backend/app/
├── api/v1/personal/
├── domains/
│   ├── personal_profile/
│   ├── health_records/
│   ├── health_timeline/
│   ├── vitals/
│   ├── documents/
│   ├── laboratory/
│   ├── medications/
│   ├── appointments/
│   ├── care_navigation/
│   ├── emergency/
│   ├── consent/
│   ├── privacy/
│   ├── notifications/
│   └── ai/
├── core/
├── integrations/
├── workers/
└── database/
```

## 4. Responsibilities

### Router
HTTP transport, authentication dependency, response serialization.

### Schema
Request and response validation.

### Service
Business rules and orchestration.

### Repository
Persistence operations.

### Integration
External storage, maps, notification providers, medication references, wearable connectors.

### Worker
OCR, document extraction, health analysis, scheduled reminders, asynchronous AI jobs.

## 5. Error model

Use consistent errors for:

- validation failure;
- authentication failure;
- authorization failure;
- resource not found;
- conflict/duplicate;
- unsupported operation;
- external dependency failure;
- internal failure.

Do not expose stack traces or internal database details to users.
