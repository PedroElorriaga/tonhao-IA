import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { useState } from 'react'
import {
    ArrowLeftIcon,
    CalendarIcon,
    UserIcon,
    TagIcon,
    PaperclipIcon,
    CheckCircle2Icon,
    CircleIcon,
    ClockIcon,
    XCircleIcon,
    CheckIcon,
    ChevronLeftIcon,
    SendIcon,
    SparklesIcon,
} from 'lucide-react'
import { getTicket, updateTicket, deleteTicket, getReplies, createReply, triggerAiReply } from '@/api/tickets'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'
// import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { StatusBadge } from '@/components/StatusBadge'
import { PriorityBadge } from '@/components/PriorityBadge'
import { STATUS_FLOW, STATUS_LABELS } from '@/types/ticket'
import type { TicketStatus } from '@/types/ticket'

const STATUS_ICON: Record<TicketStatus, typeof CircleIcon> = {
    open: CircleIcon,
    pending: ClockIcon,
    in_progress: ClockIcon,
    solved: CheckCircle2Icon,
    closed: XCircleIcon,
}

export default function TicketDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const { user } = useAuth()
    const isAgent = user?.role === 'agent'
    const [replyBody, setReplyBody] = useState('')

    const {
        data: ticket,
        isLoading,
        isError,
    } = useQuery({
        queryKey: ['ticket', id],
        queryFn: () => getTicket(id!),
        enabled: !!id,
    })

    const { mutate: advanceStatus, isPending: isAdvancing } = useMutation({
        mutationFn: (status: TicketStatus) => updateTicket(id!, { status }),
        onSuccess: (updated) => {
            queryClient.setQueryData(['ticket', id], updated)
            queryClient.invalidateQueries({ queryKey: ['tickets'] })
        },
    })

    const { mutate: remove, isPending: isDeleting } = useMutation({
        mutationFn: () => deleteTicket(id!),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['tickets'] })
            navigate('/')
        },
    })

    const { data: replies = [] } = useQuery({
        queryKey: ['replies', id],
        queryFn: () => getReplies(id!),
        enabled: !!id,
    })

    const { mutate: sendReply, isPending: isSending } = useMutation({
        mutationFn: () => createReply(id!, { body: replyBody.trim() }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['replies', id] })
            setReplyBody('')
        },
    })

    const { mutate: generateAiReply, isPending: isGenerating } = useMutation({
        mutationFn: () => triggerAiReply(id!),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['replies', id] })
        },
    })

    if (isLoading) {
        return (
            <div className="mx-auto max-w-3xl space-y-4">
                <div className="h-8 w-32 animate-pulse rounded bg-slate-200" />
                <div className="h-64 animate-pulse rounded-xl bg-slate-200" />
            </div>
        )
    }

    if (isError || !ticket) {
        return (
            <div className="mx-auto max-w-3xl text-center">
                <p className="text-red-600">Ticket not found.</p>
                <Button variant="outline" className="mt-4" onClick={() => navigate('/')}>
                    Back to Dashboard
                </Button>
            </div>
        )
    }

    const currentIndex = STATUS_FLOW.indexOf(ticket.status)
    const nextStatus = currentIndex < STATUS_FLOW.length - 1 ? STATUS_FLOW[currentIndex + 1] : null
    const prevStatus = currentIndex > 0 ? STATUS_FLOW[currentIndex - 1] : null
    const isClosed = ticket.status === 'closed'

    return (
        <div className="mx-auto max-w-3xl space-y-6">
            {/* Back */}
            <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="-ml-1">
                <ArrowLeftIcon className="h-4 w-4" />
                All Tickets
            </Button>

            {/* Header card */}
            <Card>
                <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0 flex-1">
                            <p className="text-xs font-mono text-slate-400">#{ticket.id.slice(0, 8).toUpperCase()}</p>
                            <CardTitle className="mt-1 text-xl">{ticket.title}</CardTitle>
                        </div>
                        <div className="flex shrink-0 flex-col items-end gap-2">
                            <StatusBadge status={ticket.status} />
                            <PriorityBadge priority={ticket.priority} />
                        </div>
                    </div>

                    {/* Meta row */}
                    <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-slate-500">
                        <span className="flex items-center gap-1.5">
                            <UserIcon className="h-4 w-4" />
                            {ticket.client_name}
                        </span>
                        <span className="flex items-center gap-1.5">
                            <TagIcon className="h-4 w-4" />
                            {ticket.category}
                        </span>
                        <span className="flex items-center gap-1.5">
                            <CalendarIcon className="h-4 w-4" />
                            Created {format(new Date(ticket.created_at), 'MMM d, yyyy · HH:mm')}
                        </span>
                        {ticket.updated_at && ticket.updated_at !== ticket.created_at && (
                            <span className="flex items-center gap-1.5">
                                <CalendarIcon className="h-4 w-4" />
                                Updated {format(new Date(ticket.updated_at), 'MMM d, yyyy · HH:mm')}
                            </span>
                        )}
                    </div>
                </CardHeader>

                <Separator />

                <CardContent className="pt-6">
                    <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                        {ticket.description}
                    </p>

                    {/* Attachment */}
                    {ticket.attachment_url && (
                        <div className="mt-4">
                            <a
                                href={`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}${ticket.attachment_url}`}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100 transition-colors"
                            >
                                <PaperclipIcon className="h-4 w-4 text-slate-400" />
                                {ticket.attachment_name ?? 'Download attachment'}
                            </a>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Status timeline */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Status Flow</CardTitle>
                </CardHeader>
                <CardContent>
                    <ol className="flex items-center justify-between gap-1">
                        {STATUS_FLOW.map((status, idx) => {
                            const isCompleted = idx < currentIndex
                            const isCurrent = idx === currentIndex
                            const Icon = STATUS_ICON[status]

                            return (
                                <li key={status} className="flex flex-1 items-center">
                                    <div className="flex flex-col items-center gap-1 flex-1">
                                        <div
                                            className={`flex h-8 w-8 items-center justify-center rounded-full border-2 transition-colors ${isCompleted
                                                ? 'border-emerald-500 bg-emerald-500 text-white'
                                                : isCurrent
                                                    ? 'border-blue-600 bg-blue-600 text-white'
                                                    : 'border-slate-300 bg-white text-slate-400'
                                                }`}
                                        >
                                            {isCompleted ? (
                                                <CheckIcon className="h-4 w-4" />
                                            ) : (
                                                <Icon className="h-4 w-4" />
                                            )}
                                        </div>
                                        <span
                                            className={`text-center text-xs font-medium ${isCurrent ? 'text-blue-600' : isCompleted ? 'text-emerald-600' : 'text-slate-400'
                                                }`}
                                        >
                                            {STATUS_LABELS[status]}
                                        </span>
                                    </div>
                                    {/* Connector line */}
                                    {idx < STATUS_FLOW.length - 1 && (
                                        <div
                                            className={`h-0.5 flex-1 -mt-5 ${idx < currentIndex ? 'bg-emerald-400' : 'bg-slate-200'}`}
                                        />
                                    )}
                                </li>
                            )
                        })}
                    </ol>
                </CardContent>
            </Card>

            {/* Actions */}
            {isAgent && (
                <div className="flex flex-wrap items-center justify-between gap-3">
                    {/* Go back */}
                    {prevStatus && !isClosed && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => advanceStatus(prevStatus)}
                            disabled={isAdvancing}
                            className="gap-2"
                        >
                            <ChevronLeftIcon className="h-4 w-4" />
                            Back to {STATUS_LABELS[prevStatus]}
                        </Button>
                    )}

                    {/* Advance status */}
                    {!isClosed && nextStatus && (
                        <Button
                            onClick={() => advanceStatus(nextStatus)}
                            disabled={isAdvancing}
                            className="gap-2"
                        >
                            <CheckCircle2Icon className="h-4 w-4" />
                            {isAdvancing ? 'Updating…' : `Mark as ${STATUS_LABELS[nextStatus]}`}
                        </Button>
                    )}

                    {/* Jump to closed */}
                    {!isClosed && ticket.status !== 'closed' && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                if (confirm('Close this ticket? This action is final.')) {
                                    advanceStatus('closed')
                                }
                            }}
                            disabled={isAdvancing}
                        >
                            Close Ticket
                        </Button>
                    )}

                    {/* Reopen */}
                    {isClosed && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => advanceStatus('open')}
                            disabled={isAdvancing}
                            className="gap-2"
                        >
                            <CircleIcon className="h-4 w-4" />
                            {isAdvancing ? 'Reopening…' : 'Reopen Ticket'}
                        </Button>
                    )}

                    {/* Delete */}
                    <Button
                        variant="destructive"
                        size="sm"
                        className="ml-auto"
                        disabled={isDeleting}
                        onClick={() => {
                            if (confirm('Delete this ticket permanently? This cannot be undone.')) {
                                remove()
                            }
                        }}
                    >
                        {isDeleting ? 'Deleting…' : 'Delete Ticket'}
                    </Button>
                </div>
            )}

            {/* Replies */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">
                        Replies {replies.length > 0 && <span className="ml-1 text-slate-400 font-normal">({replies.length})</span>}
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {replies.length === 0 && (
                        <p className="text-sm text-slate-400 text-center py-4">No replies yet.</p>
                    )}
                    {replies.map((reply) => (
                        <div
                            key={reply.id}
                            className={`rounded-lg border px-4 py-3 space-y-1 ${reply.is_ai
                                ? 'border-violet-200 bg-violet-50'
                                : 'border-slate-200 bg-slate-50'
                                }`}
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium text-slate-800">{reply.author}</span>
                                    {reply.is_ai && (
                                        <span className="inline-flex items-center gap-1 rounded-full bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-700">
                                            <SparklesIcon className="h-3 w-3" />
                                            AI
                                        </span>
                                    )}
                                </div>
                                <span className="text-xs text-slate-400">
                                    {format(new Date(reply.created_at), 'MMM d, yyyy · HH:mm')}
                                </span>
                            </div>
                            <p className="text-sm whitespace-pre-wrap text-slate-700">{reply.body}</p>
                        </div>
                    ))}

                    <Separator />

                    {/* New reply form */}
                    <div className="space-y-3">
                        <div className="space-y-1.5">
                            <Label htmlFor="reply-body">Response</Label>
                            <Textarea
                                id="reply-body"
                                placeholder="Write your response to the client…"
                                rows={4}
                                value={replyBody}
                                onChange={(e) => setReplyBody(e.target.value)}
                            />
                        </div>
                        <div className="flex gap-2">
                            <Button
                                className="gap-2"
                                disabled={isSending || !replyBody.trim()}
                                onClick={() => sendReply()}
                            >
                                <SendIcon className="h-4 w-4" />
                                {isSending ? 'Sending…' : 'Send Reply'}
                            </Button>
                            {isAgent && (
                                <Button
                                    variant="outline"
                                    className="gap-2 border-violet-200 text-violet-700 hover:bg-violet-50"
                                    disabled={isGenerating}
                                    onClick={() => generateAiReply()}
                                >
                                    <SparklesIcon className="h-4 w-4" />
                                    {isGenerating ? 'Generating…' : 'Generate AI Reply'}
                                </Button>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
