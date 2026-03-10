export type AppSettings = {
  incognitoAnalysis: boolean;
  highFidelityAnalysis: boolean;
  activeNoiseFilter: boolean;
};

const STORAGE_KEY = 'quantumear.settings.v1';

export function getDefaultSettings(): AppSettings {
  return {
    incognitoAnalysis: false,
    highFidelityAnalysis: false,
    activeNoiseFilter: true,
  };
}

export function loadSettings(): AppSettings {
  if (typeof window === 'undefined') return getDefaultSettings();
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return getDefaultSettings();
    const parsed = JSON.parse(raw) as Partial<AppSettings>;
    return {
      ...getDefaultSettings(),
      ...parsed,
    };
  } catch {
    return getDefaultSettings();
  }
}

export function saveSettings(next: AppSettings): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // ignore
  }
}
