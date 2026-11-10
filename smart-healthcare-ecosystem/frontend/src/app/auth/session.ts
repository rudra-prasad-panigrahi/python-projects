import type { Session } from './auth-types';
const key = 'personal-health-session';
export const loadSession = (): Session | null => { try { const raw = sessionStorage.getItem(key); return raw ? JSON.parse(raw) as Session : null; } catch { return null; } };
export const saveSession = (session: Session) => sessionStorage.setItem(key, JSON.stringify(session));
export const clearSession = () => sessionStorage.removeItem(key);
