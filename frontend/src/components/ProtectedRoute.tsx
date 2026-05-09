import { Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { user, isLoading } = useAuth()

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <span className="text-slate-400 text-sm">Loading…</span>
            </div>
        )
    }

    if (!user) return <Navigate to="/login" replace />

    return <>{children}</>
}
