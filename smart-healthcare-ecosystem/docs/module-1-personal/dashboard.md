# Personal Dashboard Specification

## 1. Objective

The dashboard should answer four questions:

- What changed?
- What requires my attention?
- What care is coming next?
- Where is my health information and who has accessed it?

## 2. Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Logo | Search | Alerts | Profile                            │
├──────────────────────────────────────────────────────────────┤
│ Good morning, <User>                                        │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AI HEALTH BRIEF                                          │ │
│ │ Transparent summary of recent authorized health data     │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ [Vitals] [Medications] [Appointments] [Data Access]         │
│                                                              │
│ ┌──────────────────── Health Trends ──────────────────────┐ │
│ │ BP / Glucose / Weight / Heart Rate / SpO2 / HbA1c      │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────── Personal AI ────────────────────────┐ │
│ │ Ask about your records...                               │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ Recent Timeline            | Important Alerts              │
│ Emergency Readiness        | Privacy Center                │
└──────────────────────────────────────────────────────────────┘
```

## 3. KPI rules

Dashboard values must come from APIs/database-derived aggregates.

Never hardcode production statistics.

Examples:

- active medications;
- upcoming appointments;
- recent reports;
- recent access events;
- number of connected sources;
- measurements recorded in the selected period.

## 4. AI brief rules

The AI brief must identify:

- source period;
- data sources;
- detected trend/summary;
- uncertainty when applicable.

Do not present generated text as a confirmed medical diagnosis.

## 5. Failure states

Every panel must support:

- loading;
- no data;
- partial data;
- service unavailable;
- retry where sensible.

A failed AI panel must not prevent the rest of the dashboard from loading.
