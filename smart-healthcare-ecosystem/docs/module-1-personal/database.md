# Personal Gateway Database Design

## 1. Database

Primary database: PostgreSQL.

Use relational normalization for core entities and JSON only where flexible metadata is appropriate.

## 2. Core entities

```mermaid
erDiagram
    USER ||--|| PERSONAL_PROFILE : owns
    USER ||--o{ HEALTH_RECORD : has
    USER ||--o{ HEALTH_EVENT : has
    USER ||--o{ VITAL_READING : records
    USER ||--o{ DOCUMENT : uploads
    USER ||--o{ MEDICATION : manages
    USER ||--o{ APPOINTMENT : books
    USER ||--o{ EMERGENCY_CONTACT : configures
    USER ||--o{ CONSENT_GRANT : creates
    USER ||--o{ ACCESS_LOG : receives
    DOCUMENT ||--o{ LAB_RESULT : may_contain
    HEALTH_RECORD ||--o{ HEALTH_EVENT : generates

    USER {
        uuid id PK
        string email UK
        string phone
        string status
        datetime created_at
        datetime updated_at
    }

    PERSONAL_PROFILE {
        uuid user_id PK,FK
        string first_name
        string last_name
        date date_of_birth
        string gender
        string blood_group
    }

    HEALTH_RECORD {
        uuid id PK
        uuid user_id FK
        string record_type
        string source_type
        string source_name
        datetime record_date
        datetime created_at
    }

    VITAL_READING {
        uuid id PK
        uuid user_id FK
        string metric_type
        decimal value
        string unit
        datetime recorded_at
        string source
    }

    DOCUMENT {
        uuid id PK
        uuid user_id FK
        string document_type
        string storage_key
        string provenance_status
        datetime uploaded_at
    }

    MEDICATION {
        uuid id PK
        uuid user_id FK
        string name
        string dosage
        string frequency
        date start_date
        date end_date
        string status
    }

    APPOINTMENT {
        uuid id PK
        uuid user_id FK
        string provider_name
        string specialty
        datetime scheduled_at
        string status
    }

    EMERGENCY_CONTACT {
        uuid id PK
        uuid user_id FK
        string name
        string relationship
        string phone
        boolean primary_contact
    }

    CONSENT_GRANT {
        uuid id PK
        uuid user_id FK
        string grantee
        string scope
        string purpose
        datetime expires_at
        string status
    }

    ACCESS_LOG {
        uuid id PK
        uuid user_id FK
        string actor_type
        string actor_reference
        string resource_type
        uuid resource_id
        string action
        datetime occurred_at
    }
```

## 3. Data provenance

Every health record/document should preserve:

- source;
- source organization where known;
- original record/document reference;
- recorded date;
- import date;
- verification status;
- transformation history;
- AI-derived status where applicable.

## 4. Data retention

Retention policy must be configurable by deployment and jurisdiction. Avoid deleting source medical documents as a side effect of deleting derived summaries.

## 5. Indexing

Index:

- user_id;
- record_date;
- metric_type + recorded_at;
- medication status;
- appointment date;
- consent status + expiry;
- access log timestamp.

## 6. Soft deletion

Prefer deactivation/soft deletion for core health records where required by policy. Permanent deletion must be an explicit policy-driven operation.
