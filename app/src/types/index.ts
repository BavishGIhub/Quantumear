/* ═══════════════════════════════════════════════════════════
   QuantumEAR — TypeScript Type Definitions
   ═══════════════════════════════════════════════════════════ */

export interface ScanResult {
    id: string;
    filename: string;
    trust_score: number;
    label: 'organic' | 'synthetic';
    synthetic_probability: number;
    entropy_regions: [number, number][];
    entropy_timeline: EntropyTimeline | null;
    waveform_data: number[] | null;
    spectrogram_base64: string | null;
    processing_time_ms: number;
    quantum_features: number[];
    timestamp: string;
    status: 'complete' | 'processing' | 'error';
    reasoning?: string;
}

export interface EntropyTimeline {
    times: number[];
    values: number[];
    threshold: number;
    total_duration: number;
}

export interface ScanStatus {
    status: 'processing' | 'complete' | 'error';
    progress: number;
    message: string;
}

export interface HistoryResponse {
    total: number;
    limit: number;
    offset: number;
    results: ScanResult[];
}

export interface HealthCheck {
    status: string;
    service: string;
    version: string;
    timestamp: string;
    models_loaded: boolean;
}

export type TrustLevel = 'safe' | 'warning' | 'danger';

export function getTrustLevel(score: number): TrustLevel {
    if (score >= 70) return 'safe';
    if (score >= 40) return 'warning';
    return 'danger';
}

// FIXED: Proper detection logic
// High trust score (>=70) = Organic/Safe
// Low trust score (<40) = Synthetic/Danger
// Mid range (40-70) = Warning/Uncertain
export function getTrustColor(score: number): string {
    if (score >= 70) return '#22c55e'; // Green = Organic/High trust
    if (score >= 40) return '#f59e0b'; // Yellow = Warning
    return '#ef4444'; // Red = Synthetic/Low trust
}

export function getTrustGlow(score: number): string {
    if (score >= 70) return '0 0 30px rgba(34, 197, 94, 0.4)';
    if (score >= 40) return '0 0 30px rgba(245, 158, 11, 0.4)';
    return '0 0 30px rgba(239, 68, 68, 0.4)';
}

// Get label based on trust score
export function getLabelFromScore(score: number): 'organic' | 'synthetic' {
    return score >= 50 ? 'organic' : 'synthetic';
}

export function formatDuration(ms: number): string {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
}

export function formatDate(isoString: string): string {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}
