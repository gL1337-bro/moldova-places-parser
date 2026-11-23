import { cn } from '@/utils/helpers'
import { Button } from './Button'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}

export function Pagination({ currentPage, totalPages, onPageChange, className }: PaginationProps) {
  if (totalPages <= 1) return null

  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages, start + maxVisible - 1)

  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return (
    <nav className={cn('flex items-center justify-center gap-2', className)} aria-label="Pagination">
      <Button
        variant="secondary"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Предыдущая страница"
      >
        <ChevronLeft className="w-4 h-4" />
      </Button>

      {start > 1 && (
        <>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onPageChange(1)}
            className={cn(currentPage === 1 && 'bg-primary-100 text-primary-700')}
          >
            1
          </Button>
          {start > 2 && (
            <span className="px-2 text-gray-400">...</span>
          )}
        </>
      )}

      {pages.map((page) => (
        <Button
          key={page}
          variant={currentPage === page ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => onPageChange(page)}
          className={cn(currentPage === page && 'bg-primary-600 text-white')}
        >
          {page}
        </Button>
      ))}

      {end < totalPages && (
        <>
          {end < totalPages - 1 && (
            <span className="px-2 text-gray-400">...</span>
          )}
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onPageChange(totalPages)}
            className={cn(currentPage === totalPages && 'bg-primary-100 text-primary-700')}
          >
            {totalPages}
          </Button>
        </>
      )}

      <Button
        variant="secondary"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="Следующая страница"
      >
        <ChevronRight className="w-4 h-4" />
      </Button>
    </nav>
  )
}