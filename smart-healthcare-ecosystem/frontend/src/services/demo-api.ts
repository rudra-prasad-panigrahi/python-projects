const configuredApiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
const normalizedApiBase = configuredApiBase.replace(/\/+$/, '');
const API_BASE = normalizedApiBase.endsWith('/personal') ? normalizedApiBase : `${normalizedApiBase}/personal`;

export type DemoSession = { access_token: string; user: { email: string; display_name: string } };
export type OAuthProvider = 'google' | 'github';
export type OAuthProviders = Record<OAuthProvider, boolean>;

async function authRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || 'The authentication service could not complete that request.');
  }
  return body as T;
}

export async function signIn(email: string, password: string): Promise<DemoSession> {
  return authRequest<DemoSession>('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
}

export async function register(input: {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email: string;
  password: string;
}): Promise<DemoSession> {
  return authRequest<DemoSession>('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
}

export async function getOAuthProviders(): Promise<OAuthProviders> {
  return authRequest<OAuthProviders>('/auth/providers');
}

export function startOAuth(provider: OAuthProvider): void {
  window.location.assign(`${API_BASE}/auth/${provider}/start`);
}

export async function exchangeOAuthTicket(ticket: string): Promise<DemoSession> {
  return authRequest<DemoSession>('/auth/oauth/exchange', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticket }),
  });
}

export async function signOut(token: string): Promise<void> {
  const response = await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || 'The session could not be revoked.');
  }
}

export async function api<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || 'The development service could not complete that request.');
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
