'use client';

import React, { useMemo, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Mic, Paperclip, Voicemail, AudioWaveform, Play, Share2, Trash2 } from 'lucide-react';
import { ScanResult } from '@/types';
import api from '@/lib/api';
import { loadLocalHistory, removeLocalHistoryItem, clearLocalHistory, saveLocalHistory } from '@/lib/historyStore';
import ThemeToggle from '@/components/ThemeToggle';

export default function HistoryPage() {
    const [history, setHistory] = useState<ScanResult[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [query, setQuery] = useState('');
    const [filter, setFilter] = useState<'all' | 'week' | 'month' | 'deepfakes'>('all');

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        setLoading(true);
        try {
            const data = await api.getHistory();
            setHistory(data.results);
            saveLocalHistory(data.results);
        } catch {
            setError('Could not connect to backend — showing local data');
            setHistory(loadLocalHistory());
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await api.deleteScan(id);
        } catch { /* ignore */ }
        setHistory(() => removeLocalHistoryItem(id));
    };

    const handleClear = async () => {
        try {
            await api.clearHistory();
        } catch { /* ignore */ }
        clearLocalHistory();
        setHistory([]);
    };

    const filtered = useMemo(() => {
        const now = Date.now();

        const withinDays = (iso: string, days: number) => {
            const ts = new Date(iso).getTime();
            return Number.isFinite(ts) ? now - ts <= days * 24 * 60 * 60 * 1000 : false;
        };

        return history
            .filter((h) => {
                if (!query.trim()) return true;
                return h.filename.toLowerCase().includes(query.trim().toLowerCase());
            })
            .filter((h) => {
                if (filter === 'all') return true;
                if (filter === 'deepfakes') return h.label === 'synthetic' || h.trust_score < 40;
                if (filter === 'week') return withinDays(h.timestamp, 7);
                if (filter === 'month') return withinDays(h.timestamp, 30);
                return true;
            });
    }, [history, query, filter]);

    const FILTERS = [
        { key: 'all', label: 'All Time' },
        { key: 'week', label: 'This Week' },
        { key: 'month', label: 'Last Month' },
        { key: 'deepfakes', label: 'Deepfakes Only' },
    ] as const;

    return (
        <div style={{ position: 'relative', minHeight: '100vh' }}>
            <BackgroundBlobs />

            {/* ── Sticky glassmorphic header ── */}
            <header style={{
                position: 'sticky',
                top: 0,
                zIndex: 20,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '14px 0 12px',
            }}>
                <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                    Scan <span style={{ color: '#FB3595' }}>History</span>
                </h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <button
                        type="button"
                        onClick={handleClear}
                        style={{
                            padding: '7px 14px',
                            borderRadius: 999,
                            border: '1px solid var(--border-default)',
                            background: 'transparent',
                            cursor: 'pointer',
                            fontSize: 12,
                            fontWeight: 700,
                            color: 'var(--text-secondary)',
                        }}
                    >
                        Clear
                    </button>
                    <ThemeToggle />
                </div>
            </header>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} style={{ paddingTop: 8 }}>

                {error && (
                    <div style={{
                        marginBottom: 12,
                        padding: '10px 14px',
                        borderRadius: 14,
                        background: 'rgba(255,255,255,0.07)',
                        border: '1px solid rgba(255,255,255,0.10)',
                        fontSize: 12,
                        color: 'var(--text-secondary)',
                    }}>
                        {error}
                    </div>
                )}

                {/* ── Search bar ── */}
                <div style={{ position: 'relative', marginBottom: 14 }}>
                    <span style={{
                        position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)',
                        color: 'var(--text-muted)', fontSize: 16, pointerEvents: 'none',
                    }}>🔍</span>
                    <input
                        type="text"
                        placeholder="Search audio scans..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '13px 16px 13px 42px',
                            borderRadius: 16,
                            border: 'none',
                            background: 'var(--bg-surface)',
                            color: 'var(--text-primary)',
                            fontSize: 14,
                            outline: 'none',
                            boxSizing: 'border-box',
                        }}
                    />
                </div>

                {/* ── Filter pills ── */}
                <div style={{ display: 'flex', gap: 10, marginBottom: 18, overflowX: 'auto', paddingBottom: 4 }}>
                    {FILTERS.map(({ key, label }) => (
                        <button
                            key={key}
                            type="button"
                            onClick={() => setFilter(key)}
                            style={{
                                padding: '8px 18px',
                                borderRadius: 999,
                                border: 'none',
                                background: filter === key
                                    ? 'linear-gradient(to right, #FB3595, #4589F5)'
                                    : 'rgba(255,255,255,0.08)',
                                color: filter === key ? '#fff' : 'var(--text-secondary)',
                                fontSize: 13,
                                fontWeight: 600,
                                cursor: 'pointer',
                                whiteSpace: 'nowrap',
                                boxShadow: filter === key ? '0 4px 14px rgba(251,53,149,0.25)' : 'none',
                                transition: 'all 0.2s',
                            }}
                        >
                            {label}
                        </button>
                    ))}
                </div>

                {/* ── Cards ── */}
                {loading ? (
                    <div style={{
                        padding: 20, borderRadius: 20,
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid var(--border-default)',
                    }}>
                        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading history…</div>
                    </div>
                ) : filtered.length === 0 ? (
                    <div style={{
                        padding: 32, borderRadius: 20, textAlign: 'center',
                        background: 'rgba(255,255,255,0.04)',
                        border: '1px solid var(--border-default)',
                    }}>
                        <div style={{ fontSize: 32, marginBottom: 8 }}>🎙</div>
                        <div style={{ fontSize: 14, color: 'var(--text-muted)' }}>No scans found</div>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                        {filtered.map((scan) => (
                            <HistoryCard key={scan.id} scan={scan} onDelete={() => handleDelete(scan.id)} />
                        ))}
                    </div>
                )}
            </motion.div>
        </div>
    );
}

