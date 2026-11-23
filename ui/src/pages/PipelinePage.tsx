import { Card, Progress, StepIndicator } from '@/components'
import { usePipelineStatus } from '@/hooks/usePipeline'
import { Play, Pause, RotateCw, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { pipelineSteps } from './DashboardPage'

export function PipelinePage() {
  const { status, startPipeline, refetch } = usePipelineStatus()

  const isRunning = status?.status === 'running'

  return (
    <div className="space-y-6 max-w-3xl">
      <Card>
        <h3 className="text-lg font-semibold mb-4">Управление пайплайном</h3>

        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium">Статус: </h4>
            <span className={cn('badge', {
              'bg-blue-100 text-blue-800': status?.status === 'running',
              'bg-green-100 text-green-800': status?.status === 'completed',
              'bg-red-100 text-red-800': status?.status === 'error',
              'bg-gray-100 text-gray-800': status?.status === 'idle',
            })}>
              {status?.status === 'running' && <><Loader2 className="w-3 h-3 mr-1 animate-spin" /> Выполняется</>}
              {status?.status === 'completed' && <><CheckCircle className="w-3 h-3 mr-1" /> Завершён</>}
              {status?.status === 'error' && <><AlertCircle className="w-3 h-3 mr-1" /> Ошибка</>}
              {status?.status === 'idle' && 'Готов к запуску'}
            </span>
          </div>

          {status && (
            <>
              <Progress value={status.progress} />
              <p className="mt-2 text-sm text-gray-600">{status.message}</p>
              {status.error && (
                <p className="mt-2 text-sm text-red-600">Ошибка: {status.error}</p>
              )}
            </>
          )}

          <div className="mt-6 flex gap-3">
            <button
              onClick={startPipeline}
              disabled={isRunning}
              className="btn-primary flex-1 gap-2"
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Выполняется...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Запустить пайплайн
                </>
              )}
            </button>
            <button
              onClick={refetch}
              className="btn-secondary gap-2"
            >
              <RotateCw className="w-4 h-4" />
              Обновить
            </button>
          </div>
        </div>

        <h4 className="font-medium mb-4">Этапы пайплайна</h4>
        <StepIndicator
          currentStep={status?.current_step || 0}
          totalSteps={4}
          steps={pipelineSteps}
        />
      </Card>

      {status?.status === 'completed' && (
        <Card className="border-green-200 bg-green-50">
          <h3 className="text-lg font-semibold text-green-800 mb-2 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Пайплайн успешно завершён!
          </h3>
          <p className="text-green-700">
            Найдено {status.places_count} заведений.
            Группа A: {status.groups.A}, Группа B: {status.groups.B}.
            Высокий приоритет: {status.priority_distribution.high}.
          </p>
          <p className="mt-2 text-sm text-green-600">
            Перейдите на вкладку «Заведения» для просмотра, фильтрации и экспорта данных.
          </p>
        </Card>
      )}

      {status?.status === 'error' && (
        <Card className="border-red-200 bg-red-50">
          <h3 className="text-lg font-semibold text-red-800 mb-2 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Ошибка выполнения
          </h3>
          <p className="text-red-700">{status.error}</p>
          <p className="mt-2 text-sm text-red-600">
            Проверьте подключение к интернету и попробуйте запустить снова.
          </p>
        </Card>
      )}
    </div>
  )
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ')
}