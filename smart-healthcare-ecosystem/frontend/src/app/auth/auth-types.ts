export interface PersonalUser { email: string; display_name: string }
export interface Session { accessToken: string; user: PersonalUser; developmentDemo: boolean }
