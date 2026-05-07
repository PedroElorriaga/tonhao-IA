import { Badge, type BadgeProps } from '@/components/ui/badge'
import { STATUS_LABELS, type TicketStatus } from '@/types/ticket'

type BadgeVariant = BadgeProps['variant']

const STATUS_VARIANT: Record<TicketStatus, BadgeVariant> = {
    open: 'info',
    pending: 'warning',
    in_progress: 'purple',
    solved: 'success',
    closed: 'gray',
}

interface StatusBadgeProps {
    status: TicketStatus
    className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
    return (
        <Badge variant={STATUS_VARIANT[status]} className={className}>
            {STATUS_LABELS[status]}
        </Badge>
    )
}
