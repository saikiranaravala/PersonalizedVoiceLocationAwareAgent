# Personalized Agentic Assistant - UI

**Mobile-First, Voice-First, Accessibility-First Design System**

A production-grade React component library designed for voice-based interactions with exceptional accessibility and beautiful design.

---

## 🎨 Design Philosophy

This UI follows three core principles:

1. **Mobile-First**: Optimized for touch devices with generous tap targets (48px minimum)
2. **Voice-First**: Interface defers to voice interactions, with clear visual feedback
3. **Accessibility-First**: WCAG AAA compliant, screen reader optimized, keyboard navigable

### Design Inspiration

- **Apple Human Interface Guidelines**: Clean, refined, gesture-based interactions
- **Airbnb Design Language**: Accessible, thoughtful component design
- **Material Design**: Touch targets and elevation system

---

## 📦 What's Included

### Core Components

- **Button** - Multiple variants with loading states, icons, and full accessibility
- **VoiceButton** - Main interaction element with pulse animations and status feedback
- **Card** - Elevated surfaces for content grouping
- **Input** - Form elements with validation and error states

### Voice Components

- **VoiceButton** - Primary voice interaction with visual feedback
- **Waveform** - Audio visualization component
- **StatusIndicator** - Real-time status display
- **ConversationBubble** - Chat-style message display

### Layout Components

- **Container** - Responsive max-width container
- **Grid** - CSS Grid wrapper with responsive columns
- **Stack** - Flexbox-based vertical/horizontal spacing
- **Spacer** - Consistent spacing utility

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Basic Usage

```tsx
import { VoiceButton, Button } from './components';
import './styles/tokens.css';
import './styles/global.css';

function App() {
  const [status, setStatus] = useState('idle');

  return (
    <div>
      <VoiceButton
        status={status}
        onPress={() => setStatus('listening')}
        onRelease={() => setStatus('processing')}
        size="large"
      />
      
      <Button variant="primary" size="lg">
        Get Started
      </Button>
    </div>
  );
}
```

---

## 🎨 Theming System

### Available Themes

The design system includes 5 built-in themes:

1. **Light** (default) - Clean, bright interface
2. **Dark** - Rich blacks with elevated surfaces
3. **High Contrast** - Maximum accessibility
4. **Warm** - Amber-based color palette
5. **Cool** - Indigo-based color palette

### Using Themes

```tsx
// Set theme programmatically
document.documentElement.setAttribute('data-theme', 'dark');

// Themes automatically respect system preference
@media (prefers-color-scheme: dark) {
  // Auto dark mode when no theme set
}
```

### Custom Themes

Create custom themes by overriding CSS variables:

```css
[data-theme="custom"] {
  --primary: #ff6b6b;
  --background: #ffffff;
  --text-primary: #1a1a1a;
  /* ... other tokens ... */
}
```

---

## 📐 Design Tokens

All design decisions are tokenized for consistency:

### Colors

```css
--color-primary-500: #0ea5e9;
--color-success: #10b981;
--color-error: #ef4444;
--text-primary: #111827;
--background: #ffffff;
```

### Spacing (8-point grid)

```css
--space-2: 0.5rem;   /* 8px */
--space-4: 1rem;     /* 16px - base unit */
--space-6: 1.5rem;   /* 24px */
```

### Typography

```css
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--font-display: -apple-system, system-ui;
```

### Sizing

```css
--touch-min: 48px;        /* Minimum touch target */
--icon-base: 24px;
--height-button: 48px;
```

See [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md) for complete token reference.

---

## ♿ Accessibility Features

### WCAG AAA Compliant

- **Color Contrast**: 7:1 for normal text, 4.5:1 for large text
- **Focus Indicators**: 3px visible outline on all interactive elements
- **Keyboard Navigation**: Full keyboard support with logical tab order
- **Screen Readers**: Semantic HTML + ARIA labels

### Accessibility Testing

```bash
# Run accessibility audit
npm run test:a11y

# Test with screen reader
# Enable VoiceOver (Mac): Cmd + F5
# Enable NVDA (Windows): Ctrl + Alt + N
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  /* All animations disabled automatically */
}
```

---

## 📱 Responsive Design

### Breakpoints

```css
--breakpoint-sm: 640px;   /* Large phone */
--breakpoint-md: 768px;   /* Tablet */
--breakpoint-lg: 1024px;  /* Desktop */
```

### Mobile-First Approach

```css
/* Mobile (default) */
.button {
  height: 48px;
  font-size: 16px;
}

/* Tablet and up */
@media (min-width: 768px) {
  .button {
    height: 56px;
    font-size: 18px;
  }
}
```

### Safe Area Support (iOS)

```css
.safe-top {
  padding-top: max(0px, env(safe-area-inset-top));
}

.safe-bottom {
  padding-bottom: max(0px, env(safe-area-inset-bottom));
}
```

---

## 🎭 Animation System

### Motion Principles

1. **Purposeful** - Every animation communicates state
2. **Responsive** - Immediate feedback to user input
3. **Natural** - Follows physics (ease-out for entrance)
4. **Accessible** - Respects `prefers-reduced-motion`

### Timing Functions

