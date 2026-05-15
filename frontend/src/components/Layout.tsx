import { Link, useLocation, useNavigate } from 'react-router-dom'
import { TicketIcon, PlusIcon, LayoutDashboardIcon, LogOutIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/AuthContext'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface LayoutProps {
    children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
    const location = useLocation()
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const navItems = [
        { to: '/', label: 'Dashboard', icon: LayoutDashboardIcon },
        { to: '/tickets/new', label: 'New Ticket', icon: PlusIcon },
    ]

    async function handleLogout() {
        await logout()
        navigate('/login')
    }

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Top nav */}
            <header className="sticky top-0 z-40 border-b border-slate-200 bg-white shadow-sm">
                <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
                    {/* Brand */}
                    <Link to="/" className="flex items-center gap-2 font-semibold text-slate-900">
                        <TicketIcon className="h-5 w-5 text-blue-600" />
                        <span>TonhãoDesk</span>
                    </Link>

                    {/* Nav links */}
                    <nav className="flex items-center gap-1">
                        {navItems.map(({ to, label, icon: Icon }) => {
                            const active =
                                to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
                            return (
                                <Link
                                    key={to}
                                    to={to}
                                    className={cn(
                                        'flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                                        active
                                            ? 'bg-slate-100 text-slate-900'
                                            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                                    )}
                                >
                                    <Icon className="h-4 w-4" />
                                    {label}
                                </Link>
                            )
                        })}
                    </nav>

                    {/* User info + logout */}
                    {user && (
                        <div className="flex items-center gap-3">
                            <div className="hidden sm:flex flex-col items-end leading-tight">
                                <span className="text-sm font-medium text-slate-900">{user.name}</span>
                                <Badge variant={user.role === 'agent' ? 'default' : 'secondary'} className="mt-0.5 text-[10px] py-0 px-1.5 h-4">
                                    {user.role}
                                </Badge>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                title="Log out"
                                onClick={handleLogout}
                                className="text-slate-500 hover:text-slate-900 cursor-pointer"
                            >
                                <LogOutIcon className="h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </div>
            </header>

            {/* Main */}
            <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
        </div>
    )
}

