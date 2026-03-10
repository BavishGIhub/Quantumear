'use client';

import React, { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('theme');
    const dark = stored !== 'light';
    document.documentElement.classList.toggle('dark', dark);
    setIsDark(dark);
  }, []);

  const toggle = () => {
    const next = !isDark;
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
    setIsDark(next);
  };

  return (
    <button
      type="button"
      onClick={toggle}
      style={{
        width: 36,
        height: 36,
        borderRadius: 999,
        border: '1px solid var(--border-default)',
        background: 'var(--bg-surface)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        flexShrink: 0,
      }}
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Sun size={16} color="var(--text-primary)" />
      ) : (
        <Moon size={16} color="var(--text-primary)" />
      )}
    </button>
  );
}
