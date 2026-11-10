# Testing Strategy

## 1. Test layers

```text
Unit
 ↓
Integration
 ↓
API
 ↓
Security
 ↓
E2E
 ↓
Performance
 ↓
AI Evaluation
```

## 2. Backend

Test:

- validation;
- CRUD;
- ownership;
- pagination;
- filtering;
- authorization;
- consent;
- audit logging;
- database constraints.

## 3. Frontend

Test:

- routes;
- dashboard rendering;
- forms;
- loading/empty/error states;
- MSW handlers;
- permission-aware UI;
- accessibility.

## 4. E2E scenarios

### Scenario A
Sign up → complete onboarding → dashboard.

### Scenario B
Upload synthetic lab report → parse → review → save → timeline.

### Scenario C
Add vitals → view trend chart → receive trend insight.

### Scenario D
Create medication → schedule → adherence event.

### Scenario E
Create consent → view → revoke → audit log.

### Scenario F
Ask AI about a known record → verify source reference.

## 5. Security tests

Verify:

- unauthenticated requests rejected;
- cross-user record access rejected;
- document URLs cannot expose another user's documents;
- expired consent blocks access;
- rate limiting works where enabled;
- secrets are not logged.

## 6. AI evaluation

Measure separately for each use case.

Examples:

- extraction accuracy;
- trend-detection precision/recall;
- retrieval recall;
- groundedness;
- citation correctness;
- unsafe-response rate.

Do not use only generic accuracy for every AI feature.
