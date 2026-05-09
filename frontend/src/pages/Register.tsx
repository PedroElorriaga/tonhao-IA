import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { TicketIcon, EyeIcon, EyeOffIcon } from 'lucide-react'
import axios from 'axios'
import { useAuth } from '@/context/AuthContext'
import { googleLoginUrl } from '@/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const schema = z.object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Enter a valid email'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    role: z.enum(['client', 'agent'], { error: () => 'Select a role' }),
})

type FormValues = z.infer<typeof schema>

export default function Register() {
    const { register: registerUser } = useAuth()
    const navigate = useNavigate()
    const [apiError, setApiError] = useState('')
    const [showPassword, setShowPassword] = useState(false)

    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
        resolver: zodResolver(schema),
        defaultValues: { role: 'client' },
    })

    async function onSubmit(values: FormValues) {
        setApiError('')
        try {
            await registerUser(values)
            navigate('/')
        } catch (err) {
            if (axios.isAxiosError(err)) {
                const detail = err.response?.data?.detail
                setApiError(typeof detail === 'string' ? detail : 'Registration failed. Please try again.')
            } else {
                setApiError('Registration failed. Please try again.')
            }
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
            <div className="w-full max-w-sm space-y-6">
                <div className="flex flex-col items-center gap-2">
                    <TicketIcon className="h-8 w-8 text-blue-600" />
                    <h1 className="text-2xl font-bold text-slate-900">TonhãoDesk</h1>
                    <p className="text-sm text-slate-500">Create your account</p>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Register</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
                            <div className="space-y-1.5">
                                <Label htmlFor="name">Full name</Label>
                                <Input id="name" autoComplete="name" {...register('name')} aria-invalid={!!errors.name} />
                                {errors.name && <p className="text-xs text-red-600">{errors.name.message}</p>}
                            </div>

                            <div className="space-y-1.5">
                                <Label htmlFor="email">Email</Label>
                                <Input id="email" type="email" autoComplete="email" {...register('email')} aria-invalid={!!errors.email} />
                                {errors.email && <p className="text-xs text-red-600">{errors.email.message}</p>}
                            </div>

                            <div className="space-y-1.5">
                                <Label htmlFor="password">Password</Label>
                                <div className="relative">
                                    <Input
                                        id="password"
                                        type={showPassword ? 'text' : 'password'}
                                        autoComplete="new-password"
                                        className="pr-10"
                                        {...register('password')}
                                        aria-invalid={!!errors.password}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(v => !v)}
                                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                                    >
                                        {showPassword ? <EyeOffIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
                                    </button>
                                </div>
                                {errors.password && <p className="text-xs text-red-600">{errors.password.message}</p>}
                            </div>

                            {/* <div className="space-y-1.5">
                                <Label htmlFor="role">Role</Label>
                                <Select id="role" {...register('role')} aria-invalid={!!errors.role}>
                                    <option value="client">Client</option>
                                    <option value="agent">Agent</option>
                                </Select>
                                {errors.role && <p className="text-xs text-red-600">{errors.role.message}</p>}
                            </div> */}

                            {apiError && <p className="text-sm text-red-600">{apiError}</p>}

                            <Button type="submit" className="w-full" disabled={isSubmitting}>
                                {isSubmitting ? 'Creating account…' : 'Create account'}
                            </Button>
                        </form>

                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t border-slate-200" />
                            </div>
                            <div className="relative flex justify-center text-xs text-slate-400">
                                <span className="bg-white px-2">or</span>
                            </div>
                        </div>

                        <Button
                            variant="outline"
                            className="w-full gap-2"
                            onClick={() => { window.location.href = googleLoginUrl() }}
                        >
                            <svg className="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                            </svg>
                            Continue with Google
                        </Button>
                    </CardContent>
                </Card>

                <p className="text-center text-sm text-slate-500">
                    Already have an account?{' '}
                    <Link to="/login" className="font-medium text-blue-600 hover:underline">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    )
}
