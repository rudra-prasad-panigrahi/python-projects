import { apiConfig } from '../app/config/api-config';
import { loadSession } from '../app/auth/session';
export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const session = loadSession();
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  if (session) headers.set('Authorization', `Bearer ${session.accessToken}`);
  const response = await fetch(`${apiConfig.personalApi}${path}`, { ...init, headers });
  if (!response.ok) throw new ApiError(response.status, (await response.json().catch(() => ({ detail: response.statusText }))).detail ?? 'Request failed');
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}
