import React, { useState, useEffect, useRef, useCallback } from 'react';
import VoiceButton from './components/voice/VoiceButton/VoiceButton';
import Button from './components/core/Button/Button';
import { useVoiceAssistant } from './hooks/useVoiceAssistant';
import { useUserProfile } from './hooks/useUserProfile';
import { ProfileSetup } from './components/ProfileSetup/ProfileSetup';
import { ProfileSettings } from './components/ProfileSettings/ProfileSettings';
import './styles/tokens.css';
import './styles/global.css';
import './App.css';

type Theme = 'light' | 'dark' | 'high-contrast';
type ChatWindowState = 'minimized' | 'default' | 'maximized';

// Drag state type
interface DragState {
  isDragging: boolean;
  startX: number;
  startY: number;
  startLeft: number;
  startTop: number;
}

// Resize state type
interface ResizeState {
  isResizing: boolean;
  startX: number;
  startY: number;
  startWidth: number;
  startHeight: number;
}

function App() {
  const [theme, setTheme] = useState<Theme>('light');
  const [chatWindowState, setChatWindowState] = useState<ChatWindowState>('default');
  const [chatPosition, setChatPosition] = useState({ left: -1, top: -1 }); // -1 = use CSS default
  const [chatSize, setChatSize] = useState({ width: 380, height: 480 });
  const dragState = useRef<DragState>({ isDragging: false, startX: 0, startY: 0, startLeft: 0, startTop: 0 });
  const resizeState = useRef<ResizeState>({ isResizing: false, startX: 0, startY: 0, startWidth: 0, startHeight: 0 });
  const chatWindowRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textInputRef = useRef<HTMLInputElement>(null);

  const {
    isProfileSetup, profile, getGreeting, updateProfile, resetUserData,
  } = useUserProfile();

  const {
    status: voiceStatus, conversation, isConnected, isConnecting, error,
    startListening, stopListening, stopSpeaking, sendTextMessage,
    clearConversation, reconnect,
  } = useVoiceAssistant({
    backendUrl: 'ws://localhost:8000',
    autoConnect: true,
    enableSpeechRecognition: true,
    enableSpeechSynthesis: true,
    userProfile: profile,
  });

  const [showProfileSetup, setShowProfileSetup] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  const [textInput, setTextInput] = useState('');

  useEffect(() => {
    if (!isProfileSetup) {
      const timer = setTimeout(() => setShowProfileSetup(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [isProfileSetup]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  // Keyboard shortcut: Escape stops speaking
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && voiceStatus === 'speaking') stopSpeaking();
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [voiceStatus, stopSpeaking]);

  const cycleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'high-contrast'];
    setTheme(themes[(themes.indexOf(theme) + 1) % themes.length]);
  };

  const handleQuickAction = (action: string) => {
    if (!isConnected) return;
    const messages: Record<string, string> = {
      weather: "What's the weather like?",
      restaurants: "Find restaurants near me",
      ride: "Book me a ride",
    };
    sendTextMessage(messages[action] || action);
  };

  const handleTextSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!textInput.trim() || !isConnected) return;
    sendTextMessage(textInput);
    setTextInput('');
  };

  const handleTextKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleTextSubmit(); }
  };

  const handleVoicePress = () => {
    if (!isConnected) return;
    startListening();
  };

  const handleVoiceRelease = () => stopListening();

  // ── DRAG ──────────────────────────────────────────────────────
  const startDrag = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (chatWindowState === 'maximized') return;
    const rect = chatWindowRef.current!.getBoundingClientRect();
    dragState.current = {
      isDragging: true,
      startX: e.clientX, startY: e.clientY,
      startLeft: rect.left, startTop: rect.top,
    };
    e.currentTarget.setPointerCapture(e.pointerId);
  }, [chatWindowState]);

  const onDragMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (!dragState.current.isDragging) return;
    const dx = e.clientX - dragState.current.startX;
    const dy = e.clientY - dragState.current.startY;
    const newLeft = Math.max(0, Math.min(window.innerWidth - chatSize.width, dragState.current.startLeft + dx));
    const newTop = Math.max(0, Math.min(window.innerHeight - 60, dragState.current.startTop + dy));
    setChatPosition({ left: newLeft, top: newTop });
  }, [chatSize.width]);

  const endDrag = useCallback(() => {
    dragState.current.isDragging = false;
  }, []);

  // ── RESIZE ────────────────────────────────────────────────────
  const startResize = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    e.stopPropagation();
    resizeState.current = {
      isResizing: true,
      startX: e.clientX, startY: e.clientY,
      startWidth: chatSize.width, startHeight: chatSize.height,
    };
    e.currentTarget.setPointerCapture(e.pointerId);
  }, [chatSize]);

  const onResizeMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (!resizeState.current.isResizing) return;
    const dx = e.clientX - resizeState.current.startX;
    const dy = e.clientY - resizeState.current.startY;
    setChatSize({
      width: Math.max(300, Math.min(720, resizeState.current.startWidth + dx)),
      height: Math.max(360, Math.min(800, resizeState.current.startHeight + dy)),
    });
  }, []);

  const endResize = useCallback(() => {
    resizeState.current.isResizing = false;
  }, []);

  const toggleMinimize = () => {
    setChatWindowState(s => s === 'minimized' ? 'default' : 'minimized');
  };

  const toggleMaximize = () => {
    setChatWindowState(s => s === 'maximized' ? 'default' : 'maximized');
  };

  // Compute chat window styles
  const chatWindowStyle: React.CSSProperties = (() => {
    if (chatWindowState === 'maximized') return {};
    const style: React.CSSProperties = {};
    if (chatPosition.left !== -1) { style.left = chatPosition.left; style.top = chatPosition.top; style.right = 'auto'; style.bottom = 'auto'; }
    if (chatWindowState !== 'minimized') {
      style.width = chatSize.width;
      style.height = chatSize.height;
    }
    return style;
  })();

  const linkifyText = (text: string) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.split(urlRegex).map((part, i) =>
      urlRegex.test(part)
        ? <a key={i} href={part} target="_blank" rel="noopener noreferrer" className="message-link">[click here]</a>
        : part
    );
  };

  return (
    <div className="app">
      <a href="#main-content" className="skip-link">Skip to main content</a>

      {/* ── STATUS BANNERS ── */}
      {!isConnected && !isConnecting && (
        <div className="connection-banner" role="alert">
          <div className="container">
            <div className="connection-banner__content">
              <span className="connection-banner__icon">⚠️</span>
              <span className="connection-banner__text">
                Not connected. Start: <code>python api_server.py</code>
              </span>
              <Button variant="ghost" size="sm" onClick={reconnect}>Retry</Button>
            </div>
          </div>
        </div>
      )}
      {isConnecting && (
        <div className="connecting-banner" role="status">
          <div className="container">
            <div className="connecting-banner__content">
              <span className="connecting-banner__icon">🔄</span>
              <span className="connecting-banner__text">Connecting to backend...</span>
            </div>
          </div>
        </div>
      )}
      {error && (
        <div className="error-banner" role="alert">
          <div className="container">
            <div className="error-banner__content">
              <span className="error-banner__icon">❌</span>
              <span className="error-banner__text">{error}</span>
            </div>
          </div>
        </div>
      )}

      {/* ── HEADER ── */}
      <header className="app-header safe-top">
        <div className="container">
          <div className="app-header__content">
            <h1 className="app-header__title">
              Voice Assistant
              {isConnected && <span className="connection-dot" title="Connected" />}
            </h1>
            <div className="app-header__actions">
              <Button variant="ghost" size="sm" iconOnly={<ThemeIcon />} onClick={cycleTheme} aria-label={`Theme: ${theme}`} />
              {conversation.length > 0 && (
                <Button variant="ghost" size="sm" iconOnly={<ClearIcon />} onClick={clearConversation} aria-label="Clear conversation" />
              )}
            </div>
          </div>
        </div>
      </header>

      {/* ── MAIN HISTORY AREA ── */}
      <main id="main-content" className="app-main">
        <div className="container">
          <div className="conversation-area">
            {conversation.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state__icon"><EmptyStateIcon /></div>
                <h2 className="empty-state__title">
                  {isConnected
                    ? (isProfileSetup ? getGreeting() : 'Use the chat window below')
                    : 'Waiting for backend...'}
                </h2>
                <p className="empty-state__description">
                  {isConnected
                    ? 'Type or speak — I can help with weather, restaurants, rides & more'
                    : 'Start the backend server: python api_server.py'}
                </p>
                {isProfileSetup && profile && (
                  <button onClick={() => setShowProfileSettings(true)} className="edit-profile-link">Edit Profile</button>
                )}
              </div>
            ) : (
              <div className="conversation-list">
                {conversation.map((message, index) => (
                  <div key={index} className={`conversation-bubble conversation-bubble--${message.role}`}>
                    <div className="conversation-bubble__content">{linkifyText(message.text)}</div>
                    <div className="conversation-bubble__timestamp">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>
      </main>

      {/* ── FLOATING CHAT WINDOW ── */}
      <div
        ref={chatWindowRef}
        className={`chat-window chat-window--${chatWindowState}`}
        style={chatWindowStyle}
        role="complementary"
        aria-label="Chat input window"
      >
        {/* Title bar — draggable */}
        <div
          className="chat-window__titlebar"
          onPointerDown={startDrag}
          onPointerMove={onDragMove}
          onPointerUp={endDrag}
        >
          <div className="chat-window__titlebar-info">
            {voiceStatus !== 'idle' && (
              <span className={`chat-window__status-dot chat-window__status-dot--${voiceStatus}`} />
            )}
            <span className="chat-window__title">
              {voiceStatus === 'listening' ? 'Listening…'
                : voiceStatus === 'processing' ? 'Processing…'
                : voiceStatus === 'speaking' ? 'Speaking…'
                : 'Chat'}
            </span>
          </div>
          <div className="chat-window__controls">
            <button
              className="chat-window__ctrl chat-window__ctrl--minimize"
              onClick={toggleMinimize}
              aria-label={chatWindowState === 'minimized' ? 'Restore chat' : 'Minimize chat'}
              title={chatWindowState === 'minimized' ? 'Restore' : 'Minimize'}
            >
              <MinimizeIcon />
            </button>
            <button
              className="chat-window__ctrl chat-window__ctrl--maximize"
              onClick={toggleMaximize}
              aria-label={chatWindowState === 'maximized' ? 'Restore chat size' : 'Maximize chat'}
              title={chatWindowState === 'maximized' ? 'Restore' : 'Maximize'}
            >
              {chatWindowState === 'maximized' ? <RestoreIcon /> : <MaximizeIcon />}
            </button>
          </div>
        </div>

        {/* Body — hidden when minimized */}
        {chatWindowState !== 'minimized' && (
          <div className="chat-window__body">
            {/* Quick actions */}
            <div className="chat-window__quickactions">
              <button className="chat-window__qa-btn" onClick={() => handleQuickAction('weather')} disabled={!isConnected}>
                <WeatherIcon /> <span>Weather</span>
              </button>
              <button className="chat-window__qa-btn" onClick={() => handleQuickAction('restaurants')} disabled={!isConnected}>
                <RestaurantIcon /> <span>Restaurants</span>
              </button>
              <button className="chat-window__qa-btn" onClick={() => handleQuickAction('ride')} disabled={!isConnected}>
                <CarIcon /> <span>Ride</span>
              </button>
            </div>

            {/* Input row */}
            <form className="chat-window__inputrow" onSubmit={handleTextSubmit}>
              {/* Mic button — inline, compact */}
              <div className="chat-window__mic-wrap">
                <VoiceButton
                  status={voiceStatus}
                  onPress={handleVoicePress}
                  onRelease={handleVoiceRelease}
                  size="base"
                  showWaveform={false}
                  disabled={!isConnected}
                />
              </div>

              {/* Text input */}
              <input
                ref={textInputRef}
                type="text"
                className="chat-window__textinput"
                placeholder={
                  !isConnected ? 'Not connected…'
                    : voiceStatus === 'listening' ? 'Listening…'
                    : voiceStatus === 'processing' ? 'Processing…'
                    : 'Type a message…'
                }
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyDown={handleTextKeyDown}
                disabled={!isConnected || voiceStatus === 'processing'}
                aria-label="Type your message"
                autoComplete="off"
              />

              {/* Send button */}
              <button
                type="submit"
                className="chat-window__sendbtn"
                disabled={!isConnected || !textInput.trim() || voiceStatus === 'processing'}
                aria-label="Send message"
              >
                <SendIcon />
              </button>
            </form>

            {/* Voice status hints */}
            {voiceStatus === 'listening' && (
              <div className="chat-window__voice-hint">
                <span>Release mic to send</span>
                <button className="chat-window__stop-btn" onClick={handleVoiceRelease}>Stop & Send</button>
              </div>
            )}
            {voiceStatus === 'speaking' && (
              <div className="chat-window__voice-hint">
                <span>Speaking response…</span>
                <button className="chat-window__stop-btn" onClick={stopSpeaking}>🔇 Stop</button>
              </div>
            )}
          </div>
        )}

        {/* Resize handle — bottom-right corner */}
        {chatWindowState === 'default' && (
          <div
            className="chat-window__resize-handle"
            onPointerDown={startResize}
            onPointerMove={onResizeMove}
            onPointerUp={endResize}
            aria-label="Resize chat window"
          >
            <ResizeIcon />
          </div>
        )}
      </div>

      {/* ── MODALS ── */}
      {showProfileSetup && !isProfileSetup && (
        <ProfileSetup
          onComplete={(p) => { updateProfile(p); setShowProfileSetup(false); }}
          onSkip={() => setShowProfileSetup(false)}
        />
      )}
      {showProfileSettings && isProfileSetup && profile && (
        <ProfileSettings
          profile={profile}
          onUpdate={updateProfile}
          onReset={() => { resetUserData(); setShowProfileSettings(false); setTimeout(() => setShowProfileSetup(true), 500); }}
          onClose={() => setShowProfileSettings(false)}
        />
      )}
    </div>
  );
}

// ── ICON COMPONENTS ──────────────────────────────────────────────────────────

const ThemeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);

const ClearIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  </svg>
);

const EmptyStateIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const SendIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const MinimizeIcon = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
    <rect x="1" y="5.5" width="10" height="1.5" rx="0.75" />
  </svg>
);

const MaximizeIcon = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="1" y="1" width="10" height="10" rx="1.5" />
  </svg>
);

const RestoreIcon = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="3" y="1" width="8" height="8" rx="1" />
    <path d="M1 4v6a1 1 0 0 0 1 1h6" />
  </svg>
);

const ResizeIcon = () => (
  <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
    <line x1="9" y1="1" x2="1" y2="9" />
    <line x1="9" y1="5" x2="5" y2="9" />
  </svg>
);

const WeatherIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);

const RestaurantIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7" />
  </svg>
);

const CarIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M5 11l1.5-4.5h11L19 11m-1 3h.01M6 14h.01M5 17h14a2 2 0 0 0 2-2v-3H3v3a2 2 0 0 0 2 2Z" />
  </svg>
);

export default App;
