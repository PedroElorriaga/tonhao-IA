import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { PlusIcon, SearchIcon, RefreshCwIcon, TicketIcon } from 'lucide-react'
import { getTickets } from '@/api/tickets'
import { TicketCard } from '@/components/TicketCard'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import type { TicketFilters, TicketStatus, TicketPriority } from '@/types/ticket'
import { TICKET_CATEGORIES } from '@/types/ticket'

const PAGE_SIZE = 10

export default function Dashboard() {
    const [filters, setFilters] = useState<TicketFilters>({
        status: '',
        priority: '',
        category: '',
        search: '',
        page: 1,
        page_size: PAGE_SIZE,
    })
    const [searchDraft, setSearchDraft] = useState('')

    const { data, isLoading, isError, refetch, isFetching } = useQuery({
        queryKey: ['tickets', filters],
        queryFn: () => getTickets(filters),
    })

    function handleFilterChange(key: keyof TicketFilters, value: string) {
        setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
    }

    function handleSearch(e: React.FormEvent) {
        e.preventDefault()
        setFilters((prev) => ({ ...prev, search: searchDraft, page: 1 }))
    }

    const tickets = data?.items ?? []
    const total = data?.total ?? 0
    const currentPage = filters.page ?? 1
    const totalPages = Math.ceil(total / PAGE_SIZE)

    return (
        <div className="space-y-6">
            {/* Page header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Tickets</h1>
                    <p className="text-sm text-slate-500">
                        {isLoading ? 'Loading…' : `${total} ticket${total !== 1 ? 's' : ''} total`}
                    </p>
                </div>
                <Link to="/tickets/new">
                    <Button>
                        <PlusIcon className="h-4 w-4" />
                        New Ticket
                    </Button>
                </Link>
            </div>

            {/* Filters bar */}
            <div className="flex flex-wrap gap-3">
                {/* Search */}
                <form onSubmit={handleSearch} className="flex min-w-[220px] flex-1 items-center gap-2">
                    <div className="relative flex-1">
                        <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                        <Input
                            placeholder="Search tickets…"
                            className="pl-9"
                            value={searchDraft}
                            onChange={(e) => setSearchDraft(e.target.value)}
                        />
                    </div>
                    <Button type="submit" variant="outline" size="icon" aria-label="Search">
                        <SearchIcon className="h-4 w-4" />
                    </Button>
                </form>

                {/* Status filter */}
                <Select
                    className="w-40"
                    value={filters.status ?? ''}
                    onChange={(e) => handleFilterChange('status', e.target.value as TicketStatus | '')}
                    aria-label="Filter by status"
                >
                    <option value="">All statuses</option>
                    <option value="open">Open</option>
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="solved">Solved</option>
                    <option value="closed">Closed</option>
                </Select>

                {/* Priority filter */}
                <Select
                    className="w-40"
                    value={filters.priority ?? ''}
                    onChange={(e) => handleFilterChange('priority', e.target.value as TicketPriority | '')}
                    aria-label="Filter by priority"
                >
                    <option value="">All priorities</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                </Select>

                {/* Category filter */}
                <Select
                    className="w-48"
                    value={filters.category ?? ''}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    aria-label="Filter by category"
                >
                    <option value="">All categories</option>
                    {TICKET_CATEGORIES.map((cat) => (
                        <option key={cat} value={cat}>
                            {cat}
                        </option>
                    ))}
                </Select>

                {/* Refresh */}
                <Button
                    variant="outline"
                    size="icon"
                    onClick={() => refetch()}
                    disabled={isFetching}
                    aria-label="Refresh"
                >
                    <RefreshCwIcon className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
                </Button>
            </div>

            {/* Ticket list */}
            {isLoading ? (
                <div className="space-y-3">
                    {Array.from({ length: 5 }).map((_, i) => (
                        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-200" />
                    ))}
                </div>
            ) : isError ? (
                <div className="flex flex-col items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-10 text-center">
                    <p className="font-medium text-red-700">Failed to load tickets</p>
                    <Button variant="outline" onClick={() => refetch()}>
                        Try again
                    </Button>
                </div>
            ) : tickets.length === 0 ? (
                <div className="flex flex-col items-center gap-3 rounded-xl border border-slate-200 bg-white p-16 text-center">
                    <TicketIcon className="h-10 w-10 text-slate-300" />
                    <p className="font-medium text-slate-600">No tickets found</p>
                    <p className="text-sm text-slate-400">
                        {filters.search || filters.status || filters.priority || filters.category
                            ? 'Try adjusting your filters'
                            : 'Create the first ticket to get started'}
                    </p>
                    <Link to="/tickets/new">
                        <Button variant="outline" size="sm">
                            <PlusIcon className="h-4 w-4" />
                            New Ticket
                        </Button>
                    </Link>
                </div>
            ) : (
                <div className="space-y-3">
                    {tickets.map((ticket) => (
                        <TicketCard key={ticket.id} ticket={ticket} />
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-500">
                        Page {currentPage} of {totalPages}
                    </p>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={currentPage <= 1}
                            onClick={() => setFilters((p) => ({ ...p, page: (p.page ?? 1) - 1 }))}
                        >
                            Previous
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={currentPage >= totalPages}
                            onClick={() => setFilters((p) => ({ ...p, page: (p.page ?? 1) + 1 }))}
                        >
                            Next
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}
