'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ScanResult, formatDuration, formatDate } from '@/types';
import { ClipboardList, FileAudio, Trash2, Shield, AlertTriangle } from 'lucide-react';

interface ScanHistoryProps {
    results: ScanResult[];
    onDelete?: (id: string) => void;
    onClear?: () => void;
}

export default function ScanHistory({ results, onDelete, onClear }: ScanHistoryProps) {
    if (results.length === 0) {
        return (
            <div className="card" style={{ padding: 40, textAlign: 'center' }}>
                <ClipboardList size={48} style={{ marginBottom: 16, color: 'var(--text-muted)', opacity: 0.5 }} />
                <p style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
                    No scans yet
                </p>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    Upload an audio file to start scanning for deepfakes
                </p>
            </div>
        );
    }

    return (
        <div className="card" style={{ overflow: 'hidden' }}>
            {/* Header */}
            <div
                style={{
                    padding: '16px 20px',
                    borderBottom: '1px solid var(--border-default)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
                        Recent Analysis
                    </span>
                    <span
                        style={{
                            fontSize: 11,
                            padding: '2px 8px',
                            borderRadius: '9999px',
                            background: 'var(--bg-elevated)',
                            color: 'var(--blue-500)',
                            border: '1px solid var(--border-default)',
                            fontFamily: 'var(--font-mono)',
                        }}
                    >
                        {results.length}
                    </span>
                </div>
                {onClear && results.length > 0 && (
                    <button className="btn-danger" onClick={onClear} style={{ padding: '6px 12px', fontSize: 12 }}>
                        <Trash2 size={14} style={{ display: 'inline', marginRight: 4 }} />
                        Clear
                    </button>
                )}
            </div>

            {/* Table */}
            <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Score</th>
                            <th>Result</th>
                            <th>Entropy Regions</th>
                            <th>Duration</th>
                            <th>Date</th>
                            {onDelete && <th>Actions</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {results.map((scan, index) => (
                            <motion.tr
                                key={scan.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                            >
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <FileAudio size={16} style={{ color: 'var(--blue-500)' }} />
                                        <span
                                            style={{
                                                fontWeight: 500,
                                                color: 'var(--text-primary)',
                                                maxWidth: 160,
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap',
                                            }}
                                        >
                                            {scan.filename}
                                        </span>
                                    </div>
                                </td>
                                <td>
                                    <span
                                        className="font-mono"
                                        style={{
                                            fontWeight: 700,
                                            color:
                                                scan.trust_score >= 70
                                                    ? 'var(--green-400)'
                                                    : scan.trust_score >= 40
                                                        ? 'var(--yellow-400)'
                                                        : 'var(--red-400)',
                                        }}
                                    >
                                        {scan.trust_score}%
                                    </span>
                                </td>
                                <td>
                                    <span
                                        className="badge"
                                        style={{
                                            background: scan.label === 'organic' ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                                            color: scan.label === 'organic' ? 'var(--green-400)' : 'var(--red-400)',
                                            border: `1px solid ${scan.label === 'organic' ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                                            gap: 4,
                                        }}
                                    >
                                        {scan.label === 'organic' ? (
                                            <Shield size={12} />
                                        ) : (
                                            <AlertTriangle size={12} />
                                        )}
                                        {scan.label}
                                    </span>
                                </td>
                                <td>
                                    <span className="font-mono" style={{ fontSize: 12 }}>
                                        {scan.entropy_regions.length > 0 ? (
                                            <span style={{ color: 'var(--red-400)' }}>
                                                {scan.entropy_regions.length} detected
                                            </span>
                                        ) : (
                                            <span style={{ color: 'var(--green-400)' }}>None</span>
                                        )}
                                    </span>
                                </td>
                                <td>
                                    <span className="font-mono" style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                                        {formatDuration(scan.processing_time_ms)}
                                    </span>
                                </td>
                                <td>
                                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                                        {formatDate(scan.timestamp)}
                                    </span>
                                </td>
                                {onDelete && (
                                    <td>
                                        <button
                                            onClick={() => onDelete(scan.id)}
                                            style={{
                                                background: 'transparent',
                                                border: 'none',
                                                color: 'var(--text-muted)',
                                                cursor: 'pointer',
                                                padding: 4,
                                                borderRadius: 4,
                                                transition: 'color 0.2s',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                            }}
                                            onMouseOver={(e) => (e.currentTarget.style.color = 'var(--red-400)')}
                                            onMouseOut={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </td>
                                )}
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
