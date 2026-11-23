import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('ru-RU').format(num)
}

export function formatScore(score: number): string {
  return score.toFixed(1)
}

export function getPriorityBadgeClass(level: string): string {
  switch (level) {
    case 'high':
      return 'badge-high'
    case 'medium':
      return 'badge-medium'
    case 'low':
      return 'badge-low'
    default:
      return 'badge-low'
  }
}

export function getGroupBadgeClass(group: string): string {
  switch (group) {
    case 'A':
      return 'badge-group-a'
    case 'B':
      return 'badge-group-b'
    default:
      return 'badge'
  }
}

export function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    cafe: 'Кафе',
    restaurant: 'Рестораны',
    bar: 'Бары',
    bakery: 'Пекарни',
    pastry: 'Кондитерские',
    beauty: 'Салоны красоты',
    barber: 'Барбершопы',
    car_repair: 'Автосервисы',
  }
  return labels[category] || category
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength - 3) + '...'
}

export function openInNewTab(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}