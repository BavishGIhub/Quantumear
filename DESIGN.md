# Design System: QuantumEAR Mobile
**Project ID:** 5839098960376223996 (Stitch Reference)

## 1. Visual Theme & Atmosphere

QuantumEAR embodies a **"Future-Tech Laboratory"** aesthetic — clean, authoritative, and scientifically precise. The design language draws from:
- **Deep Space Navigation**: Dark backgrounds with vibrant blue waypoints
- **Scientific Instrumentation**: Clear data hierarchies and measured precision
- **Mobile-First Density**: Optimized for thumb-friendly touch targets while maintaining information density

The atmosphere is **focused and clinical**, yet approachable. Deep navy backgrounds create immersion, while electric blue accents guide the user's attention to critical analysis data.

## 2. Color Palette & Roles

### Primary Colors
- **Deep Space Navy** (`#030712`): Primary background — creates infinite depth
- **Laboratory Blue** (`#1736cf`): Primary accent — interactive elements, active states, trust indicators
- **Bright Signal Blue** (`#2563eb`): Highlights, progress indicators, positive scan results
- **Pure White** (`#ffffff`): Primary text on dark backgrounds

### Secondary Colors
- **Slate Gray** (`#64748b`): Secondary text, timestamps, metadata
- **Muted Silver** (`#94a3b8`): Tertiary text, disabled states
- **Surface Gray** (`#1e293b`): Card backgrounds, elevated surfaces
- **Border Gray** (`#334155`): Subtle dividers and borders

### Semantic Colors
- **Safe Green** (`#22c55e`): Organic voice detected, success states
- **Warning Amber** (`#f59e0b`): Suspicious audio, medium risk
- **Alert Red** (`#ef4444`): Synthetic detected, high-risk alerts

### Usage Patterns
- Backgrounds: Deep navy with subtle gradient overlays
- Cards: Semi-transparent surface gray with 8px rounded corners
- Interactive elements: Laboratory blue with glow effects on hover/active
- Data visualization: Gradient blues for entropy charts, semantic colors for trust scores

## 3. Typography Rules

### Font Family
- **Primary**: `Space Grotesk` — Modern geometric sans-serif with technical character
- **Monospace**: `JetBrains Mono` — For quantum values, timestamps, file sizes

### Type Scale (Mobile-Optimized)

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| H1 | 28px | 700 | Screen titles ("QuantumEAR", "Analysis Report") |
| H2 | 20px | 600 | Section headers ("Waveform Analysis") |
| H3 | 16px | 600 | Card titles, scan filenames |
| Body | 14px | 400 | Primary content, descriptions |
| Caption | 12px | 500 | Timestamps, metadata, labels |
| Mono | 13px | 600 | Quantum features, trust scores, file sizes |

