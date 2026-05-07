import { Link } from 'react-router-dom'
import { CalendarIcon, UserIcon, TagIcon } from 'lucide-react'
import { format } from 'date-fns'
import { Card, CardContent } from '@/components/ui/card'
import { StatusBadge } from '@/components/StatusBadge'
import { PriorityBadge } from '@/components/PriorityBadge'
import type { Ticket } from '@/types/ticket'

interface TicketCardProps {
    ticket: Ticket
}

export function TicketCard({ ticket }: TicketCardProps) {
    return (
        <Link to={`/tickets/${ticket.id}`} className="block focus-visible:outline-none group">
            <Card className="transition-shadow group-hover:shadow-md group-focus-visible:ring-2 group-focus-visible:ring-slate-900">
                <CardContent className="p-5">
                    <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                            <p className="truncate font-medium text-slate-900 group-hover:text-blue-600 transition-colors">
                                {ticket.title}
                            </p>
                            <p className="mt-1 line-clamp-2 text-sm text-slate-500">{ticket.description}</p>
                        </div>
                        <div className="flex shrink-0 flex-col items-end gap-1.5">
                            <StatusBadge status={ticket.status} />
                            <PriorityBadge priority={ticket.priority} />
                        </div>
                    </div>

                    <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                            <UserIcon className="h-3 w-3" />
                            {ticket.client_name}
                        </span>
                        <span className="flex items-center gap-1">
                            <TagIcon className="h-3 w-3" />
                            {ticket.category}
                        </span>
                        <span className="flex items-center gap-1">
                            <CalendarIcon className="h-3 w-3" />
                            {format(new Date(ticket.created_at), 'MMM d, yyyy')}
                        </span>
                        <span className="ml-auto font-mono text-xs text-slate-400">#{ticket.id.slice(0, 8)}</span>
                    </div>
                </CardContent>
            </Card>
        </Link>
    )
}
