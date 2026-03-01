import React, { useState } from 'react';
import VoiceButton from './components/voice/VoiceButton/VoiceButton';
import Button from './components/core/Button/Button';
import { useVoiceAssistant } from './hooks/useVoiceAssistant';
import './styles/tokens.css';
import './styles/global.css';
import './App.css';

/**
 * Main App Component
 * 
 * Voice-first AI Assistant UI connected to backend
 * - Real-time voice interaction
 * - WebSocket communication
 * - Speech recognition & synthesis
 * - Theme switching
 * - Responsive layout
 */

type Theme = 'light' | 'dark' | 'high-contrast';

function App() {
  const [theme, setTheme] = useState<Theme>('light');

  // Connect to backend voice assistant
  const {
    status: voiceStatus,
    conversation,
    isConnected,
    error,
    startListening,
    stopListening,
    sendTextMessage,
    clearConversation,
    reconnect,
  } = useVoiceAssistant({
    backendUrl: 'ws://localhost:8000',
    autoConnect: true,
    enableSpeechRecognition: true,
    enableSpeechSynthesis: true,
  });

  // Apply theme to document
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Handle voice button press
  const handleVoicePress = () => {
    if (!isConnected) {
      alert('Backend not connected. Please start the backend server: python api_server.py');
      return;
    }
    console.log('[App] Voice button pressed - starting listening');
    startListening();
  };

  const handleVoiceRelease = () => {
    // Stop listening when button is released
    console.log('[App] Voice button released - stopping listening');
    stopListening();
  };

  const cycleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'high-contrast'];
    const currentIndex = themes.indexOf(theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  // Quick action handlers
  const handleQuickAction = (action: string) => {
    if (!isConnected) {
      alert('Backend not connected. Please start the backend server.');
      return;
    }

    const messages: Record<string, string> = {
      weather: "What's the weather like?",
      restaurants: "Find restaurants near me",
      ride: "Book me a ride"
    };

    sendTextMessage(messages[action] || action);
  };

  return (
    <div className="app">
      {/* Skip to main content */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Connection Status Banner */}
      {!isConnected && (
        <div className="connection-banner" role="alert">
          <div className="container">
            <div className="connection-banner__content">
              <span className="connection-banner__icon">⚠️</span>
              <span className="connection-banner__text">
                Not connected to backend. Please start the server: <code>python api_server.py</code>
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={reconnect}
              >
                Retry
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
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

      {/* Header */}
      <header className="app-header safe-top">
        <div className="container">
          <div className="app-header__content">
            <h1 className="app-header__title">
              Voice Assistant
              {isConnected && <span className="connection-dot" title="Connected" />}
            </h1>
            
            <div className="app-header__actions">
              {/* Theme switcher */}
              <Button
                variant="ghost"
                size="base"
                iconOnly={<ThemeIcon />}
                onClick={cycleTheme}
                aria-label={`Current theme: ${theme}. Click to change theme`}
              />
              
              {/* Clear conversation */}
              {conversation.length > 0 && (
                <Button
                  variant="ghost"
                  size="base"
                  iconOnly={<ClearIcon />}
                  onClick={clearConversation}
                  aria-label="Clear conversation"
                />
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="app-main">
        <div className="container">
          {/* Conversation Area */}
          <div className="conversation-area">
            {conversation.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state__icon">
                  <MicrophoneIcon />
                </div>
                <h2 className="empty-state__title">
                  {isConnected ? 'Tap the microphone to start' : 'Waiting for backend connection...'}
                </h2>
                <p className="empty-state__description">
                  {isConnected 
                    ? 'I can help you with weather, restaurants, rides, and more'
                    : 'Start the backend server to begin: python api_server.py'
                  }
                </p>
              </div>
            ) : (
              <div className="conversation-list">
                {conversation.map((message, index) => (
                  <div
                    key={index}
                    className={`conversation-bubble conversation-bubble--${message.role}`}
                  >
                    <div className="conversation-bubble__content">
                      {message.text}
                    </div>
                    <div className="conversation-bubble__timestamp">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Voice Status Indicator */}
          {voiceStatus !== 'idle' && (
            <div className="status-indicator" role="status" aria-live="polite">
              <StatusIndicator status={voiceStatus} />
            </div>
          )}
        </div>
      </main>

      {/* Bottom Action Area */}
      <div className="app-bottom safe-bottom">
        <div className="container">
          {/* Voice control with instructions */}
          <div className="voice-control">
            {/* Push-to-talk instruction */}
            {voiceStatus === 'idle' && (
              <p className="voice-instruction">
                Hold to talk, release to send
              </p>
            )}
            
            {/* Status text when active */}
            {voiceStatus !== 'idle' && (
              <p className="voice-instruction voice-instruction--active">
                {voiceStatus === 'listening' && 'Listening... Release when done'}
                {voiceStatus === 'processing' && 'Processing your request...'}
                {voiceStatus === 'speaking' && 'Speaking response...'}
                {voiceStatus === 'error' && 'Error occurred'}
              </p>
            )}
            
            <VoiceButton
              status={voiceStatus}
              onPress={handleVoicePress}
              onRelease={handleVoiceRelease}
              size="large"
              showWaveform={true}
              disabled={!isConnected}
            />
            
            {/* Manual stop button when listening */}
            {voiceStatus === 'listening' && (
              <Button
                variant="secondary"
                size="base"
                onClick={handleVoiceRelease}
                style={{ marginTop: 'var(--space-4)' }}
              >
                Stop & Send
              </Button>
            )}
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <Button
              variant="secondary"
              size="sm"
              iconBefore={<WeatherIcon />}
              onClick={() => handleQuickAction('weather')}
              disabled={!isConnected}
            >
              Weather
            </Button>
            <Button
              variant="secondary"
              size="sm"
              iconBefore={<RestaurantIcon />}
              onClick={() => handleQuickAction('restaurants')}
              disabled={!isConnected}
            >
              Restaurants
            </Button>
            <Button
              variant="secondary"
              size="sm"
              iconBefore={<CarIcon />}
              onClick={() => handleQuickAction('ride')}
              disabled={!isConnected}
            >
              Ride
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Status Indicator Component
const StatusIndicator: React.FC<{ status: string }> = ({ status }) => {
  const getStatusText = () => {
    switch (status) {
      case 'listening':
        return 'Listening...';
      case 'processing':
        return 'Processing your request...';
      case 'speaking':
        return 'Speaking...';
      case 'error':
        return 'Something went wrong';
      default:
        return '';
    }
  };

  return (
    <div className={`status-indicator__content status-indicator--${status}`}>
      <div className="status-indicator__dot" />
      <span className="status-indicator__text">{getStatusText()}</span>
    </div>
  );
};

// Icon Components
const ThemeIcon = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);

const ClearIcon = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  </svg>
);

const MicrophoneIcon = () => (
  <svg
    width="64"
    height="64"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
);

const WeatherIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
    <path d="M12 2v2m0 16v2m10-10h-2M4 12H2m15.07 7.07l-1.41-1.41M8.34 8.34L6.93 6.93" />
    <circle cx="12" cy="12" r="5" />
  </svg>
);

const RestaurantIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
    <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7" />
  </svg>
);

const CarIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
    <path d="M5 11l1.5-4.5h11L19 11m-1 3h.01M6 14h.01M5 17h14a2 2 0 0 0 2-2v-5H3v5a2 2 0 0 0 2 2Z" />
    <circle cx="7" cy="14" r="1" />
    <circle cx="17" cy="14" r="1" />
  </svg>
);

export default App;
