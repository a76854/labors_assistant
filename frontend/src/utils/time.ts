const BEIJING_TIME_ZONE = 'Asia/Shanghai';
const HAS_TIMEZONE_SUFFIX = /(Z|[+-]\d{2}:\d{2})$/;

function parseApiDateTime(value?: string): Date | null {
  if (!value) return null;

  const normalized = value.trim();
  if (!normalized) return null;

  if (HAS_TIMEZONE_SUFFIX.test(normalized)) {
    const parsed = new Date(normalized);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  const match = normalized.match(
    /^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?$/,
  );

  if (!match) {
    const fallback = new Date(normalized);
    return Number.isNaN(fallback.getTime()) ? null : fallback;
  }

  const [, year, month, day, hour, minute, second = '0', microseconds = '0'] = match;
  const millisecond = Number((microseconds + '000').slice(0, 3));
  const utcMillis = Date.UTC(
    Number(year),
    Number(month) - 1,
    Number(day),
    Number(hour) - 8,
    Number(minute),
    Number(second),
    millisecond,
  );

  return new Date(utcMillis);
}

function formatWithBeijing(
  value: string | undefined,
  options: Intl.DateTimeFormatOptions,
): string {
  const date = parseApiDateTime(value);
  if (!date) return '时间未知';

  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: BEIJING_TIME_ZONE,
    ...options,
  }).format(date);
}

export function formatBeijingTime(value?: string): string {
  return formatWithBeijing(value, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

export function formatBeijingDateTime(value?: string): string {
  return formatWithBeijing(value, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function formatBeijingSessionTime(value?: string): string {
  const date = parseApiDateTime(value);
  if (!date) return '时间未知';

  const beijingDayKey = new Intl.DateTimeFormat('zh-CN', {
    timeZone: BEIJING_TIME_ZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
  const currentDayKey = new Intl.DateTimeFormat('zh-CN', {
    timeZone: BEIJING_TIME_ZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());

  if (beijingDayKey === currentDayKey) {
    return formatBeijingTime(value);
  }

  return formatWithBeijing(value, {
    month: 'numeric',
    day: 'numeric',
  });
}
