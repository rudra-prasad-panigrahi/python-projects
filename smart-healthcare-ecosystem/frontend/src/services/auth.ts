import { apiConfig } from '../app/config/api-config';
import { clearSession, saveSession } from '../app/auth/session';
import type { Session } from '../app/auth/auth-types';
export async function signIn(email: string, password: string): Promise<Session> {
  const response = await fetch(`${apiConfig.personalApi}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
  if (!response.ok) throw new Error('Unable to sign in with those credentials.');
  const result = await response.json(); const session = { accessToken: result.access_token, user: result.user, developmentDemo: result.development_demo };
  saveSession(session); return session;
}
export async function signOut(): Promise<void> { clearSession(); }
