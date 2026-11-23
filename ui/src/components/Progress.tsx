import { cn } from '@/utils/helpers'

interface ProgressProps {
  value: number
  max?: number
  className?: string
  showLabel?: boolean
  color?: 'primary' | 'green' | 'yellow' | 'red'
}

export function Progress({ value, max = 100, className, showLabel = true, color = 'primary' }: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const colors = {
    primary: 'bg-primary-600',
    green: 'bg-green-600',
    yellow: 'bg-yellow-500',
    red: 'bg-red-600',
  }

  return (
    <div className={cn('w-full', className)}>
      <div className="flex items-center justify-between text-sm mb-1">
        <span className="text-gray-600">Прогресс</span>
        {showLabel && <span className="font-medium text-gray-900">{Math.round(percentage)}%</span>}
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-300', colors[color])}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

interface StepIndicatorProps {
  currentStep: number
  totalSteps: number
  steps: { label: string; description?: string }[]
  className?: string
}

export function StepIndicator({ currentStep, totalSteps, steps, className }: StepIndicatorProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {steps.map((step, index) => {
        const stepNumber = index + 1
        const isActive = stepNumber === currentStep
        const isCompleted = stepNumber < currentStep

        return (
          <div key={stepNumber} className="flex items-start gap-4">
            <div className="flex-shrink-0 flex items-center justify-center">
              <div
                className={cn(
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all',
                  isActive
                    ? 'bg-primary-600 text-white'
                    : isCompleted
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-500'
                )}
              >
                {isCompleted ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  stepNumber
                )}
              </div>
            </div>
            <div className="flex-1 min-w-0 pt-1">
              <div className="flex items-center gap-2">
                <h4 className={cn('font-medium', isActive ? 'text-gray-900' : 'text-gray-700')}>
                  {step.label}
                </h4>
                {isActive && (
                  <span className="badge bg-primary-100 text-primary-800">Текущий</span>
                )}
                {isCompleted && (
                  <span className="badge bg-green-100 text-green-800">Готово</span>
                )}
              </div>
              {step.description && (
                <p className={cn('text-sm mt-1', isActive ? 'text-gray-600' : 'text-gray-400')}>
                  {step.description}
                </p>
              )}
            </div>
            {index < totalSteps - 1 && (
              <div className="absolute left-3 top-10 bottom-0 w-0.5" style={{ marginLeft: '4px' }}>
                <div
                  className={cn('h-full rounded', isCompleted ? 'bg-green-300' : 'bg-gray-200')}
                />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}