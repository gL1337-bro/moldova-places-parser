import { cn } from '@/utils/helpers'
import { Card } from './Card'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  trend?: string
  trendUp?: boolean
  className?: string
}

export function StatCard({ title, value, icon, trend, trendUp, className }: StatCardProps) {
  return (
    <Card className={cn('stat-card', className)} padding="md">
      <div className="p-3 bg-primary-100 rounded-xl text-primary-600">
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {trend && (
          <p className={cn('text-xs mt-1', trendUp ? 'text-green-600' : 'text-red-600')}>
            {trend}
          </p>
        )}
      </div>
    </Card>
  )
}