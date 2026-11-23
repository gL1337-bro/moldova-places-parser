import { forwardRef, InputHTMLAttributes } from 'react'
import { cn } from '@/utils/helpers'

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn('input', className)}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'