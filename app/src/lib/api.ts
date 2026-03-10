/* ═══════════════════════════════════════════════════════════
   QuantumEAR — API Client
   ═══════════════════════════════════════════════════════════ */

import { ScanResult, ScanStatus, HistoryResponse, HealthCheck } from '@/types';

// API base URL — configurable via environment variable
// For Android Emulators, localhost must be accessed via 10.0.2.2
const getBaseUrl = () => {
    if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;

    // Detection for Capacitor / Android environment
    if (typeof window !== 'undefined' && (window as any).Capacitor) {
        return 'http://10.0.2.2:8000'; // Default host for Android Emulator
    }

    return 'http://localhost:8000';
};

const API_BASE = getBaseUrl();

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    /**
     * Health check
     */
    async healthCheck(): Promise<HealthCheck> {
        const res = await fetch(`${this.baseUrl}/api/health`);
        if (!res.ok) throw new Error('API is not healthy');
        return res.json();
    }

    /**
     * Analyze audio file (synchronous — waits for result)
     */
    async analyzeAudio(file: File, onProgress?: (progress: number) => void): Promise<ScanResult> {
        const formData = new FormData();
        formData.append('file', file);

        // Use XMLHttpRequest for upload progress
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable && onProgress) {
                    const uploadProgress = (event.loaded / event.total) * 0.3; // Upload is 30%
                    onProgress(uploadProgress);
                }
            };

            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const result = JSON.parse(xhr.responseText);
                        onProgress?.(1.0);
                        resolve(result);
                    } catch {
                        reject(new Error('Failed to parse response'));
                    }
                } else {
                    try {
                        const error = JSON.parse(xhr.responseText);
                        reject(new Error(error.detail || 'Analysis failed'));
                    } catch {
                        reject(new Error(`Analysis failed with status ${xhr.status}`));
                    }
                }
            };

            xhr.onerror = () => reject(new Error('Network error'));
            xhr.ontimeout = () => reject(new Error('Request timed out'));

            xhr.open('POST', `${this.baseUrl}/api/analyze`);
            xhr.timeout = 300000; // 5 min timeout for quantum simulation
            xhr.send(formData);

            // Simulate processing progress after upload completes
            let processingInterval: NodeJS.Timeout | null = null;
            xhr.upload.onloadend = () => {
                let progress = 0.3;
                processingInterval = setInterval(() => {
                    progress = Math.min(progress + 0.05, 0.95);
                    onProgress?.(progress);
                }, 500);
            };

            const originalOnload = xhr.onload;
            xhr.onload = function (this: XMLHttpRequest, ev: ProgressEvent) {
                if (processingInterval) clearInterval(processingInterval);
                originalOnload?.call(this, ev);
            };
        });
    }

    /**
     * Start async audio analysis
     */
    async analyzeAudioAsync(file: File): Promise<{ scan_id: string }> {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${this.baseUrl}/api/analyze/async`, {
            method: 'POST',
            body: formData,
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Failed to start analysis');
        }

        return res.json();
    }

    /**
     * Poll scan status
     */
    async getScanStatus(scanId: string): Promise<ScanStatus> {
        const res = await fetch(`${this.baseUrl}/api/scan/${scanId}/status`);
        if (!res.ok) throw new Error('Failed to get scan status');
        return res.json();
    }

    /**
     * Get scan result
     */
    async getScanResult(scanId: string): Promise<ScanResult> {
        const res = await fetch(`${this.baseUrl}/api/scan/${scanId}`);
        if (!res.ok) throw new Error('Failed to get scan result');
        return res.json();
    }

    /**
     * Get scan history
     */
    async getHistory(limit: number = 50, offset: number = 0): Promise<HistoryResponse> {
        const res = await fetch(
            `${this.baseUrl}/api/history?limit=${limit}&offset=${offset}`
        );
        if (!res.ok) throw new Error('Failed to get history');
        return res.json();
    }

    /**
     * Delete a scan
     */
    async deleteScan(scanId: string): Promise<void> {
        const res = await fetch(`${this.baseUrl}/api/history/${scanId}`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('Failed to delete scan');
    }

    /**
     * Clear all history
     */
    async clearHistory(): Promise<void> {
        const res = await fetch(`${this.baseUrl}/api/history`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('Failed to clear history');
    }
}

// Singleton API client
export const api = new ApiClient(API_BASE);
export default api;
