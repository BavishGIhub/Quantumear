'use client';

import React, { Suspense, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import api from '@/lib/api';
import { ScanResult } from '@/types';
import TrustMeter from '@/components/TrustMeter';
import WaveformViewer from '@/components/WaveformViewer';
import ResultsPanel from '@/components/ResultsPanel';
import ThemeToggle from '@/components/ThemeToggle';
import { loadLocalHistory } from '@/lib/historyStore';

export default function ReportPage() {
  return (
    <Suspense
      fallback={
        <div style={{ padding: 18, borderRadius: 18, background: 'var(--bg-surface)', border: '1px solid var(--border-default)' }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Loading report…</div>
        </div>
      }
    >
      <ReportPageInner />
    </Suspense>
  );
}

function ReportPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = searchParams.get('id');

  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      if (!id) {
        setError('Missing report id');
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const res = await api.getScanResult(id);
        if (!mounted) return;
        setResult(res);
      } catch (e) {
        if (!mounted) return;
        // Try localStorage fallback
        const localHistory = loadLocalHistory();
        const localResult = localHistory.find(h => h.id === id);
        if (localResult) {
          setResult(localResult);
        } else {
          setError(e instanceof Error ? e.message : 'Failed to load report');
        }
      } finally {
        if (!mounted) return;
        setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [id]);

  const duration = useMemo(() => result?.entropy_timeline?.total_duration || 5, [result]);

  return (
    <div style={{ position: 'relative' }}>
      <BackgroundBlobs />

      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 0 10px' }}>
        <button
          type="button"
          onClick={() => router.back()}
          style={{
            width: 36,
            height: 36,
            borderRadius: 999,
            border: '1px solid var(--border-default)',
            background: 'var(--bg-surface)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
          }}
          aria-label="Back"
        >
          <span style={{ fontSize: 16, fontWeight: 900, color: 'var(--text-primary)' }}>←</span>
        </button>

        <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>Report</div>

        <ThemeToggle />
      </header>

      {loading ? (
        <div style={{ padding: 18, borderRadius: 18, background: 'var(--bg-surface)', border: '1px solid var(--border-default)' }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Loading report…</div>
        </div>
      ) : error ? (
        <div style={{ padding: 18, borderRadius: 18, background: 'var(--bg-surface)', border: '1px solid var(--border-default)' }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{error}</div>
        </div>
      ) : result ? (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
            <TrustMeter score={result.trust_score} label={result.label} isAnimating={true} />
            <WaveformViewer waveformData={result.waveform_data} entropyRegions={result.entropy_regions} duration={duration} />
            <ResultsPanel result={result} />
          </div>
        </motion.div>
      ) : null}
    </div>
  );
}

function BackgroundBlobs() {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
      <div style={{ position: 'absolute', top: '-10%', right: '-20%', width: 320, height: 320, background: '#4589F5', filter: 'blur(120px)', opacity: 0.18, borderRadius: 9999 }} />
      <div style={{ position: 'absolute', top: '25%', left: '-20%', width: 280, height: 280, background: '#FB3595', filter: 'blur(100px)', opacity: 0.16, borderRadius: 9999 }} />
      <div style={{ position: 'absolute', bottom: '5%', right: '10%', width: 240, height: 240, background: '#a855f7', filter: 'blur(90px)', opacity: 0.10, borderRadius: 9999 }} />
    </div>
  );
}

