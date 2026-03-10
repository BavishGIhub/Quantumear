'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, History, Home, Settings } from 'lucide-react';

export default function Navbar() {
    const pathname = usePathname();

    const links = [
        { href: '/', label: 'Home', icon: Home },
        { href: '/history', label: 'History', icon: History },
        { href: '/stats', label: 'Stats', icon: BarChart3 },
        { href: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <nav style={{
            position: 'fixed',
            left: 12, right: 12,
            bottom: 'calc(8px + var(--safe-bottom, 0px))',
            zIndex: 50,
            background: 'var(--bg-navbar)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            border: '1px solid var(--border-default)',
            borderRadius: 22,
            boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
        }}>
            <div style={{
                height: 58,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-around',
                padding: '0 6px',
                maxWidth: 520,
                margin: '0 auto',
            }}>
                {links.map((link) => {
                    const Icon = link.icon;
                    const active = link.href === '/'
                        ? pathname === '/'
                        : pathname.startsWith(link.href);

                    return (
                        <Link key={link.href} href={link.href} style={{
                            textDecoration: 'none',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 4,
                            padding: '7px 18px',
                            borderRadius: 14,
                            position: 'relative',
                            background: active
                                ? 'linear-gradient(135deg, rgba(251,53,149,0.15), rgba(69,137,245,0.15))'
                                : 'transparent',
                            transition: 'background 0.25s ease',
                        }}>
                            {active && (
                                <span style={{
                                    position: 'absolute',
                                    top: 3,
                                    left: '50%',
                                    transform: 'translateX(-50%)',
                                    width: 4,
                                    height: 4,
                                    borderRadius: 999,
                                    background: 'linear-gradient(to right, #FB3595, #4589F5)',
                                    boxShadow: '0 0 6px #FB3595',
                                }} />
                            )}
                            <Icon
                                size={21}
                                color={active ? '#FB3595' : 'var(--text-muted)'}
                                strokeWidth={active ? 2.5 : 1.7}
                            />
                            <span style={{
                                fontSize: 10,
                                fontWeight: active ? 700 : 500,
                                color: active ? '#FB3595' : 'var(--text-muted)',
                                letterSpacing: '0.01em',
                                transition: 'color 0.25s ease',
                            }}>
                                {link.label}
                            </span>
                        </Link>
                    );
                })}
            </div>
        </nav>
    );
}
