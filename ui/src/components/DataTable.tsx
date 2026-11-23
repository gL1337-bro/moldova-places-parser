import { forwardRef, TableHTMLAttributes } from 'react'
import { cn } from '@/utils/helpers'

interface Column<T> {
  key: string
  header: string
  render?: (row: T, index: number) => React.ReactNode
  width?: string
  align?: 'left' | 'center' | 'right'
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (row: T) => string
  onRowClick?: (row: T) => void
  className?: string
  emptyMessage?: string
  loading?: boolean
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  className,
  emptyMessage = 'Нет данных',
  loading = false,
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className={cn('table-container', className)}>
        <table className="table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key} style={{ width: col.width }} className={cn(col.align === 'center' && 'text-center', col.align === 'right' && 'text-right')}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <tr key={i}>
                {columns.map((col) => (
                  <td key={col.key} className={cn(col.align === 'center' && 'text-center', col.align === 'right' && 'text-right')}>
                    <div className="h-4 bg-gray-200 animate-pulse rounded w-3/4" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className={cn('table-container', className)}>
        <div className="p-12 text-center text-gray-500">
          {emptyMessage}
        </div>
      </div>
    )
  }

  return (
    <div className={cn('table-container scrollbar-thin', className)}>
      <table className="table">
        <thead className="sticky top-0 z-10">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                style={{ width: col.width, minWidth: col.width }}
                className={cn(
                  'whitespace-nowrap',
                  col.align === 'center' && 'text-center',
                  col.align === 'right' && 'text-right'
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {data.map((row, rowIndex) => (
            <tr
              key={keyExtractor(row)}
              className={cn(
                onRowClick && 'cursor-pointer hover:bg-gray-50',
                rowIndex % 2 === 0 && 'bg-white',
                rowIndex % 2 === 1 && 'bg-gray-50/50'
              )}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={cn(
                    'whitespace-nowrap',
                    col.align === 'center' && 'text-center',
                    col.align === 'right' && 'text-right'
                  )}
                >
                  {col.render ? col.render(row, rowIndex) : String((row as any)[col.key] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}