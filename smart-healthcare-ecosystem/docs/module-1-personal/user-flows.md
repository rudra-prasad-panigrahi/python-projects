# Module 1 User Flows

## 1. First-time user

```mermaid
flowchart TD
    A[Landing Page] --> B[Choose Personal]
    B --> C[Sign Up]
    C --> D[Verify Account]
    D --> E[Basic Profile]
    E --> F[Health Profile]
    F --> G[Emergency Profile]
    G --> H[Dashboard]
```

## 2. Returning user

```mermaid
flowchart TD
    A[Personal Gate] --> B[Login]
    B --> C[Session Validation]
    C --> D[Personal Dashboard]
```

## 3. Upload health document

```mermaid
flowchart TD
    A[Select Document] --> B[Upload]
    B --> C[File Validation]
    C --> D[Secure Storage]
    D --> E[OCR / Parsing]
    E --> F[Structured Extraction]
    F --> G[User Review]
    G --> H[Save Record]
    H --> I[Timeline Update]
```

## 4. AI question flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Personal UI
    participant API as FastAPI
    participant RET as Retriever
    participant GEN as AI Generator
    participant DB as Health Data

    U->>UI: Ask question
    UI->>API: Authenticated query
    API->>RET: Retrieve authorized context
    RET->>DB: Query user records
    DB-->>RET: Relevant records
    RET->>GEN: Context + question
    GEN-->>API: Grounded response + sources
    API-->>UI: Response
    UI-->>U: Answer with source references
```

## 5. Consent flow

```mermaid
flowchart TD
    A[External Organization requests access] --> B[Consent Request]
    B --> C[User Reviews Scope]
    C --> D{Approve?}
    D -- Yes --> E[Time/Purpose Limited Grant]
    D -- No --> F[Deny]
    E --> G[Authorized Data Exchange]
    G --> H[Audit Entry]
    F --> H
```

## 6. Emergency readiness

The Personal Gateway prepares information for a later Emergency module:

```text
Emergency Profile
→ Blood Group
→ Severe Allergies
→ Critical Conditions
→ Emergency Contacts
→ Preferred Hospital
→ Sharing Preferences
```

No autonomous emergency dispatch is implemented by Module 1 itself.
