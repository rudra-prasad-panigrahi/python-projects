import unittest
from datetime import date
from fastapi.testclient import TestClient
from backend.app.main import app, DEMO_EMAIL, DEMO_PASSWORD

class TestPersonalHealthAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        res = self.client.post('/api/v1/personal/auth/login', json={'email': DEMO_EMAIL, 'password': DEMO_PASSWORD})
        self.assertEqual(res.status_code, 200)
        self.token = res.json()['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_health_check(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(data['synthetic_data_only'])

    def test_auth_invalid_credentials(self):
        res = self.client.post('/api/v1/personal/auth/login', json={'email': 'wrong@test.com', 'password': 'wrong'})
        self.assertEqual(res.status_code, 401)

    def test_auth_session(self):
        res = self.client.get('/api/v1/personal/auth/session', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['authenticated'])
        self.assertEqual(data['user']['email'], DEMO_EMAIL)

    def test_profile_get_and_update(self):
        res = self.client.get('/api/v1/personal/profile', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['first_name'], 'Avery')

        update_data = {
            'first_name': 'Avery',
            'last_name': 'Morgan',
            'date_of_birth': '1987-04-18',
            'email': DEMO_EMAIL,
            'city': 'Seattle',
            'state': 'WA',
            'blood_group': 'O+'
        }
        res_update = self.client.put('/api/v1/personal/profile', json=update_data, headers=self.headers)
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()['status'], 'success')

        invalid_data = {**update_data, 'date_of_birth': '2099-01-01'}
        res_invalid = self.client.put('/api/v1/personal/profile', json=invalid_data, headers=self.headers)
        self.assertEqual(res_invalid.status_code, 422)

    def test_profile_persists_for_new_session_and_user(self):
        register = self.client.post('/api/v1/personal/auth/register', json={
            'first_name': 'Jamie',
            'last_name': 'Rivera',
            'date_of_birth': '1990-02-14',
            'gender': 'female',
            'email': 'jamie.rivera@example.com',
            'password': 'SecurePass123',
            'phone': '+1-555-0100'
        })
        self.assertEqual(register.status_code, 201, register.text)
        token = register.json()['access_token']

        update = self.client.put('/api/v1/personal/profile', json={
            'first_name': 'Jamie',
            'last_name': 'Rivera',
            'date_of_birth': '1990-02-14',
            'email': 'jamie.rivera@example.com',
            'city': 'Portland',
            'state': 'OR',
            'blood_group': 'A+'
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(update.status_code, 200, update.text)

        refreshed = self.client.get('/api/v1/personal/profile', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(refreshed.status_code, 200)
        self.assertEqual(refreshed.json()['city'], 'Portland')
        self.assertEqual(refreshed.json()['first_name'], 'Jamie')

        session2 = self.client.post('/api/v1/personal/auth/login', json={'email': 'jamie.rivera@example.com', 'password': 'SecurePass123'})
        self.assertEqual(session2.status_code, 200, session2.text)
        follow_up = self.client.get('/api/v1/personal/profile', headers={'Authorization': f"Bearer {session2.json()['access_token']}"})
        self.assertEqual(follow_up.status_code, 200)
        self.assertEqual(follow_up.json()['city'], 'Portland')
        self.assertEqual(follow_up.json()['email'], 'jamie.rivera@example.com')

    def test_vitals_crud_and_bounds(self):
        vital = {
            'type': 'glucose',
            'value': 122.0,
            'unit': 'mg/dL',
            'recorded_at': '2026-08-30T09:00:00Z',
            'source': 'Home Meter'
        }
        res = self.client.post('/api/v1/personal/vitals', json=vital, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['value'], 122.0)

        invalid_vital = {**vital, 'value': 1500.0}
        res_invalid = self.client.post('/api/v1/personal/vitals', json=invalid_vital, headers=self.headers)
        self.assertEqual(res_invalid.status_code, 422)

        res_trends = self.client.get('/api/v1/personal/vitals/trends?metric=glucose', headers=self.headers)
        self.assertEqual(res_trends.status_code, 200)
        self.assertIn('direction', res_trends.json())

    def test_documents_upload_validation(self):
        res = self.client.post(
            '/api/v1/personal/documents',
            files={'file': ('script.exe', b'binary content', 'application/x-msdownload')},
            headers=self.headers
        )
        self.assertEqual(res.status_code, 415)

        res_pdf = self.client.post(
            '/api/v1/personal/documents',
            files={'file': ('lab_test.pdf', b'%PDF-1.4 sample content', 'application/pdf')},
            headers=self.headers
        )
        self.assertEqual(res_pdf.status_code, 201)
        self.assertEqual(res_pdf.json()['status'], 'processed')

    def test_laboratory_and_ai_interpretation(self):
        res = self.client.get('/api/v1/personal/laboratory', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        labs = res.json()
        self.assertGreater(len(labs), 0)
        lab_id = labs[0]['id']

        res_interp = self.client.get(f'/api/v1/personal/laboratory/{lab_id}/interpret', headers=self.headers)
        self.assertEqual(res_interp.status_code, 200)
        data = res_interp.json()
        self.assertIn('interpretations', data)
        self.assertIn('AI-GENERATED INFORMATIONAL EXPLANATION ONLY', data['ai_notice'])

    def test_medications_and_dose_logging(self):
        res = self.client.get('/api/v1/personal/medications', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        meds = res.json()
        self.assertGreater(len(meds), 0)
        med_id = meds[0]['id']

        res_dose = self.client.post(f'/api/v1/personal/medications/{med_id}/dose', json={'taken': True, 'late': False}, headers=self.headers)
        self.assertEqual(res_dose.status_code, 200)
        self.assertEqual(res_dose.json()['status'], 'success')

        res_ml = self.client.get('/api/v1/personal/medications/adherence-ml', headers=self.headers)
        self.assertEqual(res_ml.status_code, 200)
        self.assertIn('predicted_adherence_probability', res_ml.json())

    def test_appointments_and_care_navigation(self):
        res = self.client.get('/api/v1/personal/appointments', headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res_care = self.client.get('/api/v1/personal/care?query=seattle', headers=self.headers)
        self.assertEqual(res_care.status_code, 200)
        self.assertGreater(len(res_care.json()), 0)

    def test_emergency_profile_and_contacts(self):
        res = self.client.get('/api/v1/personal/emergency', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['blood_group'], 'O+')
        self.assertFalse(data['dispatch_available'])

    def test_privacy_and_consent(self):
        res_log = self.client.get('/api/v1/personal/privacy/access-log', headers=self.headers)
        self.assertEqual(res_log.status_code, 200)

        res_consents = self.client.get('/api/v1/personal/consents', headers=self.headers)
        self.assertEqual(res_consents.status_code, 200)
        consent_id = res_consents.json()[0]['id']

        res_patch = self.client.patch(f'/api/v1/personal/consents/{consent_id}', json={'status': 'approved'}, headers=self.headers)
        self.assertEqual(res_patch.status_code, 200)
        self.assertEqual(res_patch.json()['status'], 'approved')

    def test_ai_assistant_grounded_qa(self):
        res = self.client.post('/api/v1/personal/ai/answer', json={'message': 'What was my latest glucose result?'}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('126', data['answer'])
        self.assertTrue(data['informational_only'])
        self.assertGreater(len(data['sources']), 0)

    def test_data_export_workflow(self):
        res_exp = self.client.post('/api/v1/personal/export', headers=self.headers)
        self.assertEqual(res_exp.status_code, 200)
        job_data = res_exp.json()
        self.assertEqual(job_data['status'], 'completed')

        res_dl = self.client.get(job_data['download_url'], headers=self.headers)
        self.assertEqual(res_dl.status_code, 200)
        archive = res_dl.json()
        self.assertIn('health_data', archive)
        self.assertIn('profile', archive['health_data'])

if __name__ == '__main__':
    unittest.main()
