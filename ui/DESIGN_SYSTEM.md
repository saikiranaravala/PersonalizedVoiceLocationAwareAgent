# Design System - Personalized Agentic Assistant

## Design Philosophy

**Voice-First, Mobile-First, Accessibility-First**

This design system draws inspiration from Apple's Human Interface Guidelines and Airbnb's design language, emphasizing:
- **Clarity**: Clear visual hierarchy with generous touch targets
- **Deference**: Interface defers to voice content
- **Depth**: Subtle layers and motion create intuitive navigation
- **Accessibility**: WCAG AAA compliant for all users

---

## 🎨 Color System

### Theme Structure

Our theming system uses CSS custom properties for instant theme switching:

```css
:root {
  /* Primary Brand Colors */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-200: #bae6fd;
  --color-primary-300: #7dd3fc;
  --color-primary-400: #38bdf8;
  --color-primary-500: #0ea5e9;  /* Main brand */
  --color-primary-600: #0284c7;
  --color-primary-700: #0369a1;
  --color-primary-800: #075985;
  --color-primary-900: #0c4a6e;
  
  /* Semantic Colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
}
```

### Available Themes

**1. Light Theme (Default)**
- Background: Pure white (#FFFFFF)
- Surface: Soft gray (#F9FAFB)
- Text: Deep charcoal (#1F2937)
- Primary: Ocean blue (#0ea5e9)

**2. Dark Theme**
- Background: Rich black (#0A0A0A)
- Surface: Elevated dark (#1A1A1A)
- Text: Soft white (#F9FAFB)
- Primary: Electric blue (#38bdf8)

**3. High Contrast (Accessibility)**
- Maximum contrast ratios
- Bold outlines
- Enhanced focus indicators

**4. Warm Theme**
- Primary: Amber (#F59E0B)
- Warm neutrals
- Cozy, approachable feel

**5. Cool Theme**
- Primary: Indigo (#6366F1)
- Cool grays
- Professional, calm

---

## 📐 Spacing System

**8-point grid system** (based on iOS and Material Design)

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px - base unit */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
  --space-20: 5rem;    /* 80px */
  --space-24: 6rem;    /* 96px */
}
```

---

## 🔤 Typography

### Font Stack

**Display Font**: SF Pro Display (iOS) / Inter (fallback)
**Body Font**: SF Pro Text (iOS) / System UI (fallback)
**Mono Font**: SF Mono (iOS) / Menlo (fallback)

```css
:root {
  --font-display: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', system-ui, sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
  --font-mono: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
}
```

### Type Scale (Mobile-First, Responsive)

```css
:root {
  /* Mobile */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */
  --text-5xl: 3rem;        /* 48px */
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
  
  /* Letter Spacing */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
}

/* Tablet & Desktop */
@media (min-width: 768px) {
  :root {
    --text-3xl: 2.25rem;   /* 36px */
    --text-4xl: 3rem;      /* 48px */
    --text-5xl: 4rem;      /* 64px */
  }
}
```

---

## 📱 Touch Targets & Sizing

**Minimum touch target**: 44x44px (iOS) / 48x48px (Material)
We use 48px minimum for better accessibility

```css
:root {
  /* Interactive Elements */
  --touch-min: 48px;        /* Minimum touch target */
  --touch-comfortable: 56px; /* Comfortable touch */
  --touch-large: 64px;      /* Large, primary actions */
  
  /* Icon Sizes */
  --icon-xs: 16px;
  --icon-sm: 20px;
  --icon-base: 24px;
  --icon-md: 32px;
  --icon-lg: 40px;
  --icon-xl: 48px;
  --icon-2xl: 64px;
}
```

### Size Categories

**Extra Small (xs)**: Secondary icons, badges
**Small (sm)**: Navigation icons, list items
**Base**: Default interactive elements
**Medium (md)**: Feature highlights
**Large (lg)**: Primary CTAs
**Extra Large (xl)**: Hero actions, microphone button
**2XL**: Voice recording button (main interaction)

---

## 🎭 Motion & Animation

### Timing Functions

```css
:root {
  /* Easing */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  
  /* Durations */
  --duration-fast: 150ms;
  --duration-base: 250ms;
  --duration-slow: 350ms;
  --duration-slower: 500ms;
}
```

### Animation Principles

1. **Purposeful**: Every animation communicates state or guides attention
2. **Responsive**: Animations react to user input immediately
3. **Natural**: Motion follows physics (ease-out for entrance, ease-in for exit)
4. **Accessible**: Respects `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 🔘 Component Specifications

### Buttons

**Primary Button**
- Height: 48px (mobile), 56px (desktop)
- Padding: 16px 24px
- Border radius: 12px
- Font: Semi-bold, 16px
- Active state: Scale 0.98

**Secondary Button**
- Height: 48px
- Padding: 16px 24px
- Border: 2px solid
- Background: Transparent

**Icon Button**
- Size: 48x48px minimum
- Padding: 12px
- Border radius: 50%

**Voice Button (Main CTA)**
- Size: 72x72px (mobile), 80x80px (desktop)
- Border radius: 50%
- Pulse animation on active
- Haptic feedback trigger

### Cards

**Elevation System** (Apple-inspired)

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.04);
}
```

**Card Specs**
- Border radius: 16px
- Padding: 20px
- Background: Surface color
- Shadow: --shadow-md (resting), --shadow-lg (hover)

### Input Fields

- Height: 48px
- Padding: 12px 16px
- Border: 1px solid (neutral-300)
- Border radius: 12px
- Focus: 3px outline, primary color

### Navigation

**Bottom Tab Bar** (Mobile)
- Height: 72px (includes safe area)
- 4-5 items maximum
- Active indicator: Bold + primary color
- Touch target: Full width per item

**Top Navigation** (Desktop)
- Height: 64px
- Sticky on scroll
- Blur background when scrolling

---

## ♿ Accessibility Standards

### WCAG AAA Compliance

**Color Contrast**
- Normal text: 7:1 minimum
- Large text (18px+): 4.5:1 minimum
- UI components: 3:1 minimum

**Focus Indicators**
- Visible outline: 3px solid
- Color: Primary brand color
- Offset: 2px from element

**Keyboard Navigation**
- All interactive elements accessible via Tab
- Logical tab order
- Skip links for main content

**Screen Reader Support**
- Semantic HTML5 elements
- ARIA labels for all icons
- Live regions for voice status
- Descriptive button labels

**Touch Gestures**
- All features accessible without gestures
- Gesture alternatives provided
- Clear feedback for all interactions

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  .voice-pulse {
    animation: none;
  }
  .slide-in {
    transition: none;
  }
}
```

---

## 🌐 Responsive Breakpoints

```css
:root {
  /* Mobile first */
  --breakpoint-sm: 640px;   /* Large phone */
  --breakpoint-md: 768px;   /* Tablet */
  --breakpoint-lg: 1024px;  /* Desktop */
  --breakpoint-xl: 1280px;  /* Large desktop */
  --breakpoint-2xl: 1536px; /* Extra large */
}
```

### Layout Guidelines

**Mobile (< 640px)**
- Single column
- Full-width components
- Bottom navigation
- Large touch targets

**Tablet (640px - 1024px)**
- Two column grid
- Side navigation option
- Increased spacing

**Desktop (> 1024px)**
- Multi-column layouts
- Hover states enabled
- Keyboard shortcuts
- Mouse interactions

---

## 🎯 Voice-Specific Components

### Waveform Visualizer
- Real-time audio visualization
- Smooth 60fps animation
- Primary color gradient
- Height: 120px

### Status Indicators
- Listening: Pulsing blue
- Processing: Spinning gradient
- Speaking: Animated bars
- Error: Red shake animation

### Conversation Bubbles
- User: Right-aligned, primary color
- Assistant: Left-aligned, surface color
- Timestamp: Small, gray
- Max width: 75% viewport

---

## 📦 Component Library Structure

```
components/
├── core/
│   ├── Button/
│   ├── Card/
│   ├── Input/
│   ├── Icon/
│   └── Typography/
├── voice/
│   ├── VoiceButton/
│   ├── Waveform/
│   ├── StatusIndicator/
│   └── ConversationBubble/
├── navigation/
│   ├── TabBar/
│   ├── TopNav/
│   └── Sidebar/
├── layout/
│   ├── Container/
│   ├── Grid/
│   ├── Stack/
│   └── Spacer/
└── feedback/
    ├── Toast/
    ├── Modal/
    ├── Spinner/
    └── ProgressBar/
```

---

## 🎨 Theme Switching

### Implementation

```javascript
// Theme context
const themes = {
  light: { /* light theme vars */ },
  dark: { /* dark theme vars */ },
  highContrast: { /* high contrast vars */ },
  warm: { /* warm theme vars */ },
  cool: { /* cool theme vars */ }
};

// Apply theme
function applyTheme(themeName) {
  const theme = themes[themeName];
  Object.entries(theme).forEach(([key, value]) => {
    document.documentElement.style.setProperty(key, value);
  });
}
```

### User Preference Persistence

```javascript
// Save to localStorage
localStorage.setItem('theme', 'dark');

// Respect system preference
const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)');
```

---

## 🔧 Development Tools

### CSS Architecture
- CSS Modules for component scoping
- CSS Custom Properties for theming
- PostCSS for vendor prefixing
- Utility classes for common patterns

### Component Documentation
- Storybook for component showcase
- Visual regression testing
- Accessibility audits
- Performance monitoring

---

## 📊 Performance Targets

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s
- **Cumulative Layout Shift**: < 0.1
- **Lighthouse Score**: > 95

---

## 🎯 Design Tokens Export

All design tokens are available as:
- CSS Custom Properties
- JavaScript/TypeScript constants
- Figma tokens
- JSON configuration

This ensures consistency across design and development.

---

**Last Updated**: 2024
**Version**: 1.0.0
**Maintainer**: Design System Team
