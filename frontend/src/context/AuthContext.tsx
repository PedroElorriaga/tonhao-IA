import { createContext, useContext, useEffect, useState } from 'react'
import { getMe, login as apiLogin, logout as apiLogout, register as apiRegister } from '@/api/auth'
import type { User, LoginPayload, RegisterPayload } from '@/types/auth'

interface AuthState {
    user: User | null
    isLoading: boolean
    login: (payload: LoginPayload) => Promise<void>
    register: (payload: RegisterPayload) => Promise<void>
    logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        getMe()
            .then(setUser)
            .catch(() => setUser(null))
            .finally(() => setIsLoading(false))
    }, [])

    async function login(payload: LoginPayload) {
        const u = await apiLogin(payload)
        setUser(u)
    }

    async function register(payload: RegisterPayload) {
        const u = await apiRegister(payload)
        setUser(u)
    }

    async function logout() {
        await apiLogout()
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth(): AuthState {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
    return ctx
}
