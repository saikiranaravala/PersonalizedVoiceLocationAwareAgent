/**
 * useVoiceAssistant Hook
 * Manages voice interaction with the backend
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketClient, Message } from '../api/client';

export type VoiceStatus = 'idle' | 'listening' | 'processing' | 'speaking' | 'error';

export interface ConversationMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
}

export interface ActionPayload {
  action: string;   // e.g. 'save_restaurant', 'save_uber_trip', 'update_preference'
  data: Record<string, any>;
}

export interface UseVoiceAssistantOptions {
  backendUrl?: string;
  sessionId?: string;
  autoConnect?: boolean;
  enableSpeechRecognition?: boolean;
  enableSpeechSynthesis?: boolean;
  userProfile?: any;
  /** Called whenever the backend sends a structured action message */
  onAction?: (payload: ActionPayload) => void;
}

export function useVoiceAssistant(options: UseVoiceAssistantOptions = {}) {
  const {
    backendUrl = 'ws://localhost:8000',
    sessionId,
    autoConnect = true,
    enableSpeechRecognition = true,
    enableSpeechSynthesis = true,
    userProfile,
    onAction,
  } = options;

  // Keep onAction in a ref so handleBackendMessage always sees the latest version
  const onActionRef = useRef(onAction);
  useEffect(() => { onActionRef.current = onAction; }, [onAction]);

  // Use ref to track latest userProfile value (updates when profile changes)
  const userProfileRef = useRef(userProfile);
  
  // Update ref when userProfile changes
  useEffect(() => {
    userProfileRef.current = userProfile;
    console.log('[Voice Assistant] User profile updated:', userProfile);
  }, [userProfile]);

  const [status, setStatus] = useState<VoiceStatus>('idle');
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasConnectedOnce, setHasConnectedOnce] = useState(false);

  const wsClient = useRef<WebSocketClient | null>(null);
  const recognitionRef = useRef<any>(null);
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null);

  /**
   * Initialize WebSocket connection
   */
  useEffect(() => {
    if (!autoConnect) return;

    console.log('[Voice Assistant] Initializing WebSocket...');
    setIsConnecting(true);
    
    wsClient.current = new WebSocketClient(backendUrl, sessionId);

    wsClient.current.onOpen = () => {
      console.log('[Voice Assistant] Connected to backend');
      console.log('[Voice Assistant] WebSocket ready state:', wsClient.current?.isConnected());
      setIsConnected(true);
      setIsConnecting(false);
      setHasConnectedOnce(true);
      setError(null);
    };

    wsClient.current.onClose = () => {
      console.log('[Voice Assistant] Disconnected from backend');
      console.log('[Voice Assistant] WebSocket ready state:', wsClient.current?.isConnected());
      setIsConnected(false);
      setIsConnecting(false);
    };

    wsClient.current.onError = (error) => {
      console.error('[Voice Assistant] Connection error:', error);
      
      // Only show error if we've never connected, or if we had a connection that dropped
      if (hasConnectedOnce) {
        setError('Connection lost. Attempting to reconnect...');
      } else {
        // First connection attempt - show user-friendly message after a delay
        setTimeout(() => {
          if (!wsClient.current?.isConnected()) {
            setError('Failed to connect to backend. Make sure the server is running on port 8000.');
          }
        }, 2000); // Wait 2 seconds before showing error
      }
      
      setIsConnected(false);
      setIsConnecting(false);
    };

    wsClient.current.onMessage = handleBackendMessage;

    wsClient.current.connect();

    return () => {
      if (wsClient.current) {
        wsClient.current.disconnect();
      }
    };
  }, [backendUrl, sessionId, autoConnect, hasConnectedOnce]);

  /**
   * Initialize Speech Recognition (Web Speech API)
   */
  useEffect(() => {
    if (!enableSpeechRecognition) return;

    // Check if browser supports Speech Recognition
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('[Voice Assistant] Speech Recognition not supported in this browser');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      console.log('[Voice Recognition] Started listening');
      setStatus('listening');
      setError(null);
      
      // Set a timeout to prevent stuck listening state
      const timeoutId = setTimeout(() => {
        if (recognitionRef.current) {
          console.warn('[Voice Recognition] Timeout - stopping recognition');
          try {
            recognitionRef.current.stop();
          } catch (e) {
            console.error('[Voice Recognition] Error stopping:', e);
          }
          setStatus('idle');
          setError('Listening timeout. Please try again.');
          setTimeout(() => setError(null), 3000);
        }
      }, 10000); // 10 second timeout
      
      // Store timeout ID to clear it later
      (recognitionRef.current as any).timeoutId = timeoutId;
    };

    recognition.onresult = (event: any) => {
      // Clear timeout if we got a result
      if ((recognitionRef.current as any).timeoutId) {
        clearTimeout((recognitionRef.current as any).timeoutId);
      }
      
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;
      console.log('[Voice Recognition] Transcript:', transcript);
      console.log('[Voice Recognition] Confidence:', confidence);
      
      if (!transcript || transcript.trim().length === 0) {
        console.warn('[Voice Recognition] Empty transcript');
        setStatus('idle');
        return;
      }
      
      // Add user message to conversation
      addUserMessage(transcript);
      
      // Send to backend - this will set status to processing
      sendToBackend(transcript);
    };

    recognition.onerror = (event: any) => {
      // Clear timeout on error
      if ((recognitionRef.current as any).timeoutId) {
        clearTimeout((recognitionRef.current as any).timeoutId);
      }
      
      console.error('[Voice Recognition] Error:', event.error);
      
      // Handle "no-speech" error gracefully
      if (event.error === 'no-speech') {
        console.log('[Voice Recognition] No speech detected');
        setStatus('idle');
        setError('No speech detected. Please speak clearly.');
        setTimeout(() => setError(null), 3000);
        return;
      }
      
      // Handle "aborted" error (happens when stopped manually)
      if (event.error === 'aborted') {
        console.log('[Voice Recognition] Recognition aborted');
        setStatus('idle');
        return;
      }
      
      let errorMessage = 'Speech recognition error';
      
      switch (event.error) {
        case 'audio-capture':
          errorMessage = 'Microphone not found. Check your device.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone access denied. Please allow in browser settings.';
          break;
        case 'network':
          errorMessage = 'Network error. Check your connection.';
          break;
        default:
          errorMessage = `Error: ${event.error}`;
      }
      
      setStatus('error');
      setError(errorMessage);
      
      setTimeout(() => {
        setStatus('idle');
        setError(null);
      }, 3000);
    };

    recognition.onend = () => {
      // Clear timeout when recognition ends
      if ((recognitionRef.current as any).timeoutId) {
        clearTimeout((recognitionRef.current as any).timeoutId);
      }
      
      console.log('[Voice Recognition] Ended');
      // Do NOT automatically return to idle
      // Let the backend response handling control the status flow
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [enableSpeechRecognition]);

  /**
   * Handle messages from backend
   */
  const handleBackendMessage = useCallback((message: Message) => {
    console.log('[Voice Assistant] Backend message received:', JSON.stringify(message, null, 2));

    switch (message.type) {
      case 'status':
        if (message.status === 'processing') {
          setStatus('processing');
        }
        break;

      case 'response':
        console.log('[Voice Assistant] Response message:', message.message);
        
        // The backend sends the actual response text in message.message
        const responseText = message.message || '';
        
        if (responseText) {
          addAssistantMessage(responseText);
          
          // Speak the response if enabled
          if (enableSpeechSynthesis) {
            speakText(responseText);
          } else {
            setStatus('idle');
          }
        } else {
          console.warn('[Voice Assistant] Empty response from backend');
          setStatus('idle');
        }
        break;

      case 'error':
        console.error('[Voice Assistant] Error from backend:', message.message);
        setError(message.message || 'Unknown error occurred');
        setStatus('error');
        setTimeout(() => {
          setStatus('idle');
          setError(null);
        }, 3000);
        break;
        
      case 'action':
        // Backend is requesting a frontend state update (save restaurant, trip, etc.)
        console.log('[Voice Assistant] Action from backend:', message.action, message.data);
        if (message.action && onActionRef.current) {
          onActionRef.current({ action: message.action, data: message.data || {} });
        }
        break;

      default:
        console.warn('[Voice Assistant] Unknown message type:', message.type);
    }
  }, [enableSpeechSynthesis]);

  /**
   * Start voice recognition
   */
  const startListening = useCallback(() => {
    if (!isConnected) {
      setError('Not connected to backend');
      return;
    }

    if (!recognitionRef.current) {
      setError('Speech recognition not available');
      return;
    }

    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error('[Voice Recognition] Failed to start:', error);
      setError('Failed to start voice recognition');
    }
  }, [isConnected]);

  /**
   * Stop voice recognition
   */
  const stopListening = useCallback(() => {
    console.log('[Voice Assistant] Stop listening requested');
    
    if (recognitionRef.current) {
      try {
        // Clear timeout if exists
        if ((recognitionRef.current as any).timeoutId) {
          clearTimeout((recognitionRef.current as any).timeoutId);
        }
        
        // Stop recognition
        recognitionRef.current.stop();
        console.log('[Voice Assistant] Recognition stopped successfully');
      } catch (error) {
        console.error('[Voice Assistant] Error stopping recognition:', error);
      }
    }
    
    // Don't set to idle immediately - let the backend response handle that
    // This prevents the UI from flickering between states
  }, []);

  /**
   * Send text to backend
   */
  const sendToBackend = useCallback((text: string) => {
    console.log('[Voice Assistant] Attempting to send message:', text);
    
    if (!wsClient.current) {
      console.error('[WebSocket] Client not initialized');
      setError('WebSocket not initialized');
      setStatus('error');
      return;
    }

    // Check actual WebSocket state, not just the isConnected state variable
    if (!wsClient.current.isConnected()) {
      console.error('[WebSocket] Not connected');
      console.log('[WebSocket] isConnected state:', isConnected);
      setError('Not connected to backend. Check if server is running.');
      setStatus('error');
      setTimeout(() => {
        setStatus('idle');
        setError(null);
      }, 3000);
      return;
    }

    try {
      console.log('[WebSocket] Sending message to backend:', text);
      console.log('[WebSocket] Including user profile:', userProfileRef.current);
      console.log('[WebSocket] User agent:', navigator.userAgent);
      
      setStatus('processing');
      
      // Send message with user profile and user agent (use ref for latest value)
      wsClient.current.sendMessage(text, userProfileRef.current, navigator.userAgent);
      
      console.log('[WebSocket] Message sent successfully with user context');
    } catch (error) {
      console.error('[WebSocket] Failed to send message:', error);
      setError('Failed to send message to backend');
      setStatus('error');
      setTimeout(() => {
        setStatus('idle');
        setError(null);
      }, 3000);
    }
  }, [isConnected]);  // Remove userProfile from dependencies since we use ref

  /**
   * Speak text using Speech Synthesis
   */
  const speakText = useCallback((text: string) => {
    if (!enableSpeechSynthesis || !('speechSynthesis' in window)) {
      console.warn('[Voice Assistant] Speech synthesis not available');
      setStatus('idle');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      console.log('[Speech Synthesis] Started speaking');
      setStatus('speaking');
    };

    utterance.onend = () => {
      console.log('[Speech Synthesis] Finished speaking');
      setStatus('idle');
    };

    utterance.onerror = (event) => {
      console.error('[Speech Synthesis] Error:', event);
      setStatus('idle');
    };

    synthesisRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [enableSpeechSynthesis]);

  /**
   * Stop speaking
   */
  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setStatus('idle');
    }
  }, []);

  /**
   * Add user message to conversation
   */
  const addUserMessage = useCallback((text: string) => {
    setConversation((prev) => [
      ...prev,
      { role: 'user', text, timestamp: new Date() },
    ]);
  }, []);

  /**
   * Add assistant message to conversation
   */
  const addAssistantMessage = useCallback((text: string) => {
    setConversation((prev) => [
      ...prev,
      { role: 'assistant', text, timestamp: new Date() },
    ]);
  }, []);

  /**
   * Send text message (without voice input)
   */
  const sendTextMessage = useCallback((text: string) => {
    addUserMessage(text);
    sendToBackend(text);
  }, [addUserMessage, sendToBackend]);

  /**
   * Clear conversation
   */
  const clearConversation = useCallback(() => {
    setConversation([]);
  }, []);

  /**
   * Retry connection
   */
  const reconnect = useCallback(() => {
    if (wsClient.current) {
      wsClient.current.connect();
    }
  }, []);

  return {
    // State
    status,
    conversation,
    isConnected,
    isConnecting,
    error,

    // Actions
    startListening,
    stopListening,
    sendTextMessage,
    clearConversation,
    reconnect,
    stopSpeaking,

    // Utils
    isListening: status === 'listening',
    isProcessing: status === 'processing',
    isSpeaking: status === 'speaking',
    hasError: status === 'error',
  };
}
