import { useState } from 'react'
import { Card, StatCard, Progress, StepIndicator } from '@/components'
import { usePipelineStatus } from '@/hooks/usePipeline'
import { useStats } from '@/hooks/usePipeline'
import { Users, MapPin, Globe, AlertTriangle, TrendingUp, Clock } from 'lucide-react'
import { formatNumber } from '@/utils/helpers'

const pipelineSteps = [
  { label: 'Выгрузка из OSM', description: 'Скачивание данных по районам Молдовы через Overpass API' },
  { label: 'Классификация сайтов', description: 'Разделение на группы: A (нет сайта), B (только соцсети), C (свой сайт)' },
  { label: 'Расчёт приоритета', description: 'Подсчёт очков по телефону, часам, соцсетям, городу, категории' },
  { label: 'Экспорт в Excel/CSV', description: 'Формирование таблиц для ручной проверки с ссылками на Google Maps' },
]

export function DashboardPage() {
  const { status, startPipeline } = usePipelineStatus()
  const { stats } = useStats()

  const isRunning = status?.status === 'running'
  const isCompleted = status?.status === 'completed'

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Всего заведений"
          value={stats?.total ? formatNumber(stats.total) : '—'}
          icon={<MapPin className="w-6 h-6" />}
        />
        <StatCard
          title="Группа A (нет сайта)"
          value={stats?.by_group?.A ? formatNumber(stats.by_group.A) : '—'}
          icon={<Globe className="w-6 h-6" />}
        />
        <StatCard
          title="Группа B (только соцсети)"
          value={stats?.by_group?.B ? formatNumber(stats.by_group.B) : '—'}
          icon={<Users className="w-6 h-6" />}
        />
        <StatCard
          title="Высокий приоритет"
          value={stats?.by_priority_level?.high ? formatNumber(stats.by_priority_level.high) : '—'}
          icon={<TrendingUp className="w-6 h-6" />}
        />
      </div>

      {/* Pipeline Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Статус пайплайна</h3>
            {status && (
              <span className={cn('badge', {
                'bg-blue-100 text-blue-800': status.status === 'running',
                'bg-green-100 text-green-800': status.status === 'completed',
                'bg-red-100 text-red-800': status.status === 'error',
                'bg-gray-100 text-gray-800': status.status === 'idle',
              })}>
                {status.status === 'running' && 'Выполняется'}
                {status.status === 'completed' && 'Завершён'}
                {status.status === 'error' && 'Ошибка'}
                {status.status === 'idle' && 'Готов к запуску'}
              </span>
            )}
          </div>

          {status && (
            <>
              <Progress
                value={status.progress}
                color={status.status === 'error' ? 'red' : status.status === 'completed' ? 'green' : 'primary'}
              />
              <p className="mt-2 text-sm text-gray-600">{status.message}</p>
              {status.error && (
                <p className="mt-2 text-sm text-red-600">Ошибка: {status.error}</p>
              )}
            </>
          )}

          <StepIndicator
            currentStep={status?.current_step || 0}
            totalSteps={4}
            steps={pipelineSteps}
            className="mt-6"
          />

          {status?.status === 'idle' && (
            <div className="mt-6 text-center">
              <button
                onClick={startPipeline}
                className="btn-primary px-8 py-3 text-base"
              >
                Запустить полный пайплайн
              </button>
              <p className="mt-2 text-sm text-gray-500">
                Это займёт несколько минут. Можно закрыть окно — процесс продолжится в фоне.
              </p>
            </div>
          )}

          {status?.status === 'completed' && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-medium text-green-800 mb-2">Пайплайн успешно завершён!</h4>
              <p className="text-sm text-green-700">
                Найдено {status.places_count} заведений. Перейдите на вкладку «Заведения» для просмотра и экспорта.
              </p>
            </div>
          )}
        </Card>

        {/* Quick Stats */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">Быстрая статистика</h3>
          <div className="space-y-4">
            {stats && (
              <>
                <div>
                  <p className="text-sm text-gray-500">С телефоном</p>
                  <p className="text-2xl font-bold">{formatNumber(stats.with_phone)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">С email</p>
                  <p className="text-2xl font-bold">{formatNumber(stats.with_email)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Соцсети</p>
                  <p className="text-2xl font-bold">{formatNumber(stats.with_social)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Часы работы</p>
                  <p className="text-2xl font-bold">{formatNumber(stats.with_opening_hours)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Средний приоритет</p>
                  <p className="text-2xl font-bold">{stats.avg_priority_score.toFixed(1)}</p>
                </div>
              </>
            )}
          </div>
        </Card>
      </div>

      {/* Top Categories & Cities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-4">Топ категории</h3>
          <div className="space-y-3">
            {stats?.by_category && Object.entries(stats.by_category)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 8)
              .map(([cat, count]) => (
                <div key={cat} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{cat}</span>
                  <span className="font-medium text-gray-900">{formatNumber(count)}</span>
                </div>
              ))}
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-4">Топ города</h3>
          <div className="space-y-3">
            {stats?.by_city && Object.entries(stats.by_city)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 8)
              .map(([city, count]) => (
                <div key={city} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{city}</span>
                  <span className="font-medium text-gray-900">{formatNumber(count)}</span>
                </div>
              ))}
          </div>
        </Card>
      </div>
    </div>
  )
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ')
}