### Typography Patterns
- **Headings**: Tight letter-spacing (-0.02em), bold weights for impact
- **Body Text**: Relaxed line-height (1.6) for readability on mobile
- **Monospace Data**: Slightly larger (13px) for scan results, bright blue color (#2563eb)
- **Labels**: Uppercase, 11px, 500 weight, slate gray (#64748b), letter-spacing 0.1em

## 4. Component Stylings

### Cards (Primary Container)
- **Background**: `#1e293b` with 90% opacity
- **Border**: 1px solid `#334155`
- **Border Radius**: 8px (ROUND_EIGHT from Stitch)
- **Padding**: 16px mobile, 20px tablet+
- **Shadow**: None (flat design aesthetic)
- **Hover**: Subtle border color shift to `#475569`

### Buttons (Primary Action)
- **Background**: `#1736cf`
- **Text**: White, 14px, 600 weight
- **Padding**: 12px 24px
- **Border Radius**: 8px
- **Active State**: Bright blue `#2563eb` with subtle glow
- **Disabled**: 50% opacity with `#64748b` text

### Buttons (Secondary/Ghost)
- **Background**: Transparent
- **Border**: 1px solid `#334155`
- **Text**: `#94a3b8`
- **Hover**: Background `#1e293b`, border `#475569`

### Input Fields (DropZone)
- **Border**: 2px dashed `#334155`
- **Background**: `#0f172a` (slightly lighter than page)
- **Border Radius**: 8px
- **Active/Drag**: Border solid `#1736cf`, background `#1e293b`
- **Icon**: Centered, 48px, blue gradient

### Navigation Bar (Mobile-Optimized)
- **Background**: `#030712` with frosted glass blur (backdrop-filter)
- **Height**: 64px + safe area insets
- **Border Bottom**: 1px solid `#1e293b`
- **Logo**: Left-aligned, 36px icon + wordmark
- **Actions**: Right-aligned icons

### Bottom Tab Bar (Mobile)
- **Background**: `#0f172a`
- **Height**: 64px + safe area bottom
- **Border Top**: 1px solid `#1e293b`
- **Active Tab**: Blue icon (#1736cf) with filled style
- **Inactive Tab**: Gray icon (#64748b) with outline style
- **Labels**: 11px, shown only on active tab

### Trust Score Gauge
- **Size**: 180px diameter (mobile), 220px (tablet+)
- **Stroke Width**: 10px
- **Track Color**: `#1e293b`
- **Fill Gradient**: Blue (`#1736cf`) to cyan (`#06b6d4`)
- **Center Text**: Space Grotesk, 48px, 700 weight
- **Label**: "Trust Score", 12px, uppercase, slate gray

### Data Chips/Tags
- **Background**: `#0f172a`
- **Border**: 1px solid `#334155`
- **Border Radius**: 6px
- **Padding**: 6px 12px
- **Text**: 12px, monospace for values

### Waveform Visualization
- **Background**: `#0f172a`
- **Wave Color**: Gradient from `#1736cf` to `#06b6d4`
- **Entropy Highlights**: Red overlay (`#ef4444` at 20% opacity)
- **Border Radius**: 8px
- **Padding**: 12px

## 5. Layout Principles

### Spacing System (4px Grid)
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px
- **2xl**: 48px

### Mobile Layout (320px - 428px)
- **Single column** layout for all content
- **Full-width cards** with 16px horizontal padding
- **Touch targets**: Minimum 44px height
- **Bottom navigation**: Fixed tab bar for primary actions
- **Safe areas**: Respect `env(safe-area-inset-*)` for notched devices

### Content Hierarchy
1. **Header**: Logo + status indicator
2. **Primary Action**: DropZone for audio upload (prominent, centered)
3. **Results**: Trust meter (large, visual impact)
4. **Details**: Collapsible sections for waveform, entropy, features
5. **History**: Horizontal scrolling cards or vertical list
6. **Navigation**: Fixed bottom tab bar

### Grid & Alignment
- **Container**: Max-width 100%, padding 16px
- **Cards**: Full width, internal padding 16px
- **Text Alignment**: Left-aligned for readability
- **Centered Elements**: Trust meter, empty states, primary actions

## 6. Animation & Motion

### Principles
- **Purposeful**: Animations guide attention or provide feedback
- **Subtle**: Never distract from the analytical task
- **Fast**: 200-300ms duration for responsive feel

### Standard Animations
- **Page Transitions**: Fade + slight translateY (20px), 300ms ease-out
- **Card Entrance**: Staggered fade-in, 50ms delay between items
- **Button Hover**: Background color shift, 200ms ease
- **Progress Indicators**: Continuous gradient animation on bars
- **Trust Meter**: Smooth stroke-dashoffset animation, 1.5s ease-out
- **Counter**: Number counting animation with easing

### Mobile Haptics (Capacitor Integration)
- **Light Impact**: Successful upload start
- **Medium Impact**: Analysis complete - organic detected
- **Heavy Impact**: Analysis complete - synthetic detected (urgent)
- **Success Pattern**: Two quick light impacts for saved to history

## 7. Screen-Specific Guidelines

### Dashboard (Home)
- **Hero**: App title + tagline centered
- **Primary**: Large DropZone (60% of screen)
- **Recent**: Horizontal scrolling scan cards (peek at edges)
- **Empty State**: Icon + "Tap to analyze your first audio file"

### Analysis Results
- **Header**: Back button + "Analysis Report" title
- **Hero**: Trust meter (prominent, top section)
- **Status Badge**: Large, colored indicator (Organic/Synthetic)
- **Sections** (collapsible):
  - Waveform Analysis
  - Entropy Timeline
  - Quantum Features
  - File Metadata

### Scan History
- **List View**: Vertical stack of scan cards
- **Card Content**: Filename, timestamp, trust score badge
- **Swipe Actions**: Delete (red), Share (blue)
- **Empty State**: "No scans yet" with upload CTA

## 8. Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | Single column, bottom nav, full-width cards |
| Tablet | 640-1024px | 2-column layout for results, side nav |
| Desktop | > 1024px | 3-column layout, persistent sidebar |

## 9. Accessibility

### Color Contrast
- All text meets WCAG AA (4.5:1) against backgrounds
- Trust score colors have text alternatives ("Organic" not just green)

### Touch Targets
- Minimum 44px × 44px for all interactive elements
- Adequate spacing between adjacent targets (8px minimum)

### Screen Reader
- Meaningful alt text for all icons
- Live regions for analysis progress updates
- Semantic HTML structure with proper heading hierarchy

## 10. Implementation Notes

### Required Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### CSS Custom Properties
```css
:root {
  --color-primary: #1736cf;
  --color-primary-bright: #2563eb;
  --color-bg: #030712;
  --color-surface: #1e293b;
  --color-border: #334155;
  --color-text: #ffffff;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  --radius: 8px;
  --font-primary: 'Space Grotesk', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

### Capacitor-Safe Areas
```css
.safe-top { padding-top: env(safe-area-inset-top, 0); }
.safe-bottom { padding-bottom: env(safe-area-inset-bottom, 0); }
```
