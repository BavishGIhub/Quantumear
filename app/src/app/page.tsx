'use client';

import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Paperclip, Upload, Zap, ShieldCheck, AlertTriangle } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';
import { ScanResult } from '@/types';
import api from '@/lib/api';
import { Haptics, ImpactStyle } from '@capacitor/haptics';
import { loadSettings } from '@/lib/settings';
import { loadLocalHistory, upsertLocalHistoryItem } from '@/lib/historyStore';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [currentResult, setCurrentResult] = useState<ScanResult | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    setScanHistory(loadLocalHistory());
  }, []);

  const recent = useMemo(() => scanHistory.slice(0, 2), [scanHistory]);

  const handleFileAccepted = useCallback(async (file: File) => {
    setIsProcessing(true);
    setProgress(0);
    setStatusMessage('Uploading audio file...');
    setError(null);
    setCurrentResult(null);

    try {
      const result = await api.analyzeAudio(file, (p) => {
        setProgress(p);
        if (p < 0.3) setStatusMessage('Uploading audio file...');
        else if (p < 0.5) setStatusMessage('Generating Mel-Spectrogram...');
        else if (p < 0.7) setStatusMessage('Extracting features (ResNet-18)...');
        else if (p < 0.9) setStatusMessage('Quantum ensemble classification...');
        else setStatusMessage('Computing spectral entropy...');
      });

      setCurrentResult(result);

      const settings = loadSettings();
      if (!settings.incognitoAnalysis) {
        setScanHistory(() => upsertLocalHistoryItem(result));
      }

      // Mobile Haptics Feedback
      if (result.label === 'synthetic') {
        await Haptics.impact({ style: ImpactStyle.Heavy });
        setTimeout(() => Haptics.impact({ style: ImpactStyle.Heavy }), 200);
      } else {
        await Haptics.impact({ style: ImpactStyle.Light });
      }

      router.push(`/report?id=${encodeURIComponent(result.id)}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setError(message);
      // Demo mode: show mock result
      const mockResult = getMockResult(file.name);
      setCurrentResult(mockResult);

      const settings = loadSettings();
      if (!settings.incognitoAnalysis) {
        setScanHistory(() => upsertLocalHistoryItem(mockResult));
      }

      router.push(`/report?id=${encodeURIComponent(mockResult.id)}`);
    } finally {
      setIsProcessing(false);
      setProgress(0);
      setStatusMessage('');
    }
  }, []);

  const trustColor = currentResult
    ? currentResult.label === 'organic' ? '#22c55e' : '#ef4444'
    : '#4589F5';

  return (
    <div style={{ position: 'relative' }}>
      <BackgroundBlobs />

      {/* ── Header ── */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 0 8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <img
            src="/logo.svg"
            alt="QuantumEAR"
            width={32}
            height={32}
            style={{ display: 'block', filter: 'drop-shadow(0 2px 8px rgba(251,53,149,0.35))' }}
          />
          <span style={{ fontWeight: 800, fontSize: 15, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>QuantumEAR</span>
        </div>
        <ThemeToggle />
      </header>

      {/* ── Hero ── */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }} style={{ textAlign: 'center', marginTop: 14 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          padding: '5px 14px', borderRadius: 999,
          background: 'rgba(251,53,149,0.10)', border: '1px solid rgba(251,53,149,0.25)',
          marginBottom: 12,
        }}>
          <Zap size={12} color="#FB3595" />
          <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#FB3595' }}>Quantum Enhanced</span>
        </div>
        <div style={{ fontSize: 30, fontWeight: 800, lineHeight: 1.1, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
          Where audio clarity
          <br />
          <span style={{ color: '#FB3595' }}>meets intelligence</span>
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 320, margin: '10px auto 0', lineHeight: 1.6 }}>
          Advanced deepfake detection powered by next-gen quantum algorithms.
        </div>
      </motion.div>

      {/* ── Error Banner ── */}
      <AnimatePresence>
        {error && (
          <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            style={{
              marginTop: 12, padding: '10px 14px', borderRadius: 14,
              background: 'rgba(251,53,149,0.08)', border: '1px solid rgba(251,53,149,0.20)',
              fontSize: 12, color: 'var(--text-secondary)',
            }}>
            Demo mode — backend not connected.
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Hidden file input ── */}
      <input
        ref={inputRef}
        type="file"
        accept="audio/*,.wav,.mp3,.flac,.ogg,.m4a,.aac,.wma"
        style={{ display: 'none' }}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) void handleFileAccepted(f);
          if (e.target) e.target.value = '';
        }}
      />

      {/* ── Main CTA Card ── */}
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1, duration: 0.3 }}
        style={{ marginTop: 22 }}
      >
        <div
          className={isProcessing ? '' : 'animate-gradient-border'}
          onClick={() => { if (!isProcessing) inputRef.current?.click(); }}
          style={{
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            borderRadius: 26, padding: 1.5,
            background: 'linear-gradient(135deg, #FB3595, #a855f7, #4589F5, #FB3595)',
            backgroundSize: '200% 200%',
            boxShadow: isProcessing ? 'none' : '0 0 30px rgba(251,53,149,0.18), 0 0 60px rgba(69,137,245,0.08)',
            opacity: isProcessing ? 0.75 : 1,
            transition: 'box-shadow 0.3s, opacity 0.2s',
          }}
        >
          <div style={{
            borderRadius: 24, padding: '32px 20px',
            background: 'rgba(10,10,10,0.95)',
            textAlign: 'center',
          }}>
            {/* Pulsing mic */}
            <div style={{ position: 'relative', width: 96, height: 96, margin: '0 auto 20px' }}>
              {/* Pulse rings */}
              {!isProcessing && (
                <>
                  <div className="animate-pulse-ring" style={{
                    position: 'absolute', inset: 0, borderRadius: 999,
                    background: 'linear-gradient(135deg, rgba(251,53,149,0.35), rgba(69,137,245,0.35))',
                  }} />
                  <div className="animate-pulse-ring-2" style={{
                    position: 'absolute', inset: 0, borderRadius: 999,
                    background: 'linear-gradient(135deg, rgba(251,53,149,0.18), rgba(69,137,245,0.18))',
                  }} />
                </>
              )}
              {/* Gradient ring */}
              <div style={{
                position: 'absolute', inset: 0, borderRadius: 999, padding: 3,
                background: 'linear-gradient(135deg, #FB3595, #4589F5)',
              }}>
                <div style={{
                  width: '100%', height: '100%', borderRadius: 999,
                  background: '#0d0d0d',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Mic size={36} color="#4589F5" />
                </div>
              </div>
            </div>

            <div style={{ fontSize: 22, fontWeight: 800, color: '#fff', letterSpacing: '-0.02em' }}>Analyze Audio</div>
            <div style={{ fontSize: 13, color: '#9ca3af', marginTop: 5 }}>
              {isProcessing ? statusMessage : 'Tap to upload or record audio'}
            </div>

            {/* Progress bar */}
            {isProcessing && (
              <div style={{ marginTop: 16 }}>
                <div style={{ height: 5, borderRadius: 999, background: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.round(progress * 100)}%` }}
                    transition={{ duration: 0.25 }}
                    style={{
                      height: '100%',
                      background: 'linear-gradient(to right, #FB3595, #4589F5)',
                      borderRadius: 999,
                    }}
                  />
                </div>
                <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 6 }}>{Math.round(progress * 100)}% complete</div>
              </div>
            )}

            {/* Upload hint */}
            {!isProcessing && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 14 }}>
                <Upload size={13} color="#4589F5" />
                <span style={{ fontSize: 12, color: '#4589F5', fontWeight: 600 }}>MP3, WAV, FLAC, M4A supported</span>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* ── Bottom grid: Trust Check + Recent ── */}
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.18, duration: 0.3 }}
        style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 16 }}
      >
        {/* Trust Check */}
        <GlassCard>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Trust Check</div>
          <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', height: 110 }}>
            <div style={{
              width: 96, height: 96, borderRadius: 999, padding: 4,
              background: currentResult
                ? `conic-gradient(${trustColor} ${currentResult.trust_score * 3.6}deg, rgba(255,255,255,0.06) 0deg)`
                : 'conic-gradient(#FB3595 0deg, #4589F5 180deg, rgba(255,255,255,0.06) 180deg)',
            }}>
              <div style={{
                width: '100%', height: '100%', borderRadius: 999,
                background: 'rgba(0,0,0,0.9)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
              }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: currentResult ? trustColor : 'var(--text-primary)' }}>
                  {currentResult ? `${Math.round(currentResult.trust_score)}%` : '—'}
                </div>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 1 }}>
                  {currentResult ? (currentResult.label === 'organic' ? 'Real' : 'Risk') : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Recent Scans */}
        <GlassCard>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Recent</div>
            <button type="button" onClick={() => router.push('/history')}
              style={{ border: 'none', background: 'transparent', color: '#4589F5', fontSize: 11, fontWeight: 700, cursor: 'pointer', padding: 0 }}>
              View all
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {recent.length === 0 ? (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>No scans yet</div>
            ) : (
              recent.map((r) => (
                <button key={r.id} type="button"
                  onClick={() => router.push(`/report?id=${encodeURIComponent(r.id)}`)}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, border: 'none', background: 'transparent', padding: 0, cursor: 'pointer', textAlign: 'left', width: '100%', overflow: 'hidden' }}>
                  <div style={{
                    width: 30, height: 30, borderRadius: 10, flexShrink: 0,
                    background: r.label === 'organic' ? 'rgba(34,197,94,0.12)' : 'rgba(251,53,149,0.12)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    {r.label === 'organic'
                      ? <ShieldCheck size={14} color="#22c55e" />
                      : <AlertTriangle size={14} color="#FB3595" />}
                  </div>
                  <div style={{ minWidth: 0, flex: 1, overflow: 'hidden' }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.filename}</div>
                    <div style={{ fontSize: 10, marginTop: 2, color: r.label === 'organic' ? '#22c55e' : '#FB3595', fontWeight: 600 }}>
                      {r.label === 'organic' ? 'Authentic' : 'Deepfake'}
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </GlassCard>
      </motion.div>
    </div>
  );
}

function GlassCard({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.07)',
      border: '1px solid rgba(255,255,255,0.10)',
      borderRadius: 20,
      padding: 14,
    }}>
      {children}
    </div>
  );
}

