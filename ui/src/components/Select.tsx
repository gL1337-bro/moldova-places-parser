import { forwardRef, SelectHTMLAttributes } from 'react'
import { cn } from '@/utils/helpers'

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={cn('select', className)}
        {...props}
      >
        {children}
      </select>
    )
  }
)
Select.displayName = 'Select'