function HistoryCard({ scan, onDelete }: { scan: ScanResult; onDelete: () => void }) {
    const isOrganic = scan.label === 'organic';
    const isDeepfake = !isOrganic && scan.trust_score < 40;
    const isSuspicious = !isOrganic && !isDeepfake;

    const labelText = isOrganic ? 'Authentic Audio' : isDeepfake ? 'Deepfake Detected' : 'Suspicious';
    const badgeColor = isOrganic ? '#16a34a' : isDeepfake ? '#ef4444' : '#fb923c';
    const badgeBg = isOrganic ? 'rgba(22,163,74,0.12)' : isDeepfake ? 'rgba(239,68,68,0.12)' : 'rgba(251,146,60,0.12)';

    // Progress bar = how synthetic (higher = more suspicious)
    const riskPercent = Math.max(0, Math.min(100, 100 - scan.trust_score));
    const progressGradient = isOrganic
        ? '#16a34a'
        : isDeepfake
            ? 'linear-gradient(to right, #ef4444, #FB3595)'
            : 'linear-gradient(to right, #fb923c, #ef4444)';

    // Pick icon color based on result
    const iconColor = isOrganic ? '#4589F5' : isDeepfake ? '#FB3595' : '#fb923c';

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
                background: 'rgba(255,255,255,0.07)',
                border: '1px solid rgba(255,255,255,0.10)',
                borderRadius: 20,
                padding: 16,
            }}
        >
            {/* Top row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0, flex: 1, overflow: 'hidden' }}>
                    {/* Icon */}
                    <div style={{
                        width: 46, height: 46, borderRadius: 14, flexShrink: 0,
                        background: 'var(--bg-surface)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: iconColor,
                    }}>
                        <AudioWaveform size={22} />
                    </div>
                    {/* File info */}
                    <div style={{ minWidth: 0, flex: 1, overflow: 'hidden' }}>
                        <div style={{
                            fontSize: 14, fontWeight: 700, color: 'var(--text-primary)',
                            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                        }}>
                            {scan.filename}
                        </div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>
                            {new Date(scan.timestamp).toLocaleString()}
                        </div>
                    </div>
                </div>

                {/* Badge */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0 }}>
                    <span style={{
                        fontSize: 11, fontWeight: 700,
                        color: badgeColor,
                        background: badgeBg,
                        padding: '5px 9px',
                        borderRadius: 8,
                    }}>
                        {labelText}
                    </span>
                    <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                        Confidence: {Math.round(scan.trust_score)}%
                    </span>
                </div>
            </div>

            {/* Progress bar */}
            <div style={{
                marginTop: 12, height: 5,
                background: 'rgba(255,255,255,0.08)',
                borderRadius: 999, overflow: 'hidden',
            }}>
                <div style={{
                    width: `${riskPercent}%`,
                    height: '100%',
                    background: progressGradient,
                    borderRadius: 999,
                    transition: 'width 0.6s ease',
                }} />
            </div>

            {/* Bottom row */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                marginTop: 12,
                paddingTop: 10,
                borderTop: '1px solid rgba(255,255,255,0.08)',
            }}>
                <div style={{ display: 'flex', gap: 14 }}>
                    <button type="button" style={{ border: 'none', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', padding: 0, display: 'flex' }}>
                        <Play size={18} />
                    </button>
                    <button type="button" style={{ border: 'none', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', padding: 0, display: 'flex' }}>
                        <Share2 size={17} />
                    </button>
                    <button type="button" onClick={onDelete} style={{ border: 'none', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', padding: 0, display: 'flex' }}>
                        <Trash2 size={17} />
                    </button>
                </div>
                <Link href={`/report?id=${encodeURIComponent(scan.id)}`} style={{
                    textDecoration: 'none', fontSize: 13, fontWeight: 700, color: '#4589F5',
                }}>
                    View Report →
                </Link>
            </div>
        </motion.div>
    );
}

function BackgroundBlobs() {
    return (
        <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
            <div style={{ position: 'absolute', top: '-10%', right: '-20%', width: 300, height: 300, background: '#4589F5', filter: 'blur(100px)', opacity: 0.20, borderRadius: 9999 }} />
            <div style={{ position: 'absolute', top: '20%', left: '-20%', width: 260, height: 260, background: '#FB3595', filter: 'blur(90px)', opacity: 0.18, borderRadius: 9999 }} />
            <div style={{ position: 'absolute', bottom: '10%', right: '10%', width: 200, height: 200, background: '#a855f7', filter: 'blur(80px)', opacity: 0.12, borderRadius: 9999 }} />
        </div>
    );
}
