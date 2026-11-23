import { cn } from '@/utils/helpers'
import { Button } from './Button'
import { Input } from './Input'
import { Select } from './Select'
import { Search, Filter, Download, RefreshCw } from 'lucide-react'

interface FilterBarProps {
  group: string
  setGroup: (value: string) => void
  priority: string
  setPriority: (value: string) => void
  search: string
  setSearch: (value: string) => void
  page: number
  perPage: number
  total: number
  onExport: (format: 'excel' | 'csv') => void
  onRefresh: () => void
  exporting?: boolean
}

export function FilterBar({
  group,
  setGroup,
  priority,
  setPriority,
  search,
  setSearch,
  page,
  perPage,
  total,
  onExport,
  onRefresh,
  exporting,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-4 p-4 bg-white border-b border-gray-200">
      <div className="relative flex-1 min-w-[200px] max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input
          placeholder="Поиск по названию, городу, адресу..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="flex items-center gap-2">
        <Select
          value={group}
          onChange={(e) => setGroup(e.target.value)}
          className="w-[140px]"
        >
          <option value="all">Все группы</option>
          <option value="A">Группа A (нет сайта)</option>
          <option value="B">Группа B (только соцсети)</option>
        </Select>

        <Select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="w-[140px]"
        >
          <option value="all">Все приоритеты</option>
          <option value="high">Высокий</option>
          <option value="medium">Средний</option>
          <option value="low">Низкий</option>
        </Select>

        <Select
          value={perPage}
          onChange={(e) => setPerPage(Number(e.target.value))}
          className="w-[100px]"
        >
          <option value={25}>25</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </Select>
      </div>

      <div className="flex items-center gap-2 ml-auto">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onExport('excel')}
          disabled={exporting}
          className="gap-2"
        >
          <Download className="w-4 h-4" />
          Excel
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onExport('csv')}
          disabled={exporting}
          className="gap-2"
        >
          <Download className="w-4 h-4" />
          CSV
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={onRefresh}
          className="gap-2"
        >
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      <div className="w-full text-sm text-gray-500 pt-2 border-t border-gray-100 mt-2">
        Показано {Math.min((page - 1) * perPage + 1, total)}–{Math.min(page * perPage, total)} из {total} записей
      </div>
    </div>
  )
}

function setPerPage(value: number) {
  // This will be handled by parent component
  console.log('setPerPage', value)
}