import { Badge, type BadgeProps } from '@/components/ui/badge'
import { PRIORITY_LABELS, type TicketPriority } from '@/types/ticket'

type BadgeVariant = BadgeProps['variant']

const PRIORITY_VARIANT: Record<TicketPriority, BadgeVariant> = {
    low: 'secondary',
    medium: 'info',
    high: 'warning',
    critical: 'destructive',
}

interface PriorityBadgeProps {
    priority: TicketPriority
    className?: string
}

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
    return (
        <Badge variant={PRIORITY_VARIANT[priority]} className={className}>
            {PRIORITY_LABELS[priority]}
        </Badge>
    )
}
