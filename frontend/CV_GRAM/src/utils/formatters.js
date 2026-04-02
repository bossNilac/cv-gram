const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})

const shortDateFormatter = new Intl.DateTimeFormat(undefined, {
  year: 'numeric',
  month: 'short',
})

export function formatDateTime(value) {
  if (!value) {
    return 'Not available'
  }

  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : dateTimeFormatter.format(date)
}

export function formatCompactDate(value) {
  if (!value) {
    return 'Present'
  }

  const normalized = /^\d{4}$/.test(String(value)) ? `${value}-01-01` : `${value}`
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? String(value) : shortDateFormatter.format(date)
}

export function formatDateRange(start, end) {
  const startLabel = start ? formatCompactDate(start) : 'Unknown'
  const endLabel = end ? formatCompactDate(end) : 'Present'
  return `${startLabel} - ${endLabel}`
}
