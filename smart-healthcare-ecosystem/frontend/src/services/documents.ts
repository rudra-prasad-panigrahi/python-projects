import { api } from './api-client';
export type HealthDocument = { id: string; name: string; status: 'processing' | 'processed' | 'failed'; source: string; source_date: string; verified: boolean };
export const listDocuments = () => api<HealthDocument[]>('/documents');
export const uploadDocument = (file: File) => { const body = new FormData(); body.append('file', file); return api<HealthDocument>('/documents', { method: 'POST', body }); };