function BackgroundBlobs() {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}>
      <div className="animate-blob" style={{ position: 'absolute', top: '-15%', right: '-20%', width: 340, height: 340, background: '#4589F5', filter: 'blur(110px)', opacity: 0.22, borderRadius: 9999 }} />
      <div className="animate-blob-2" style={{ position: 'absolute', top: '22%', left: '-22%', width: 300, height: 300, background: '#FB3595', filter: 'blur(100px)', opacity: 0.20, borderRadius: 9999 }} />
      <div className="animate-blob-3" style={{ position: 'absolute', bottom: '8%', right: '8%', width: 260, height: 260, background: '#a855f7', filter: 'blur(90px)', opacity: 0.13, borderRadius: 9999 }} />
    </div>
  );
}

function getMockResult(filename: string): ScanResult {
  const isSynthetic = Math.random() > 0.5;
  const trustScore = isSynthetic ? Math.round(15 + Math.random() * 35) : Math.round(65 + Math.random() * 30);
  const waveform = Array.from({ length: 500 }, () => (Math.random() - 0.5) * 2 * (0.3 + Math.random() * 0.7));
  return {
    id: crypto.randomUUID(),
    filename,
    trust_score: trustScore,
    label: isSynthetic ? 'synthetic' : 'organic',
    synthetic_probability: isSynthetic ? 0.65 + Math.random() * 0.3 : 0.05 + Math.random() * 0.3,
    entropy_regions: isSynthetic ? [[1.2, 2.1], [3.5, 4.0]] : [],
    entropy_timeline: { times: Array.from({ length: 100 }, (_, i) => i * 0.05), values: Array.from({ length: 100 }, () => Math.random()), threshold: 0.85, total_duration: 5.0 },
    waveform_data: waveform,
    spectrogram_base64: null,
    processing_time_ms: 800 + Math.random() * 2000,
    quantum_features: Array.from({ length: 4 }, () => (Math.random() - 0.5) * 2),
    timestamp: new Date().toISOString(),
    status: 'complete',
  };
}
