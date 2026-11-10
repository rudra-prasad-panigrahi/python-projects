# Security

## 1. Security principles

- least privilege;
- defense in depth;
- secure defaults;
- data minimization;
- server-side authorization;
- auditability;
- secret isolation.

## 2. Threat model

Potential threats:

- credential theft;
- broken access control;
- IDOR/BOLA;
- malicious document uploads;
- SQL injection;
- XSS;
- CSRF where applicable;
- token theft;
- prompt injection;
- retrieval authorization bypass;
- sensitive data leakage;
- insecure third-party integrations.

## 3. Controls

### Authentication
- secure password hashing;
- MFA capability;
- session management;
- rate limiting.

### Authorization
- authenticated user checks;
- resource ownership;
- scoped access;
- consent enforcement.

### Documents
- MIME/type validation;
- file-size limits;
- malware scanning where deployed;
- isolated storage;
- non-public object keys;
- authorization before download.

### API
- request validation;
- parameterized queries;
- security headers;
- CORS restrictions;
- rate limiting.

### AI
Treat uploaded documents and retrieved text as untrusted input.

Protect against:

- prompt injection;
- instruction hijacking;
- data exfiltration;
- unauthorized retrieval.

## 4. Audit

Record security-relevant events such as:

- login failures;
- sensitive record access;
- consent changes;
- document access;
- security-setting changes.

Avoid logging full medical payloads, credentials, or tokens.

## 5. Break-glass future capability

A future emergency module may support controlled break-glass access. Any such event must capture:

- actor;
- reason;
- patient/resource;
- time;
- data scope;
- review status.

It must remain auditable.

## 6. Production security validation

Before deployment, perform:

- dependency scanning;
- static analysis;
- container scanning;
- API security testing;
- authorization tests;
- secret scanning;
- penetration testing appropriate to the deployment.
