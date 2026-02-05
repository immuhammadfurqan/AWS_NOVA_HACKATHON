export interface User {
    email: string;
    full_name?: string;
    is_active?: boolean;
    is_superuser?: boolean;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export interface AuthError {
    detail: string;
}
