import { api } from './api-client';
export type Notification = { id: string; type: string; title: string; read: boolean; is_synthetic: boolean };
export const listNotifications = () => api<Notification[]>('/notifications');
