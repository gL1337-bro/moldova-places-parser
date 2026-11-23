import { useState, useMemo } from 'react'
import { DataTable, Pagination, FilterBar, Badge } from '@/components'
import { usePlaces, useExport } from '@/hooks/usePipeline'
import { Place } from '@/api/client'
import { ExternalLink, Phone, Mail, MapPin, Clock, Globe, Star } from 'lucide-react'
import { formatNumber, getPriorityBadgeClass, getGroupBadgeClass, truncate, openInNewTab, cn } from '@/utils/helpers'

const columns = [
  { key: 'name', header: 'Название', width: '200px' },
  { key: 'category', header: 'Категория', width: '120px' },
  { key: 'city', header: 'Город', width: '120px' },
  { key: 'address', header: 'Адрес', width: '250px' },
  { key: 'phone', header: 'Телефон', width: '140px' },
  { key: 'opening_hours', header: 'Часы работы', width: '150px' },
  { key: 'social_url', header: 'Соцсеть', width: '150px' },
  { key: 'group', header: 'Группа', width: '80px' },
  { key: 'priority_score', header: 'Баллы', width: '80px' },
  { key: 'priority_level', header: 'Приоритет', width: '100px' },
  { key: 'actions', header: 'Действия', width: '100px' },
]

export function PlacesPage() {
  const [group, setGroup] = useState('all')
  const [priority, setPriority] = useState('all')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(50)

  const { places, total, total_pages, loading, error, refetch } = usePlaces({
    group,
    priority,
    page,
    per_page: perPage,
    search,
  })

  const { exportData, loading: exportLoading } = useExport()

  const handleExport = (format: 'excel' | 'csv') => {
    exportData(format, group)
  }

  const handleRefresh = () => {
    refetch()
  }

  const getPriorityIcon = (level: string) => {
    switch (level) {
      case 'high': return <Star className="w-4 h-4 text-red-500" />
      case 'medium': return <Star className="w-4 h-4 text-yellow-500" />
      case 'low': return <Star className="w-4 h-4 text-green-500" />
      default: return <Star className="w-4 h-4 text-gray-400" />
    }
  }

  const enhancedColumns = useMemo(() => columns.map(col => {
    if (col.key === 'category') {
      return { ...col, render: (row: Place) => <Badge variant="default">{row.category}</Badge> }
    }
    if (col.key === 'group') {
      return {
        ...col,
        render: (row: Place) => (
          <Badge variant={row.group === 'A' ? 'group-a' : 'group-b'}>
            Группа {row.group}
          </Badge>
        )
      }
    }
    if (col.key === 'priority_level') {
      return {
        ...col,
        render: (row: Place) => (
          <Badge variant={getPriorityBadgeClass(row.priority_level) as any}>
            {getPriorityIcon(row.priority_level)} {row.priority_level}
          </Badge>
        )
      }
    }
    if (col.key === 'phone') {
      return {
        ...col,
        render: (row: Place) => row.phone ? (
          <a href={`tel:${row.phone}`} className="text-primary-600 hover:underline flex items-center gap-1">
            <Phone className="w-3 h-3" />
            {truncate(row.phone, 18)}
          </a>
        ) : <span className="text-gray-400">—</span>
      }
    }
    if (col.key === 'social_url') {
      return {
        ...col,
        render: (row: Place) => row.social_url ? (
          <a href={row.social_url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline flex items-center gap-1">
            <Globe className="w-3 h-3" />
            {truncate(row.social_url, 25)}
          </a>
        ) : <span className="text-gray-400">—</span>
      }
    }
    if (col.key === 'address') {
      return {
        ...col,
        render: (row: Place) => (
          <span className="flex items-center gap-1" title={row.address}>
            <MapPin className="w-3 h-3 text-gray-400" />
            {truncate(row.address, 40)}
          </span>
        )
      }
    }
    if (col.key === 'opening_hours') {
      return {
        ...col,
        render: (row: Place) => row.opening_hours ? (
          <span className="flex items-center gap-1" title={row.opening_hours}>
            <Clock className="w-3 h-3 text-gray-400" />
            {truncate(row.opening_hours, 20)}
          </span>
        ) : <span className="text-gray-400">—</span>
      }
    }
    if (col.key === 'priority_score') {
      return {
        ...col,
        render: (row: Place) => (
          <span className="font-mono font-medium">{row.priority_score.toFixed(1)}</span>
        )
      }
    }
    if (col.key === 'actions') {
      return {
        ...col,
        render: (row: Place) => (
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); openInNewTab(row.google_maps_link) }}
              className="p-1.5 text-gray-500 hover:text-primary-600 hover:bg-gray-100 rounded transition-colors"
              title="Открыть в Google Maps"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          </div>
        )
      }
    }
    return col
  }), [])

  return (
    <div className="space-y-4">
      <FilterBar
        group={group}
        setGroup={setGroup}
        priority={priority}
        setPriority={setPriority}
        search={search}
        setSearch={setSearch}
        page={page}
        perPage={perPage}
        total={total}
        onExport={handleExport}
        onRefresh={handleRefresh}
        exporting={exportLoading}
      />

      <DataTable
        columns={enhancedColumns}
        data={places}
        keyExtractor={(row) => row.osm_id}
        loading={loading}
        emptyMessage={total === 0 ? 'Заведения не найдены. Запустите пайплайн.' : 'Нет данных для отображения'}
      />

      <Pagination
        currentPage={page}
        totalPages={total_pages}
        onPageChange={setPage}
      />

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          Ошибка загрузки: {error}
        </div>
      )}
    </div>
  )
}