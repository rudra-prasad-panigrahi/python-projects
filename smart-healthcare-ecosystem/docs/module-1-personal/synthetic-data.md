# Synthetic Data

## 1. Purpose

Synthetic data enables frontend/backend testing and model experimentation without exposing real patient information.

## 2. Generator

Recommended development tooling:

- Python;
- Faker;
- deterministic seeds;
- schema validation;
- optional SDV-style synthetic modelling for more advanced distributions.

## 3. Data groups

```text
users
patients
vitals
lab_reports
medications
appointments
documents
health_events
consents
access_logs
```

## 4. Consistency rules

The generator must enforce:

- age is derived from date of birth;
- dates are chronologically valid;
- identifiers are unique;
- medical events belong to the correct user;
- medication periods are logically ordered;
- consent expiry is after start time;
- timeline events reference existing records.

## 5. Development volumes

Initial target:

- 1,000–2,000 users/patient profiles;
- thousands of vitals;
- hundreds/thousands of lab reports;
- medication and appointment histories;
- enough data to test dashboard pagination and trend charts.

Scale can be increased for performance tests.

## 6. Safety

Clearly label all generated records as synthetic/development data. Never insert real patient information into seed scripts.
