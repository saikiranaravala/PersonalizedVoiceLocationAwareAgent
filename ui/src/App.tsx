import React, { useState } from 'react';
import VoiceButton from './components/voice/VoiceButton/VoiceButton';
import Button from './components/core/Button/Button';
import './styles/tokens.css';
import './styles/global.css';
import './App.css';

/**
 * Main App Component
 * 
 * Demonstrates the complete voice-first UI
 * - Theme switching
 * - Voice interaction
 * - Responsive layout
 * - Accessibility features
 */

type Theme = 'light' | 'dark' | 'high-contrast';
type VoiceStatus = 'idle' | 'listening' | 'processing' | 'speaking' | 'error';

function App() {
  const [theme, setTheme] = useState<Theme>('light');
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>('idle');
  const [conversation, setConversation] = useState<
    Array<{ role: 'user' | 'assistant'; text: string; timestamp: Date }>
  >([]);

  // Apply theme to document
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Handle voice button press
  const handleVoicePress = () => {
    setVoiceStatus('listening');
    
    // Simulate voice recognition
    setTimeout(() => {
      setVoiceStatus('processing');
      
      // Add user message
      const userMessage = "What's the weather like?";
      setConversation(prev => [
        ...prev,
        { role: 'user', text: userMessage, timestamp: new Date() },
      ]);
      
      setTimeout(() => {
        setVoiceStatus('speaking');
        
        // Add assistant response
        const assistantMessage = "Current weather in New York: Clear sky, 72°F";
        setConversation(prev => [
          ...prev,
          { role: 'assistant', text: assistantMessage, timestamp: new Date() },
        ]);
        
        setTimeout(() => {
          setVoiceStatus('idle');
        }, 2000);
      }, 1500);
    }, 2000);
  };

  const handleVoiceRelease = () => {
    // Handle release if needed
  };

  const cycleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'high-contrast'];
    const currentIndex = themes.indexOf(theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  return (
    <div className="app">
      {/* Skip to main content */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Header */}
      <header className="app-header safe-top">
        <div className="container">
          <div className="app-header__content">
            <h1 className="app-header__title">Voice Assistant</h1>
            
            <div className="app-header__actions">
              {/* Theme switcher */}
              <Button
                variant="ghost"
                size="base"
                iconOnly={<ThemeIcon />}
                onClick={cycleTheme}
                aria-label={`Current theme: ${theme}. Click to change theme`}
              />
              
              {/* Settings */}
              <Button
                variant="ghost"
                size="base"
                iconOnly={<SettingsIcon />}
                aria-label="Open settings"
              />
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
                  Tap the microphone to start
                </h2>
                <p className="empty-state__description">
                  I can help you with weather, restaurants, rides, and more
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
          <div className="voice-control">
            <VoiceButton
              status={voiceStatus}
              onPress={handleVoicePress}
              onRelease={handleVoiceRelease}
              size="large"
              showWaveform={true}
            />
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <Button
              variant="secondary"
              size="sm"
              iconBefore={<WeatherIcon />}
            >
              Weather
            </Button>
            <Button
              variant="secondary"
              size="sm"
              iconBefore={<RestaurantIcon />}
            >
              Restaurants
            </Button>
            <Button
              variant="secondary"
              size="sm"
              iconBefore={<CarIcon />}
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
const StatusIndicator: React.FC<{ status: VoiceStatus }> = ({ status }) => {
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

const SettingsIcon = () => (
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
    <circle cx="12" cy="12" r="3" />
    <path d="M12 1v6m0 6v6m-6-6H0m6 0h6m6 0h6" />
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
