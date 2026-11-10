import secrets
import unittest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.main import (
    DEMO_EMAIL,
    DEMO_USER_ID,
    OAUTH_TICKETS,
    OAuthAccountConflict,
    app,
    create_or_link_oauth_user,
)


class TestOAuthAuthentication(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_provider_configuration_is_reported(self):
        response = self.client.get("/api/v1/personal/auth/providers")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"google", "github"})
        self.assertTrue(all(isinstance(enabled, bool) for enabled in response.json().values()))

    def test_oauth_ticket_is_short_lived_and_single_use(self):
        ticket = secrets.token_urlsafe(48)
        OAUTH_TICKETS[ticket] = (DEMO_USER_ID, datetime.now(timezone.utc) + timedelta(minutes=5))
        self.addCleanup(OAUTH_TICKETS.pop, ticket, None)

        response = self.client.post("/api/v1/personal/auth/oauth/exchange", json={"ticket": ticket})
        self.assertEqual(response.status_code, 200, response.text)
        access_token = response.json()["access_token"]

        session = self.client.get(
            "/api/v1/personal/auth/session",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(session.status_code, 200)

        repeated_exchange = self.client.post(
            "/api/v1/personal/auth/oauth/exchange",
            json={"ticket": ticket},
        )
        self.assertEqual(repeated_exchange.status_code, 400)

        logout = self.client.post(
            "/api/v1/personal/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(logout.status_code, 204)
        expired_session = self.client.get(
            "/api/v1/personal/auth/session",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(expired_session.status_code, 401)

    def test_unrecognized_demo_token_is_not_authenticated(self):
        response = self.client.get(
            "/api/v1/personal/auth/session",
            headers={"Authorization": "Bearer demo-not-a-real-session"},
        )
        self.assertEqual(response.status_code, 401)

    def test_oauth_does_not_take_over_password_only_account(self):
        with self.assertRaises(OAuthAccountConflict):
            create_or_link_oauth_user(
                "github",
                "unlinked-provider-subject",
                DEMO_EMAIL,
                "Avery",
                "Morgan",
            )
