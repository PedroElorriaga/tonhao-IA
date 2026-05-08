import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeftIcon, PaperclipIcon, UploadIcon } from 'lucide-react'
import { createTicket } from '@/api/tickets'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TICKET_CATEGORIES } from '@/types/ticket'
import type { CreateTicketPayload } from '@/types/ticket'

const schema = z.object({
    title: z.string().min(5, 'Title must be at least 5 characters').max(150),
    description: z.string().min(10, 'Description must be at least 10 characters').max(5000),
    client_name: z.string().min(2, 'Client name is required').max(100),
    priority: z.enum(['low', 'medium', 'high', 'critical'], {
        error: () => 'Select a priority',
    }),
    category: z.string().min(1, 'Select a category'),
})

type FormValues = z.infer<typeof schema>

export default function CreateTicket() {
    const navigate = useNavigate()
    const fileInputRef = useRef<HTMLInputElement>(null)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<FormValues>({
        resolver: zodResolver(schema),
        defaultValues: { priority: 'medium' },
    })

    const { mutate, isPending, isError, error } = useMutation({
        mutationFn: (payload: CreateTicketPayload) => createTicket(payload),
        onSuccess: (ticket) => {
            navigate(`/tickets/${ticket.id}`)
        },
    })

    function onSubmit(values: FormValues) {
        mutate({ ...values, attachment: selectedFile ?? undefined })
    }

    return (
        <div className="mx-auto max-w-2xl space-y-6">
            {/* Back */}
            <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="-ml-1">
                <ArrowLeftIcon className="h-4 w-4" />
                Back
            </Button>

            <Card>
                <CardHeader>
                    <CardTitle>Open a New Ticket</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
                        {/* Client name */}
                        <div className="space-y-1.5">
                            <Label htmlFor="client_name">Your name *</Label>
                            <Input
                                id="client_name"
                                placeholder="John Doe"
                                {...register('client_name')}
                                aria-invalid={!!errors.client_name}
                            />
                            {errors.client_name && (
                                <p className="text-xs text-red-600">{errors.client_name.message}</p>
                            )}
                        </div>

                        {/* Title */}
                        <div className="space-y-1.5">
                            <Label htmlFor="title">Ticket title *</Label>
                            <Input
                                id="title"
                                placeholder="Short summary of the issue"
                                {...register('title')}
                                aria-invalid={!!errors.title}
                            />
                            {errors.title && (
                                <p className="text-xs text-red-600">{errors.title.message}</p>
                            )}
                        </div>

                        {/* Description */}
                        <div className="space-y-1.5">
                            <Label htmlFor="description">Description *</Label>
                            <Textarea
                                id="description"
                                placeholder="Describe the issue in detail…"
                                rows={5}
                                {...register('description')}
                                aria-invalid={!!errors.description}
                            />
                            {errors.description && (
                                <p className="text-xs text-red-600">{errors.description.message}</p>
                            )}
                        </div>

                        {/* Priority + Category (2 cols) */}
                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            <div className="space-y-1.5">
                                <Label htmlFor="priority">Priority *</Label>
                                <Select
                                    id="priority"
                                    {...register('priority')}
                                    aria-invalid={!!errors.priority}
                                >
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </Select>
                                {errors.priority && (
                                    <p className="text-xs text-red-600">{errors.priority.message}</p>
                                )}
                            </div>

                            <div className="space-y-1.5">
                                <Label htmlFor="category">Category *</Label>
                                <Select
                                    id="category"
                                    placeholder="Select category"
                                    defaultValue=""
                                    {...register('category')}
                                    aria-invalid={!!errors.category}
                                >
                                    {TICKET_CATEGORIES.map((cat) => (
                                        <option key={cat} value={cat}>
                                            {cat}
                                        </option>
                                    ))}
                                </Select>
                                {errors.category && (
                                    <p className="text-xs text-red-600">{errors.category.message}</p>
                                )}
                            </div>
                        </div>

                        {/* Attachment */}
                        <div className="space-y-1.5">
                            <Label>Attachment (optional)</Label>
                            <div
                                className="flex cursor-pointer items-center gap-3 rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-3 transition-colors hover:bg-slate-100"
                                onClick={() => fileInputRef.current?.click()}
                                onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
                                tabIndex={0}
                                role="button"
                                aria-label="Upload attachment"
                            >
                                {selectedFile ? (
                                    <>
                                        <PaperclipIcon className="h-4 w-4 shrink-0 text-blue-600" />
                                        <span className="truncate text-sm text-slate-700">{selectedFile.name}</span>
                                    </>
                                ) : (
                                    <>
                                        <UploadIcon className="h-4 w-4 shrink-0 text-slate-400" />
                                        <span className="text-sm text-slate-500">Click to attach a file</span>
                                    </>
                                )}
                            </div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                className="hidden"
                                accept="image/*,.pdf,.doc,.docx,.txt,.zip"
                                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                            />
                        </div>

                        {/* API error */}
                        {isError && (
                            <p className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
                                {(error as Error)?.message ?? 'Failed to create ticket. Please try again.'}
                            </p>
                        )}

                        {/* Actions */}
                        <div className="flex justify-end gap-3 pt-2">
                            <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                                Cancel
                            </Button>
                            <Button type="submit" disabled={isPending}>
                                {isPending ? 'Submitting…' : 'Submit Ticket'}
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