```css
--ease-out: cubic-bezier(0, 0, 0.2, 1);      /* Entrances */
--ease-in: cubic-bezier(0.4, 0, 1, 1);       /* Exits */
--ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Durations

```css
--duration-fast: 150ms;    /* Instant feedback */
--duration-base: 250ms;    /* Standard transitions */
--duration-slow: 350ms;    /* Emphasized motion */
```

---

## 🎯 Component Specifications

### Button Sizes

| Size | Height | Padding | Font Size | Use Case |
|------|--------|---------|-----------|----------|
| sm   | 40px   | 16px    | 14px      | Secondary actions |
| base | 48px   | 24px    | 16px      | Default |
| lg   | 56px   | 32px    | 18px      | Primary CTAs |
| xl   | 64px   | 40px    | 20px      | Hero actions |

### Icon Sizes

| Size | Dimension | Use Case |
|------|-----------|----------|
| xs   | 16px      | Inline icons |
| sm   | 20px      | List items |
| base | 24px      | Default |
| md   | 32px      | Feature highlights |
| lg   | 40px      | Large buttons |
| xl   | 48px      | Hero sections |

### Touch Targets

**Minimum**: 48x48px (Apple HIG, WCAG 2.5.5)
**Comfortable**: 56x56px
**Primary Actions**: 64x64px+

---

## 🔘 Voice Button Specifications

The VoiceButton is the centerpiece of the UI:

### States

| State | Visual | Duration |
|-------|--------|----------|
| Idle | Static, primary color | - |
| Listening | Pulsing blue, waveform | While recording |
| Processing | Rotating gradient | 1-3s |
| Speaking | Gentle glow, sound bars | While playing |
| Error | Red, shake animation | 500ms |

### Sizes

- **Base**: 72x72px (mobile)
- **Large**: 80x80px (desktop)

### Accessibility

- Minimum contrast: 4.5:1
- Clear status announcements
- Keyboard operable (Space/Enter)
- Haptic feedback on supported devices

---

## 🎨 Customization Guide

### Change Brand Color

```css
:root {
  --color-primary-500: #your-color;
  /* Other shades auto-generated or manually set */
}
```

### Adjust Spacing Scale

```css
:root {
  --space-unit: 1rem; /* Change base unit */
  --space-4: calc(var(--space-unit) * 4);
}
```

### Custom Typography

```css
:root {
  --font-display: 'Your Display Font', system-ui;
  --font-body: 'Your Body Font', system-ui;
}
```

---

## 📚 Component API Reference

### Button

```tsx
<Button
  variant="primary" | "secondary" | "ghost" | "danger"
  size="sm" | "base" | "lg" | "xl"
  fullWidth={boolean}
  loading={boolean}
  disabled={boolean}
  iconBefore={ReactNode}
  iconAfter={ReactNode}
  iconOnly={ReactNode}
  onClick={Function}
>
  Button Text
</Button>
```

### VoiceButton

```tsx
<VoiceButton
  status="idle" | "listening" | "processing" | "speaking" | "error"
  size="base" | "large"
  onPress={Function}
  onRelease={Function}
  disabled={boolean}
  showWaveform={boolean}
/>
```

---

## 🧪 Testing

### Component Testing

```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Visual regression tests
npm run test:visual
```

### Accessibility Testing

```bash
# Lighthouse CI
npm run lighthouse

# Axe accessibility tests
npm run test:a11y
```

### Browser Testing

Tested on:
- ✅ Chrome 120+
- ✅ Safari 17+
- ✅ Firefox 120+
- ✅ Edge 120+
- ✅ iOS Safari 17+
- ✅ Android Chrome 120+

---

## 📊 Performance

### Metrics

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s
- **Lighthouse Score**: > 95
- **Bundle Size**: < 150KB (gzipped)

### Optimizations

- CSS-only animations (no JS overhead)
- Lazy-loaded components
- Optimized SVG icons
- Minimal external dependencies

---

## 🔧 Development

### File Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── core/           # Basic components
│   │   ├── voice/          # Voice-specific
│   │   ├── navigation/     # Nav components
│   │   └── layout/         # Layout helpers
│   ├── styles/
│   │   ├── tokens.css      # Design tokens
│   │   └── global.css      # Base styles
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Helper functions
│   └── contexts/           # React contexts
├── DESIGN_SYSTEM.md        # Complete design docs
└── README.md               # This file
```

### Adding New Components

1. Create component folder in appropriate category
2. Add `.tsx`, `.css`, and test files
3. Export from index
4. Document in Storybook
5. Add accessibility tests

---

## 🤝 Contributing

### Code Style

- Use TypeScript for type safety
- Follow Airbnb React style guide
- Use CSS Modules for component styles
- Write accessible markup

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-component

# Make changes, test, commit
git add .
git commit -m "feat: add new component"

# Push and create PR
git push origin feature/new-component
```

---

## 📖 Resources

- [Design System Docs](./DESIGN_SYSTEM.md)
- [Accessibility Guide](./ACCESSIBILITY.md)
- [Component Storybook](http://localhost:6006)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/)
- [WCAG 2.2](https://www.w3.org/WAI/WCAG22/quickref/)

---

## 📝 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for exceptional user experiences**
