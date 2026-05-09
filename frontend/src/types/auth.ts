export type UserRole = 'agent' | 'client'

export interface User {
    id: string
    email: string
    name: string
    role: UserRole
    created_at: string
    google_id?: string
}

export interface RegisterPayload {
    name: string
    email: string
    password: string
    role?: UserRole
}

export interface LoginPayload {
    email: string
    password: string
}
