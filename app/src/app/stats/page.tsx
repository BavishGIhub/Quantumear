'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Shield, AlertOctagon, Clock, TrendingUp } from 'lucide-react';
import api from '@/lib/api';
import { ScanResult } from '@/types';
import { loadLocalHistory } from '@/lib/historyStore';
import ThemeToggle from '@/components/ThemeToggle';

export default function StatsPage() {
  const [history, setHistory] = useState<ScanResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      try {
        const data = await api.getHistory();
        if (!mounted) return;
        setHistory(data.results || []);
      } catch {
        if (!mounted) return;
        setHistory(loadLocalHistory());
      } finally {
        if (!mounted) return;
        setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const metrics = useMemo(() => {
    const total = history.length;
    const organic = history.filter((h) => h.label === 'organic').length;
    const synthetic = history.filter((h) => h.label === 'synthetic').length;
    const authenticityRate = total > 0 ? (organic / total) * 100 : 0;
    const avgProcessingMs = total > 0 ? history.reduce((a, h) => a + (h.processing_time_ms || 0), 0) / total : 0;

    const recentThreats = history
      .filter((h) => h.label === 'synthetic' || h.trust_score < 40)
      .slice(0, 5);

    return {
      total,
      organic,
      synthetic,
      authenticityRate,
      avgProcessingMs,
      recentThreats,
    };
  }, [history]);

  return (
    <div style={{ position: 'relative' }}>
      <BackgroundBlobs />

      {/* ── Header ── */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 0 10px' }}>
        <div style={{ fontSize: 22, fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>Statistics</div>
        <ThemeToggle />
      </header>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>

        {/* ── Overview + Segmented ── */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)' }}>Overview</div>
          <Segmented />
        </div>

        {/* ── Metric Cards ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <MetricCard
            icon={<BarChart3 size={18} color="#4589F5" />}
            title="Total Scans"
            value={loading ? '—' : metrics.total.toLocaleString()}
            subtitle="All-time audio analyses"
            barWidth={Math.min(100, metrics.total * 4)}
            barColor="linear-gradient(to right, #4589F5, #a855f7)"
          />
          <MetricCard
            icon={<Shield size={18} color="#22c55e" />}
            title="Authenticity Rate"
            value={loading ? '—' : `${metrics.authenticityRate.toFixed(1)}%`}
            subtitle="Verified organic audio"
            barWidth={metrics.authenticityRate}
            barColor="linear-gradient(to right, #22c55e, #4589F5)"
          />
          <MetricCard
            icon={<AlertOctagon size={18} color="#ef4444" />}
            title="Threats Detected"
            value={loading ? '—' : metrics.synthetic.toLocaleString()}
            subtitle="AI-generated voices found"
            barWidth={metrics.total > 0 ? (metrics.synthetic / metrics.total) * 100 : 0}
            barColor="linear-gradient(to right, #FB3595, #ef4444)"
          />
        </div>

        {/* ── Recent Threats ── */}
        <GlassCard style={{ marginTop: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <div style={{ width: 32, height: 32, borderRadius: 10, background: 'rgba(251,53,149,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <AlertOctagon size={16} color="#FB3595" />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 800, color: 'var(--text-primary)' }}>Recent Threats</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Most suspicious scans</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {loading ? (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', padding: '8px 0' }}>Loading…</div>
            ) : metrics.recentThreats.length === 0 ? (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
                No threats detected yet 🎉
              </div>
            ) : (
              metrics.recentThreats.map((t) => (
                <div key={t.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0, flex: 1 }}>
                    <div style={{
                      width: 34, height: 34, borderRadius: 10, flexShrink: 0,
                      background: 'rgba(251,53,149,0.10)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <div style={{ width: 8, height: 8, borderRadius: 999, background: '#FB3595', boxShadow: '0 0 6px #FB3595' }} />
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.filename}</div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 1 }}>{Math.round(t.trust_score)}% trust score</div>
                    </div>
                  </div>
                  <span style={{
                    fontSize: 10, fontWeight: 700, flexShrink: 0,
                    color: t.label === 'synthetic' ? '#ef4444' : '#fb923c',
                    background: t.label === 'synthetic' ? 'rgba(239,68,68,0.10)' : 'rgba(251,146,60,0.10)',
                    padding: '4px 8px', borderRadius: 8,
                  }}>
                    {t.label === 'synthetic' ? 'Deepfake' : 'Suspicious'}
                  </span>
                </div>
              ))
            )}
          </div>
        </GlassCard>

        {/* ── Processing Time ── */}
        <GlassCard style={{ marginTop: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: 'rgba(251,53,149,0.10)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Clock size={18} color="#FB3595" />
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)' }}>Avg Processing Time</div>
              <div style={{ fontSize: 28, fontWeight: 900, color: '#FB3595', lineHeight: 1.1 }}>
                {loading ? '—' : `${(metrics.avgProcessingMs / 1000).toFixed(2)}s`}
              </div>
            </div>
          </div>
          <div style={{ marginTop: 10, height: 4, borderRadius: 999, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: loading ? '0%' : `${Math.min(100, (metrics.avgProcessingMs / 5000) * 100)}%` }}
              transition={{ duration: 1, delay: 0.3 }}
              style={{ height: '100%', background: 'linear-gradient(to right, #FB3595, #4589F5)', borderRadius: 999 }}
            />
          </div>
        </GlassCard>

      </motion.div>
    </div>
  );
}

function Segmented() {
  const [active, setActive] = useState<'week' | 'month' | 'year'>('week');
  return (
    <div style={{ display: 'flex', borderRadius: 999, background: 'rgba(255,255,255,0.07)', padding: 3, border: '1px solid rgba(255,255,255,0.10)' }}>
      {(['week', 'month', 'year'] as const).map((k) => (
        <button key={k} type="button" onClick={() => setActive(k)} style={{
          padding: '6px 12px', borderRadius: 999, border: 'none',
          background: active === k ? 'linear-gradient(135deg, rgba(251,53,149,0.35), rgba(69,137,245,0.35))' : 'transparent',
          color: active === k ? '#fff' : 'var(--text-muted)',
          fontSize: 11, fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s',
        }}>
          {k.charAt(0).toUpperCase() + k.slice(1)}
        </button>
      ))}
    </div>
  );
}

function MetricCard({ icon, title, value, subtitle, barWidth, barColor }: {
  icon: React.ReactNode; title: string; value: string; subtitle: string; barWidth: number; barColor: string;
}) {
  return (
    <GlassCard>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 38, height: 38, borderRadius: 12, background: 'rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {icon}
          </div>
          <div>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)' }}>{title}</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', opacity: 0.7 }}>{subtitle}</div>
          </div>
        </div>
        <div style={{ fontSize: 28, fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>{value}</div>
      </div>
      <div style={{ marginTop: 12, height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 999, overflow: 'hidden' }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(100, Math.max(0, barWidth))}%` }}
          transition={{ duration: 0.9, delay: 0.2, ease: 'easeOut' }}
          style={{ height: '100%', background: barColor, borderRadius: 999 }}
        />
      </div>
    </GlassCard>
  );
}

function GlassCard({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.07)',
      border: '1px solid rgba(255,255,255,0.10)',
      borderRadius: 20, padding: 16,
      ...style,
    }}>
      {children}
    </div>
  );
}

function BackgroundBlobs() {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}>
      <div className="animate-blob" style={{ position: 'absolute', top: '-10%', right: '-20%', width: 320, height: 320, background: '#4589F5', filter: 'blur(110px)', opacity: 0.20, borderRadius: 9999 }} />
      <div className="animate-blob-2" style={{ position: 'absolute', top: '25%', left: '-20%', width: 280, height: 280, background: '#FB3595', filter: 'blur(100px)', opacity: 0.18, borderRadius: 9999 }} />
      <div className="animate-blob-3" style={{ position: 'absolute', bottom: '5%', right: '10%', width: 240, height: 240, background: '#a855f7', filter: 'blur(90px)', opacity: 0.11, borderRadius: 9999 }} />
    </div>
  );
}

