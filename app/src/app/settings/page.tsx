'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Cpu, Lock, Info, ChevronRight } from 'lucide-react';
import { loadSettings, saveSettings, AppSettings } from '@/lib/settings';
import { clearLocalHistory, loadLocalHistory } from '@/lib/historyStore';
import ThemeToggle from '@/components/ThemeToggle';

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings>(() => loadSettings());
  const [historyCount, setHistoryCount] = useState(0);
  const [cleared, setCleared] = useState(false);

  useEffect(() => {
    saveSettings(settings);
  }, [settings]);

  useEffect(() => {
    setHistoryCount(loadLocalHistory().length);
  }, []);

  const handleClearHistory = () => {
    clearLocalHistory();
    setHistoryCount(0);
    setCleared(true);
    setTimeout(() => setCleared(false), 2000);
  };

  const handleExportData = () => {
    const history = loadLocalHistory();
    const data = JSON.stringify({ settings, history, exportedAt: new Date().toISOString() }, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `quantumear-export-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ position: 'relative' }}>
      <BackgroundBlobs />

      {/* ── Header ── */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 0 10px' }}>
        <div style={{ fontSize: 26, fontWeight: 900, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>Settings</div>
        <ThemeToggle />
      </header>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}
        style={{ display: 'flex', flexDirection: 'column', gap: 20, marginTop: 8 }}>

        {/* ── Quantum Engine ── */}
        <Section title="Quantum Engine" icon={<Cpu size={14} color="#4589F5" />}>
          <ToggleRow
            title="High-Fidelity Analysis"
            subtitle="Uses more compute for deeper detection"
            checked={settings.highFidelityAnalysis}
            onChange={(v) => setSettings((s) => ({ ...s, highFidelityAnalysis: v }))}
          />
          <ToggleRow
            title="Active Noise Filter"
            subtitle="Pre-process audio to suppress static"
            checked={settings.activeNoiseFilter}
            onChange={(v) => setSettings((s) => ({ ...s, activeNoiseFilter: v }))}
          />
          <InfoRow title="Model Version" value="Quantum v2.4 (Stable)" />
          <InfoRow title="Classifier" value="Hybrid CNN + QNN Ensemble" last />
        </Section>

        {/* ── Privacy ── */}
        <Section title="Privacy" icon={<Lock size={14} color="#FB3595" />}>
          <ToggleRow
            title="Incognito Analysis"
            subtitle="Results won't be saved to history"
            checked={settings.incognitoAnalysis}
            onChange={(v) => setSettings((s) => ({ ...s, incognitoAnalysis: v }))}
          />
          <ActionRow
            title="Clear Scan History"
            subtitle={cleared ? 'History cleared!' : `${historyCount} scan${historyCount !== 1 ? 's' : ''} stored locally`}
            actionLabel={cleared ? '✓ Cleared' : 'Clear'}
            onAction={handleClearHistory}
            destructive={!cleared}
          />
          <ActionRow
            title="Export Data"
            subtitle="Download history & settings as JSON"
            actionLabel="Export"
            onAction={handleExportData}
            last
          />
        </Section>

        {/* ── About ── */}
        <Section title="About" icon={<Info size={14} color="#a855f7" />}>
          <InfoRow title="Version" value="2.4.1 (Build 8902)" />
          <InfoRow title="Engine" value="ResNet-18 + 4-Qubit QNN" />
          <InfoRow title="Entropy" value="Spectral @ 22050 Hz" last />
        </Section>

        <div style={{ textAlign: 'center', paddingBottom: 8 }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', opacity: 0.6 }}>QuantumEAR — Quantum Enhanced Audio Recognition</div>
        </div>

      </motion.div>
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, margin: '0 0 8px 2px' }}>
        {icon}
        <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>{title}</span>
      </div>
      <div style={{
        background: 'rgba(255,255,255,0.07)',
        border: '1px solid rgba(255,255,255,0.10)',
        borderRadius: 20, overflow: 'hidden',
      }}>
        {children}
      </div>
    </div>
  );
}

function InfoRow({ title, value, last = false }: { title: string; value: string; last?: boolean }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '14px 16px',
      borderBottom: last ? 'none' : '1px solid rgba(255,255,255,0.08)',
    }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{title}</div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 500 }}>{value}</div>
    </div>
  );
}

function ActionRow({ title, subtitle, actionLabel, onAction, destructive = false, last = false }: {
  title: string; subtitle: string; actionLabel: string; onAction: () => void; destructive?: boolean; last?: boolean;
}) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '14px 16px',
      borderBottom: last ? 'none' : '1px solid rgba(255,255,255,0.08)',
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{title}</div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{subtitle}</div>
      </div>
      <button type="button" onClick={onAction} style={{
        padding: '7px 14px', borderRadius: 12, marginLeft: 12,
        border: `1px solid ${destructive ? 'rgba(239,68,68,0.30)' : 'rgba(69,137,245,0.30)'}`,
        background: destructive ? 'rgba(239,68,68,0.08)' : 'rgba(69,137,245,0.08)',
        color: destructive ? '#ef4444' : '#4589F5',
        fontSize: 12, fontWeight: 700, cursor: 'pointer', whiteSpace: 'nowrap',
        transition: 'all 0.2s',
      }}>
        {actionLabel}
      </button>
    </div>
  );
}

function ToggleRow({ title, subtitle, checked, onChange }: {
  title: string; subtitle: string; checked: boolean; onChange: (v: boolean) => void;
}) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '14px 16px',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{title}</div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{subtitle}</div>
      </div>
      <Switch checked={checked} onChange={onChange} />
    </div>
  );
}

function Switch({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button type="button" onClick={() => onChange(!checked)} aria-pressed={checked} style={{
      width: 48, height: 26, borderRadius: 999, flexShrink: 0, marginLeft: 12,
      background: checked
        ? 'linear-gradient(to right, #FB3595, #4589F5)'
        : 'var(--bg-elevated)',
      border: checked ? '1.5px solid transparent' : '1.5px solid var(--border-hover)',
      position: 'relative', cursor: 'pointer',
      boxShadow: checked ? '0 0 12px rgba(251,53,149,0.35)' : 'none',
      transition: 'background 200ms ease, box-shadow 200ms ease',
    }}>
      <span style={{
        position: 'absolute', top: checked ? 4 : 3,
        left: checked ? 26 : 3,
        width: 18, height: 18, borderRadius: 999,
        background: checked ? '#fff' : 'var(--text-muted)',
        transition: 'left 200ms ease, background 200ms ease',
        boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
      }} />
    </button>
  );
}

function BackgroundBlobs() {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}>
      <div className="animate-blob" style={{ position: 'absolute', top: '-10%', left: '-10%', width: 300, height: 300, background: '#4589F5', filter: 'blur(110px)', opacity: 0.16, borderRadius: 9999 }} />
      <div className="animate-blob-2" style={{ position: 'absolute', bottom: '20%', right: '-10%', width: 260, height: 260, background: '#FB3595', filter: 'blur(100px)', opacity: 0.14, borderRadius: 9999 }} />
    </div>
  );
}

