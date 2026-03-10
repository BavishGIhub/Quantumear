'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { getTrustColor, getTrustGlow } from '@/types';
import { Shield, AlertTriangle } from 'lucide-react';

interface TrustMeterProps {
    score: number;
    label: 'organic' | 'synthetic';
    isAnimating?: boolean;
}

export default function TrustMeter({ score, label, isAnimating = true }: TrustMeterProps) {
    const color = getTrustColor(score);
    const glow = getTrustGlow(score);
    const radius = 70; // Smaller radius for better fit
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;

    return (
        <div className="card" style={{ padding: 20, textAlign: 'center' }}>
            {/* Header */}
            <div
                style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    marginBottom: 16,
                }}
            >
                Quantum Integrity Index
            </div>

            {/* Meter Container - Fixed Size */}
            <div 
                style={{ 
                    position: 'relative', 
                    width: 160, 
                    height: 160, 
                    margin: '0 auto',
                }}
            >
                {/* Ambient glow */}
                <div
                    style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: 120,
                        height: 120,
                        borderRadius: '50%',
                        background: `radial-gradient(circle, ${color}15 0%, transparent 70%)`,
                        filter: 'blur(12px)',
                    }}
                />

                <svg
                    width="160"
                    height="160"
                    viewBox="0 0 160 160"
                    style={{ transform: 'rotate(-90deg)' }}
                >
                    {/* Background ring */}
                    <circle
                        cx="80"
                        cy="80"
                        r={radius}
                        fill="none"
                        stroke="var(--bg-elevated)"
                        strokeWidth="8"
                    />
                    {/* Animated fill ring */}
                    <motion.circle
                        cx="80"
                        cy="80"
                        r={radius}
                        fill="none"
                        stroke={color}
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset: isAnimating ? offset : circumference }}
                        transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
                        style={{ filter: `drop-shadow(0 0 4px ${color})` }}
                    />
                </svg>

                {/* Center text - Positioned absolutely within container */}
                <div
                    style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        textAlign: 'center',
                    }}
                >
                    <motion.div
                        style={{ 
                            color, 
                            fontSize: 32, 
                            fontWeight: 700,
                            fontFamily: 'var(--font-mono)',
                            lineHeight: 1,
                        }}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.5, delay: 0.5 }}
                    >
                        {isAnimating ? (
                            <Counter from={0} to={Math.round(score)} duration={1.5} />
                        ) : (
                            '--'
                        )}
                        <span style={{ fontSize: 14, fontWeight: 500 }}>%</span>
                    </motion.div>
                    <motion.div
                        style={{
                            fontSize: 10,
                            fontWeight: 500,
                            textTransform: 'uppercase',
                            letterSpacing: '0.1em',
                            color: 'var(--text-muted)',
                            marginTop: 4,
                        }}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1 }}
                    >
                        Trust Score
                    </motion.div>
                </div>
            </div>

            {/* Label Badge */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 }}
                style={{ marginTop: 16 }}
            >
                <span
                    className={`badge ${label === 'organic' ? 'badge-organic' : 'badge-synthetic'}`}
                    style={{ fontSize: 12, padding: '6px 14px', gap: 6 }}
                >
                    {label === 'organic' ? (
                        <Shield size={14} style={{ color: 'var(--green-400)' }} />
                    ) : (
                        <AlertTriangle size={14} style={{ color: 'var(--red-400)' }} />
                    )}
                    {label === 'organic' ? 'Organic Voice' : 'Synthetic Detected'}
                </span>
            </motion.div>

            {/* Confidence info */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5 }}
                style={{
                    marginTop: 12,
                    fontSize: 10,
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                }}
            >
                Confidence: {score >= 50 ? score.toFixed(1) : (100 - score).toFixed(1)}%
            </motion.div>
        </div>
    );
}

/**
 * Animated counter component
 */
function Counter({ from, to, duration }: { from: number; to: number; duration: number }) {
    const [count, setCount] = React.useState(from);

    React.useEffect(() => {
        const startTime = performance.now();
        const animate = (currentTime: number) => {
            const elapsed = (currentTime - startTime) / 1000;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            setCount(Math.round(from + (to - from) * eased));
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        requestAnimationFrame(animate);
    }, [from, to, duration]);

    return <>{count}</>;
}
