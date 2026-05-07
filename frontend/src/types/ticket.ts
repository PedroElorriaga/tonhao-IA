export type TicketStatus = 'open' | 'pending' | 'in_progress' | 'solved' | 'closed'
export type TicketPriority = 'low' | 'medium' | 'high' | 'critical'

export const STATUS_LABELS: Record<TicketStatus, string> = {
    open: 'Open',
    pending: 'Pending',
    in_progress: 'In Progress',
    solved: 'Solved',
    closed: 'Closed',
}

export const STATUS_FLOW: TicketStatus[] = ['open', 'pending', 'in_progress', 'solved', 'closed']

export const PRIORITY_LABELS: Record<TicketPriority, string> = {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical',
}

export const TICKET_CATEGORIES = [
    'Technical Support',
    'Billing',
    'Account',
    'Feature Request',
    'Bug Report',
    'General Inquiry',
    'Other',
] as const

export interface Ticket {
    id: string
    title: string
    description: string
    status: TicketStatus
    priority: TicketPriority
    category: string
    client_name: string
    created_at: string
    updated_at?: string
    attachment_url?: string
    attachment_name?: string
}

export interface CreateTicketPayload {
    title: string
    description: string
    priority: TicketPriority
    category: string
    client_name: string
    attachment?: File
}

export interface UpdateTicketPayload {
    status?: TicketStatus
    priority?: TicketPriority
    description?: string
}

export interface TicketFilters {
    status?: TicketStatus | ''
    priority?: TicketPriority | ''
    category?: string
    search?: string
    page?: number
    page_size?: number
}

export interface PaginatedTickets {
    items: Ticket[]
    total: number
    page: number
    page_size: number
}
