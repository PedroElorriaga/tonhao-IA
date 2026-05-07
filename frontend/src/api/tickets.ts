import client from './client'
import type {
    Ticket,
    CreateTicketPayload,
    UpdateTicketPayload,
    TicketFilters,
    PaginatedTickets,
} from '@/types/ticket'

export async function getTickets(filters?: TicketFilters): Promise<PaginatedTickets> {
    const params: Record<string, string | number> = {}
    if (filters?.status) params.status = filters.status
    if (filters?.priority) params.priority = filters.priority
    if (filters?.category) params.category = filters.category
    if (filters?.search) params.search = filters.search
    if (filters?.page) params.page = filters.page
    if (filters?.page_size) params.page_size = filters.page_size

    const { data } = await client.get<PaginatedTickets>('/tickets', { params })
    return data
}

export async function getTicket(id: string): Promise<Ticket> {
    const { data } = await client.get<Ticket>(`/tickets/${id}`)
    return data
}

export async function createTicket(payload: CreateTicketPayload): Promise<Ticket> {
    const form = new FormData()
    form.append('title', payload.title)
    form.append('description', payload.description)
    form.append('priority', payload.priority)
    form.append('category', payload.category)
    form.append('client_name', payload.client_name)
    if (payload.attachment) {
        form.append('attachment', payload.attachment)
    }

    const { data } = await client.post<Ticket>('/tickets', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}

export async function updateTicket(id: string, payload: UpdateTicketPayload): Promise<Ticket> {
    const { data } = await client.patch<Ticket>(`/tickets/${id}`, payload)
    return data
}

export async function deleteTicket(id: string): Promise<void> {
    await client.delete(`/tickets/${id}`)
}
