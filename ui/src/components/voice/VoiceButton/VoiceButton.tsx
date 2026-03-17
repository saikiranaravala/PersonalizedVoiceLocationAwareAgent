import React, { useRef, useState } from 'react';
import './VoiceButton.css';

/**
 * VoiceButton Component
 * 
 * The primary interaction point for the voice assistant
 * Features:
 * - Large, accessible touch target (72x72px)
 * - Visual feedback for voice states
 * - Animated pulse effect when active
 * - Waveform visualization
 * - Haptic feedback integration
 */

export interface VoiceButtonProps {
  /** Current voice state */
  status?: 'idle' | 'listening' | 'processing' | 'speaking' | 'error';
  
  /** Callback when button is pressed */
  onPress?: () => void;
  
  /** Callback when button is released */
  onRelease?: () => void;
  
  /** Disabled state */
  disabled?: boolean;
  
  /** Show visual waveform */
  showWaveform?: boolean;
  
  /** Size variant */
  size?: 'base' | 'large';
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({
  status = 'idle',
  onPress,
  onRelease,
  disabled = false,
  showWaveform = true,
  size = 'large',
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Haptic feedback (if supported)
  const triggerHaptic = () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
    
    // iOS Taptic Engine (requires webkit)
    if ((window as any).webkit?.messageHandlers?.haptic) {
      (window as any).webkit.messageHandlers.haptic.postMessage('light');
    }
  };

  const handlePointerDown = () => {
    if (disabled) return;
    
    setIsPressed(true);
    triggerHaptic();
    onPress?.();
  };

  const handlePointerUp = () => {
    if (disabled) return;
    
    setIsPressed(false);
    onRelease?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handlePointerDown();
    }
  };

  const handleKeyUp = (e: React.KeyboardEvent) => {
    if (disabled) return;
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handlePointerUp();
    }
  };

  // Generate waveform bars based on status
  const generateWaveformBars = () => {
    const barCount = size === 'large' ? 5 : 3;
    return Array.from({ length: barCount }, (_, i) => (
      <div
        key={i}
        className="voice-button__waveform-bar"
        style={{
          animationDelay: `${i * 0.1}s`,
        }}
      />
    ));
  };

  const buttonClasses = [
    'voice-button',
    `voice-button--${size}`,
    `voice-button--${status}`,
    isPressed && 'voice-button--pressed',
    disabled && 'voice-button--disabled',
  ]
    .filter(Boolean)
    .join(' ');

  // Get icon and label based on status
  const getButtonContent = () => {
    switch (status) {
      case 'listening':
        return {
          icon: <MicrophoneIcon />,
          label: 'Listening...',
          ariaLabel: 'Listening to your voice. Release to stop.',
        };
      case 'processing':
        return {
          icon: <ProcessingIcon />,
          label: 'Processing...',
          ariaLabel: 'Processing your request',
        };
      case 'speaking':
        return {
          icon: <SpeakerIcon />,
          label: 'Speaking...',
          ariaLabel: 'Assistant is speaking',
        };
      case 'error':
        return {
          icon: <ErrorIcon />,
          label: 'Error',
          ariaLabel: 'Error occurred. Tap to try again.',
        };
      default:
        return {
          icon: <MicrophoneIcon />,
          label: 'Tap to speak',
          ariaLabel: 'Tap and hold to speak',
        };
    }
  };

  const content = getButtonContent();

  return (
    <div className="voice-button-container">
      {/* Pulse rings for visual feedback */}
      {(status === 'listening' || status === 'speaking') && (
        <>
          <div className="voice-button__pulse voice-button__pulse--1" />
          <div className="voice-button__pulse voice-button__pulse--2" />
          <div className="voice-button__pulse voice-button__pulse--3" />
        </>
      )}

      <button
        ref={buttonRef}
        className={buttonClasses}
        disabled={disabled}
        aria-label={content.ariaLabel}
        aria-live="polite"
        aria-pressed={isPressed}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        onKeyDown={handleKeyDown}
        onKeyUp={handleKeyUp}
        type="button"
      >
        {/* Icon */}
        <div className="voice-button__icon">{content.icon}</div>

        {/* Waveform visualization */}
        {showWaveform && status === 'listening' && (
          <div className="voice-button__waveform">
            {generateWaveformBars()}
          </div>
        )}

        {/* Processing spinner */}
        {status === 'processing' && (
          <div className="voice-button__spinner" />
        )}
      </button>

      {/* Status label */}
      <div className="voice-button-label" aria-hidden="true">
        {content.label}
      </div>
    </div>
  );
};

// Icon components (inline SVG for better control)
const MicrophoneIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
);

const ProcessingIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
    <polyline points="7.5 4.21 12 6.81 16.5 4.21" />
    <polyline points="7.5 19.79 7.5 14.6 3 12" />
    <polyline points="21 12 16.5 14.6 16.5 19.79" />
    <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
    <line x1="12" y1="22.08" x2="12" y2="12" />
  </svg>
);

const SpeakerIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
  </svg>
);

const ErrorIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

export default VoiceButton;
