# Frontend Architecture

## 1. Goals

The frontend is a production-oriented, responsive Personal Health OS.

It must:

- be role-scoped to the authenticated individual;
- separate personal pages from future organizational portals;
- use reusable components;
- treat API data as server state;
- provide loading, empty, error, and success states;
- be accessible by keyboard and assistive technology;
- never rely on the UI alone for authorization.

## 2. Structure

```text
frontend/src/
├── app/
│   ├── router/
│   ├── auth/
│   ├── permissions/
│   ├── providers/
│   ├── config/
│   └── store/
├── portals/
│   └── personal/
│       ├── layout/
│       ├── pages/
│       │   ├── dashboard/
│       │   ├── profile/
│       │   ├── health-record/
│       │   ├── timeline/
│       │   ├── health-trends/
│       │   ├── documents/
│       │   ├── laboratory/
│       │   ├── medications/
│       │   ├── appointments/
│       │   ├── care-navigation/
│       │   ├── ai-assistant/
│       │   ├── emergency/
│       │   ├── privacy/
│       │   ├── consent/
│       │   ├── notifications/
│       │   └── settings/
│       └── components/
├── features/
├── mocks/
├── shared/
├── services/
├── hooks/
├── types/
└── utils/
```

## 3. Dashboard composition

The Personal Dashboard should prioritize:

1. AI health brief
2. important health trends
3. medication status
4. upcoming care
5. recent timeline events
6. privacy/access alerts
7. emergency readiness
8. AI assistant entry point

It should not resemble an administrative hospital dashboard.

## 4. Routing

```text
/personal
/personal/dashboard
/personal/profile
/personal/health-record
/personal/timeline
/personal/health-trends
/personal/documents
/personal/laboratory
/personal/medications
/personal/appointments
/personal/care-navigation
/personal/ai-assistant
/personal/emergency
/personal/privacy
/personal/consent
/personal/notifications
/personal/settings
```

## 5. Frontend-first development

MSW can intercept API requests during local UI development.

```text
React UI -> API client -> MSW -> synthetic response
                         or
React UI -> API client -> FastAPI -> PostgreSQL/Object Storage
```

The switch must be controlled by environment configuration. Mock mode must be disabled in production.

## 6. State management

- Server state: TanStack Query or the project's established equivalent.
- Local UI state: component state where practical.
- Auth/session: centralized provider.
- Forms: React Hook Form + schema validation if already adopted.
