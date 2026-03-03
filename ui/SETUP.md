# Quick Setup Guide - UI

## Installation Fix Applied ✅

The Storybook dependency conflict has been resolved. Follow these steps:

## Step 1: Install Dependencies

```bash
cd ui
npm install
```

If you still encounter issues, use:
```bash
npm install --legacy-peer-deps
```

## Step 2: Start Development Server

```bash
npm run dev
```

The app will be available at: `http://localhost:5173`

## Step 3: View the Demo

Open your browser and you'll see:
- Voice button in the center
- Theme switcher in top-right
- Empty state with instructions
- Quick action buttons at bottom

## What's Working

✅ All components render correctly
✅ Theme switching (light/dark/high-contrast)
✅ Voice button animations
✅ Responsive layout
✅ Accessibility features

## What's Next (Backend Integration)

To connect to the Python backend:

1. **Create API Server** (see `INTEGRATION_GUIDE.md`)
2. **Start Backend**: `python api_server.py`
3. **Start Frontend**: `npm run dev`
4. Both will communicate via REST/WebSocket

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Check TypeScript types
```

## Project Structure

```
ui/
├── index.html                 # Entry HTML
├── vite.config.ts             # Vite configuration
├── tsconfig.json              # TypeScript config
├── package.json               # Dependencies
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main app component
│   ├── App.css               # App styles
│   ├── components/           # React components
│   │   ├── core/
│   │   │   └── Button/
│   │   └── voice/
│   │       └── VoiceButton/
│   └── styles/
│       ├── tokens.css        # Design tokens
│       └── global.css        # Global styles
└── README.md                 # Full documentation
```

## Troubleshooting

### Port Already in Use

```bash
# Kill the process on port 5173
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5173 | xargs kill -9
```

### TypeScript Errors

```bash
# Check for type errors
npm run type-check

# Reinstall if needed
rm -rf node_modules package-lock.json
npm install
```

### Styles Not Loading

Make sure these files exist:
- `src/styles/tokens.css`
- `src/styles/global.css`

They're imported in `src/main.tsx`.

## Next Steps

1. ✅ Run `npm install`
2. ✅ Run `npm run dev`
3. ✅ Open `http://localhost:5173`
4. 📖 Read `INTEGRATION_GUIDE.md` for backend setup
5. 🎨 Customize theme colors in `src/styles/tokens.css`

## Documentation

- **README.md** - Complete UI documentation
- **DESIGN_SYSTEM.md** - Design specifications
- **INTEGRATION_GUIDE.md** - Backend integration
- **This file** - Quick setup

---

**Need Help?**
- Check `README.md` for detailed documentation
- Review `INTEGRATION_GUIDE.md` for backend setup
- All components are fully documented with TypeScript interfaces

**You're all set!** 🚀
