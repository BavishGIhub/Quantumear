import { ScanResult } from '@/types';

const STORAGE_KEY = 'quantumear.history.v1';

export function loadLocalHistory(): ScanResult[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as ScanResult[];
  } catch {
    return [];
  }
}

export function saveLocalHistory(next: ScanResult[]): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next.slice(0, 200)));
  } catch {
    // ignore
  }
}

export function upsertLocalHistoryItem(item: ScanResult): ScanResult[] {
  const current = loadLocalHistory();
  const filtered = current.filter((h) => h.id !== item.id);
  const next = [item, ...filtered];
  saveLocalHistory(next);
  return next;
}

export function removeLocalHistoryItem(id: string): ScanResult[] {
  const current = loadLocalHistory();
  const next = current.filter((h) => h.id !== id);
  saveLocalHistory(next);
  return next;
}

export function clearLocalHistory(): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
