import client from './client'
import type { User, LoginPayload, RegisterPayload } from '@/types/auth'

export async function getMe(): Promise<User> {
    const { data } = await client.get<User>('/auth/me')
    return data
}

export async function login(payload: LoginPayload): Promise<User> {
    const { data } = await client.post<User>('/auth/login', payload)
    return data
}

export async function register(payload: RegisterPayload): Promise<User> {
    const { data } = await client.post<User>('/auth/register', payload)
    return data
}

export async function logout(): Promise<void> {
    await client.post('/auth/logout')
}

export function googleLoginUrl(): string {
    const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
    return `${base}/auth/google`
}
