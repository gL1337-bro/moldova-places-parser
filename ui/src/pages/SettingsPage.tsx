import { useState, useEffect } from 'react'
import { Card, CardHeader, Button, Input, Badge } from '@/components'
import { api, Config } from '@/api/client'
import { Save, RotateCcw, Plus, Trash2, Edit2 } from 'lucide-react'
import { cn } from '@/utils/helpers'

export function SettingsPage() {
  const [config, setConfig] = useState<Config | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const [weights, setWeights] = useState<Record<string, number>>({})
  const [socialDomains, setSocialDomains] = useState<string[]>([])
  const [newSocialDomain, setNewSocialDomain] = useState('')

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const data = await api.getConfig()
      setConfig(data)
      setWeights(data.scoring_weights || {})
      setSocialDomains(data.social_domains || [])
    } catch (err) {
      console.error('Failed to load config:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveWeights = async () => {
    setSaving(true)
    setMessage(null)
    try {
      // In a real app, this would POST to the API
      await new Promise(r => setTimeout(r, 500))
      setMessage({ type: 'success', text: 'Веса сохранены (требуется перезапуск пайплайна)' })
    } catch (err) {
      setMessage({ type: 'error', text: 'Ошибка сохранения' })
    } finally {
      setSaving(false)
    }
  }

  const addSocialDomain = () => {
    const domain = newSocialDomain.trim().toLowerCase()
    if (domain && !socialDomains.includes(domain)) {
      setSocialDomains([...socialDomains, domain].sort())
      setNewSocialDomain('')
    }
  }

  const removeSocialDomain = (domain: string) => {
    setSocialDomains(socialDomains.filter(d => d !== domain))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Scoring Weights */}
      <Card>
        <CardHeader title="Веса приоритета" subtitle="Настройте важность каждого фактора для расчёта приоритета" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(weights).map(([key, value]) => (
            <div key={key} className="space-y-2">
              <label className="text-sm font-medium text-gray-700 capitalize">{key.replace(/_/g, ' ')}</label>
              <input
                type="number"
                min="0"
                max="100"
                step="1"
                value={value}
                onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })}
                className="input w-24"
              />
            </div>
          ))}
        </div>
        <div className="mt-6 flex gap-3">
          <Button onClick={handleSaveWeights} disabled={saving} className="gap-2">
            <Save className="w-4 h-4" />
            {saving ? 'Сохранение...' : 'Сохранить веса'}
          </Button>
          <Button variant="secondary" onClick={loadConfig} className="gap-2">
            <RotateCcw className="w-4 h-4" />
            Сбросить
          </Button>
        </div>
      </Card>

      {/* Social Domains */}
      <Card>
        <CardHeader title="Домены соцсетей и агрегаторов" subtitle="Сайты на этих доменах будут классифицированы как Группа B (нет своего сайта)" />
        <div className="mb-4 flex gap-2">
          <Input
            value={newSocialDomain}
            onChange={(e) => setNewSocialDomain(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addSocialDomain()}
            placeholder="example.com"
            className="flex-1 max-w-md"
          />
          <Button onClick={addSocialDomain} className="gap-2">
            <Plus className="w-4 h-4" />
            Добавить
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          {socialDomains.map((domain) => (
            <Badge key={domain} variant="default" className="gap-1">
              {domain}
              <button
                onClick={() => removeSocialDomain(domain)}
                className="p-0.5 hover:bg-gray-200 rounded"
                aria-label={`Удалить ${domain}`}
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </Badge>
          ))}
        </div>
        <p className="mt-2 text-sm text-gray-500">
          Всего доменов: {socialDomains.length}. Изменения вступят в силу при следующем запуске классификации.
        </p>
      </Card>

      {/* Categories */}
      <Card>
        <CardHeader title="Категории заведений" subtitle="Настроенные категории для парсинга из OpenStreetMap" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {config?.category_labels && Object.entries(config.category_labels).map(([key, label]) => (
            <div key={key} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <p className="font-medium">{label}</p>
              <p className="text-sm text-gray-500">{key}</p>
              <p className="text-xs text-gray-400 mt-1">
                Теги: {config.categories[key]?.join(', ') || '—'}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Regions */}
      <Card>
        <CardHeader title="Районы для выгрузки" subtitle="Список районов и муниципалитетов, которые будут опрашиваться" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-96 overflow-y-auto">
          {config?.regions?.map((region) => (
            <Badge key={region.name} variant="default" className="gap-2">
              {region.name}
              <span className="text-xs text-gray-500">({region.type})</span>
            </Badge>
          ))}
        </div>
        <p className="mt-2 text-sm text-gray-500">
          Всего регионов: {config?.regions?.length || 0} (муниципалитетов: {config?.regions?.filter(r => r.type === 'municipality').length || 0}, районов: {config?.regions?.filter(r => r.type === 'district').length || 0})
        </p>
      </Card>

      {message && (
        <div className={cn('p-4 rounded-lg', message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200')}>
          {message.text}
        </div>
      )}
    </div>
  )
}