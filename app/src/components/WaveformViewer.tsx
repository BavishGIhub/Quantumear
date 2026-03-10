'use client';

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface WaveformViewerProps {
    waveformData: number[] | null;
    entropyRegions: [number, number][];
    duration: number;
}

export default function WaveformViewer({ waveformData, entropyRegions, duration }: WaveformViewerProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!waveformData || !canvasRef.current || !containerRef.current) return;

        const canvas = canvasRef.current;
        const container = containerRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // High DPI support
        const dpr = window.devicePixelRatio || 1;
        const width = container.clientWidth;
        const height = 160;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.scale(dpr, dpr);

        // Clear
        ctx.clearRect(0, 0, width, height);

        const centerY = height / 2;
        const barWidth = width / waveformData.length;

        // Draw entropy regions (red highlights)
        if (entropyRegions.length > 0 && duration > 0) {
            entropyRegions.forEach(([start, end]) => {
                const x1 = (start / duration) * width;
                const x2 = (end / duration) * width;

                // Red gradient for entropy region
                const gradient = ctx.createLinearGradient(0, 0, 0, height);
                gradient.addColorStop(0, 'rgba(239, 68, 68, 0.15)');
                gradient.addColorStop(0.5, 'rgba(239, 68, 68, 0.08)');
                gradient.addColorStop(1, 'rgba(239, 68, 68, 0.15)');

                ctx.fillStyle = gradient;
                ctx.fillRect(x1, 0, x2 - x1, height);

                // Top border line
                ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(x1, 0);
                ctx.lineTo(x2, 0);
                ctx.stroke();

                // Label
                ctx.fillStyle = 'rgba(239, 68, 68, 0.7)';
                ctx.font = '9px "JetBrains Mono", monospace';
                ctx.fillText('HIGH ENTROPY', x1 + 4, 14);
            });
        }

        // Draw center line
        ctx.strokeStyle = 'rgba(6, 182, 212, 0.15)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(width, centerY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw waveform bars
        waveformData.forEach((amplitude, i) => {
            const x = i * barWidth;
            const barH = Math.abs(amplitude) * centerY * 0.85;

            // Check if this position is in an entropy region
            const time = (i / waveformData.length) * duration;
            const inEntropyRegion = entropyRegions.some(
                ([start, end]) => time >= start && time <= end
            );

            if (inEntropyRegion) {
                // Red for entropy regions
                const gradient = ctx.createLinearGradient(0, centerY - barH, 0, centerY + barH);
                gradient.addColorStop(0, 'rgba(239, 68, 68, 0.8)');
                gradient.addColorStop(0.5, 'rgba(239, 68, 68, 0.4)');
                gradient.addColorStop(1, 'rgba(239, 68, 68, 0.8)');
                ctx.fillStyle = gradient;
            } else {
                // Cyan gradient for normal regions
                const gradient = ctx.createLinearGradient(0, centerY - barH, 0, centerY + barH);
                gradient.addColorStop(0, 'rgba(6, 182, 212, 0.7)');
                gradient.addColorStop(0.5, 'rgba(6, 182, 212, 0.3)');
                gradient.addColorStop(1, 'rgba(6, 182, 212, 0.7)');
                ctx.fillStyle = gradient;
            }

            // Draw symmetric bar
            const w = Math.max(barWidth - 1, 1);
            ctx.fillRect(x, centerY - barH, w, barH * 2);
        });

        // Draw glow effect on top
        const glowGradient = ctx.createLinearGradient(0, 0, 0, height);
        glowGradient.addColorStop(0, 'rgba(6, 182, 212, 0.05)');
        glowGradient.addColorStop(0.5, 'transparent');
        glowGradient.addColorStop(1, 'rgba(6, 182, 212, 0.05)');
        ctx.fillStyle = glowGradient;
        ctx.fillRect(0, 0, width, height);

    }, [waveformData, entropyRegions, duration]);

    if (!waveformData) {
        return (
            <div className="glass-card-static" style={{ padding: 24 }}>
                <div
                    style={{
                        fontSize: 12,
                        fontWeight: 600,
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.15em',
                        marginBottom: 16,
                    }}
                >
                    Waveform Analysis
                </div>
                <div
                    className="waveform-container"
                    style={{
                        height: 160,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                        Upload an audio file to view waveform
                    </p>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            className="glass-card-static"
            style={{ padding: 24 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
        >
            {/* Header */}
            <div
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 16,
                }}
            >
                <div
                    style={{
                        fontSize: 12,
                        fontWeight: 600,
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.15em',
                    }}
                >
                    Waveform Analysis
                </div>
                {entropyRegions.length > 0 && (
                    <span className="badge badge-synthetic" style={{ fontSize: 10 }}>
                        {entropyRegions.length} High Entropy Region{entropyRegions.length > 1 ? 's' : ''}
                    </span>
                )}
            </div>

            {/* Canvas */}
            <div ref={containerRef} className="waveform-container scan-line-effect">
                <canvas ref={canvasRef} style={{ display: 'block', width: '100%' }} />
            </div>

            {/* Legend */}
            <div
                style={{
                    display: 'flex',
                    gap: 20,
                    marginTop: 12,
                    fontSize: 11,
                    color: 'var(--text-muted)',
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div
                        style={{
                            width: 12,
                            height: 4,
                            background: 'var(--blue-500)',
                            borderRadius: 2,
                        }}
                    />
                    Normal Signal
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div
                        style={{
                            width: 12,
                            height: 4,
                            background: 'var(--red-400)',
                            borderRadius: 2,
                        }}
                    />
                    High Entropy (Potential Artifact)
                </div>
            </div>
        </motion.div>
    );
}
