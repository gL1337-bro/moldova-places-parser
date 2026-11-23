import { cn } from '@/utils/helpers'

interface BadgeProps {
  className?: string
  variant?: 'default' | 'high' | 'medium' | 'low' | 'group-a' | 'group-b' | 'success' | 'warning' | 'danger'
  children: React.ReactNode
}

export function Badge({ className, variant = 'default', children }: BadgeProps) {
  const variants = {
    default: 'badge bg-gray-100 text-gray-800',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
    'group-a': 'badge-group-a',
    'group-b': 'badge-group-b',
    success: 'badge bg-green-100 text-green-800',
    warning: 'badge bg-yellow-100 text-yellow-800',
    danger: 'badge bg-red-100 text-red-800',
  }

  return (
    <span className={cn(variants[variant], className)}>
      {children}
    </span>
  )
}