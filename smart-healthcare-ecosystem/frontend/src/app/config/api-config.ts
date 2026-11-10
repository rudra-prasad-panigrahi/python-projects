import { environment } from './environment';
export const apiConfig = { baseUrl: environment.apiBaseUrl, personalApi: `${environment.apiBaseUrl}/api/v1/personal` } as const;
