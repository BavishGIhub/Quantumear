'use client';

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileAudio, Loader2 } from 'lucide-react';

interface DropZoneProps {
    onFileAccepted: (file: File) => void;
    isProcessing: boolean;
    progress: number;
    statusMessage: string;
}

export default function DropZone({ onFileAccepted, isProcessing, progress, statusMessage }: DropZoneProps) {
    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            if (acceptedFiles.length > 0 && !isProcessing) {
                onFileAccepted(acceptedFiles[0]);
            }
        },
        [onFileAccepted, isProcessing]
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'audio/*': ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac', '.wma'],
        },
        maxFiles: 1,
        disabled: isProcessing,
        maxSize: 100 * 1024 * 1024, // 100MB
    });

    return (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            {/* Header */}
            <div
                style={{
                    padding: '16px 20px',
                    borderBottom: '1px solid var(--border-default)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                }}
            >
                <div
                    style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: isProcessing ? 'var(--blue-500)' : 'var(--green-400)',
                        boxShadow: isProcessing ? '0 0 8px var(--blue-500)' : '0 0 8px var(--green-400)',
                    }}
                />
                <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
                    Signal Analysis Port
                </span>
                <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 'auto' }}>
                    .wav .mp3 .flac .ogg .m4a .aac
                </span>
            </div>

            {/* Drop Zone Area */}
            <div style={{ padding: 24 }}>
                <div
                    {...getRootProps()}
                    className={`dropzone ${isDragActive ? 'active' : ''}`}
                    style={{
                        opacity: isProcessing ? 0.6 : 1,
                        cursor: isProcessing ? 'not-allowed' : 'pointer',
                    }}
                >
                    <input {...getInputProps()} />

                    <AnimatePresence mode="wait">
                        {isProcessing ? (
                            <motion.div
                                key="processing"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                style={{ position: 'relative', zIndex: 1 }}
                            >
                                {/* Quantum Processing Animation */}
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                                    style={{
                                        width: 56,
                                        height: 56,
                                        margin: '0 auto 16px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        borderRadius: '50%',
                                        border: '3px solid var(--border-default)',
                                        borderTopColor: 'var(--blue-500)',
                                    }}
                                >
                                    <Loader2 size={28} style={{ color: 'var(--blue-500)' }} />
                                </motion.div>

                                <p
                                    style={{
                                        color: 'var(--blue-500)',
                                        fontSize: 14,
                                        fontWeight: 600,
                                        marginBottom: 16,
                                        fontFamily: 'var(--font-mono)',
                                    }}
                                >
                                    {statusMessage || 'Processing...'}
                                </p>

                                {/* Progress Bar */}
                                <div style={{ maxWidth: 320, margin: '0 auto' }}>
                                    <div className="progress-track">
                                        <motion.div
                                            className="progress-fill"
                                            initial={{ width: '0%' }}
                                            animate={{ width: `${Math.round(progress * 100)}%` }}
                                        />
                                    </div>
                                    <p
                                        style={{
                                            fontSize: 12,
                                            color: 'var(--text-muted)',
                                            marginTop: 8,
                                            textAlign: 'right',
                                            fontFamily: 'var(--font-mono)',
                                        }}
                                    >
                                        {Math.round(progress * 100)}%
                                    </p>
                                </div>
                            </motion.div>
                        ) : isDragActive ? (
                            <motion.div
                                key="drag"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0 }}
                                style={{ position: 'relative', zIndex: 1 }}
                            >
                                <motion.div
                                    animate={{ y: [0, -6, 0] }}
                                    transition={{ duration: 1.2, repeat: Infinity }}
                                    style={{
                                        width: 64,
                                        height: 64,
                                        margin: '0 auto 16px',
                                        borderRadius: 'var(--radius)',
                                        background: 'var(--blue-600)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <Upload size={32} style={{ color: 'white' }} />
                                </motion.div>
                                <p style={{ fontSize: 18, fontWeight: 600, color: 'var(--blue-500)' }}>
                                    Release to Scan
                                </p>
                                <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8 }}>
                                    Quantum analysis will begin immediately
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="idle"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0, y: -10 }}
                                style={{ position: 'relative', zIndex: 1 }}
                            >
                                {/* Upload Icon */}
                                <div
                                    style={{
                                        width: 64,
                                        height: 64,
                                        margin: '0 auto 16px',
                                        borderRadius: 'var(--radius)',
                                        background: 'var(--bg-elevated)',
                                        border: '1px solid var(--border-default)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <FileAudio size={28} style={{ color: 'var(--blue-500)' }} />
                                </div>

                                <p style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
                                    Drop audio file here, or{' '}
                                    <span style={{ color: 'var(--blue-500)', textDecoration: 'underline' }}>browse</span>
                                </p>
                                <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 360, margin: '0 auto', lineHeight: 1.6 }}>
                                    Inject audio stream for quantum-grade synthesis anomaly detection
                                </p>

                                {/* Feature Tags */}
                                <div
                                    style={{
                                        display: 'flex',
                                        gap: 8,
                                        justifyContent: 'center',
                                        marginTop: 20,
                                        flexWrap: 'wrap',
                                    }}
                                >
                                    {['ResNet-18', 'ZZFeatureMap', 'Quantum Sim', 'Entropy Analysis'].map((tag) => (
                                        <span
                                            key={tag}
                                            style={{
                                                fontSize: 10,
                                                padding: '4px 10px',
                                                borderRadius: '9999px',
                                                background: 'var(--bg-elevated)',
                                                border: '1px solid var(--border-default)',
                                                color: 'var(--text-muted)',
                                                fontFamily: 'var(--font-mono)',
                                                letterSpacing: '0.02em',
                                            }}
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
