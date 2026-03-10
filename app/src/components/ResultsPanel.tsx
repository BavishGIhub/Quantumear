'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ScanResult, formatDuration } from '@/types';
import { Zap, Dna, BarChart3, Atom, AlertTriangle } from 'lucide-react';

interface ResultsPanelProps {
    result: ScanResult;
}

export default function ResultsPanel({ result }: ResultsPanelProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
            style={{ padding: 20 }}
        >
            {/* Header */}
            <div
                style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.15em',
                    marginBottom: 16,
                }}
            >
                Analysis Report
            </div>

            {/* Stats Grid */}
            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: 10,
                }}
            >
                <StatCard
                    label="Processing Time"
                    value={formatDuration(result.processing_time_ms)}
                    icon={Zap}
                    delay={0.5}
                />
                <StatCard
                    label="Synthetic Prob"
                    value={`${(result.synthetic_probability * 100).toFixed(1)}%`}
                    icon={Dna}
                    color={result.synthetic_probability > 0.5 ? 'var(--red-400)' : 'var(--green-400)'}
                    delay={0.6}
                />
                <StatCard
                    label="Entropy Regions"
                    value={`${result.entropy_regions.length}`}
                    icon={BarChart3}
                    color={result.entropy_regions.length > 0 ? 'var(--yellow-400)' : 'var(--green-400)'}
                    delay={0.7}
                />
                <StatCard
                    label="Quantum Features"
                    value={`${result.quantum_features.length}`}
                    icon={Atom}
                    delay={0.8}
                />
            </div>

            {/* Quantum Features */}
            <div style={{ marginTop: 20 }}>
                <div
                    style={{
                        fontSize: 11,
                        fontWeight: 600,
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        marginBottom: 12,
                    }}
                >
                    Quantum Feature Vector
                </div>
                <div
                    style={{
                        display: 'flex',
                        gap: 8,
                        flexWrap: 'wrap',
                    }}
                >
                    {result.quantum_features.map((feat, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.9 + i * 0.1 }}
                            style={{
                                fontSize: 11,
                                padding: '6px 10px',
                                borderRadius: 'var(--radius-sm)',
                                background: feat > 0 ? 'rgba(23, 54, 207, 0.1)' : 'rgba(100, 116, 139, 0.1)',
                                border: `1px solid ${feat > 0 ? 'rgba(23, 54, 207, 0.2)' : 'rgba(100, 116, 139, 0.2)'}`,
                                color: feat > 0 ? 'var(--blue-500)' : 'var(--text-muted)',
                                fontFamily: 'var(--font-mono)',
                            }}
                        >
                            q{i}: {feat.toFixed(4)}
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Spectrogram */}
            {result.spectrogram_base64 && (
                <div style={{ marginTop: 20 }}>
                    <div
                        style={{
                            fontSize: 11,
                            fontWeight: 600,
                            color: 'var(--text-muted)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.1em',
                            marginBottom: 12,
                        }}
                    >
                        Mel-Spectrogram
                    </div>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1.2 }}
                        style={{
                            borderRadius: 'var(--radius-md)',
                            overflow: 'hidden',
                            border: '1px solid var(--border-default)',
                        }}
                    >
                        <img
                            src={`data:image/png;base64,${result.spectrogram_base64}`}
                            alt="Mel-Spectrogram"
                            style={{
                                width: '100%',
                                display: 'block',
                                imageRendering: 'crisp-edges',
                            }}
                        />
                    </motion.div>
                </div>
            )}

            {/* Entropy Regions Detail */}
            {result.entropy_regions.length > 0 && (
                <div style={{ marginTop: 20 }}>
                    <div
                        style={{
                            fontSize: 11,
                            fontWeight: 600,
                            color: 'var(--text-muted)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.1em',
                            marginBottom: 12,
                        }}
                    >
                        High Entropy Regions
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {result.entropy_regions.map(([start, end], i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 1.3 + i * 0.1 }}
                                className="font-mono"
                                style={{
                                    fontSize: 12,
                                    padding: '8px 12px',
                                    borderRadius: 'var(--radius-sm)',
                                    background: 'rgba(239, 68, 68, 0.08)',
                                    border: '1px solid rgba(239, 68, 68, 0.15)',
                                    color: 'var(--red-400)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 8,
                                }}
                            >
                                <AlertTriangle size={12} />
                                Region {i + 1}: {start.toFixed(2)}s — {end.toFixed(2)}s
                                <span style={{ marginLeft: 'auto', opacity: 0.6 }}>
                                    Δ{(end - start).toFixed(2)}s
                                </span>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}
        </motion.div>
    );
}

function StatCard({
    label,
    value,
    icon: Icon,
    color,
    delay = 0,
}: {
    label: string;
    value: string;
    icon: React.ComponentType<{ size?: number; style?: React.CSSProperties }>;
    color?: string;
    delay?: number;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            style={{
                padding: '12px 14px',
                borderRadius: 'var(--radius)',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-default)',
            }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                <Icon size={14} style={{ color: color || 'var(--text-muted)' }} />
                <span
                    style={{
                        fontSize: 10,
                        fontWeight: 600,
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.08em',
                    }}
                >
                    {label}
                </span>
            </div>
            <div
                style={{
                    fontSize: 16,
                    fontWeight: 700,
                    color: color || 'var(--text-primary)',
                    fontFamily: 'var(--font-mono)',
                }}
            >
                {value}
            </div>
        </motion.div>
    );
}
