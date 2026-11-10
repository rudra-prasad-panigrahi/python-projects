# Personal Gateway API Specification

Base path:

`/api/v1/personal`

## Profile

```text
GET    /profile
PATCH  /profile
```

## Health records

```text
GET    /health-records
GET    /health-records/{record_id}
POST   /health-records
PATCH  /health-records/{record_id}
```

## Timeline

```text
GET /timeline
GET /timeline/{event_id}
```

## Vitals

```text
GET  /vitals
POST /vitals
GET  /vitals/trends
```

## Documents

```text
GET  /documents
POST /documents/upload
GET  /documents/{document_id}
DELETE /documents/{document_id}
```

## Laboratory

```text
GET /laboratory/reports
GET /laboratory/reports/{report_id}
GET /laboratory/trends
```

## Medications

```text
GET    /medications
POST   /medications
PATCH  /medications/{medication_id}
DELETE /medications/{medication_id}
GET    /medications/interactions
GET    /medications/adherence
```

## Appointments

```text
GET  /appointments
POST /appointments
PATCH /appointments/{appointment_id}
```

## Care navigation

```text
GET /care/doctors
GET /care/hospitals
GET /care/laboratories
GET /care/pharmacies
```

## Emergency profile

```text
GET   /emergency/profile
PATCH /emergency/profile
GET   /emergency/contacts
POST  /emergency/contacts
PATCH /emergency/contacts/{contact_id}
DELETE /emergency/contacts/{contact_id}
```

## Privacy and consent

```text
GET  /privacy/access-logs
GET  /privacy/sessions

GET  /consent
POST /consent
PATCH /consent/{consent_id}
DELETE /consent/{consent_id}
```

## AI

```text
POST /ai/summary
POST /ai/lab-explanation
POST /ai/trend-analysis
POST /ai/chat
```

### API rules

- All protected resources require authentication.
- User ownership must be enforced server-side.
- Pagination is mandatory for list APIs.
- Validation errors use a consistent schema.
- Sensitive fields must be omitted when not needed.
- AI responses must expose source references where available.
- APIs must not return secrets or internal stack traces.
