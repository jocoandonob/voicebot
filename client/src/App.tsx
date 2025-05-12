import React, { useState, useEffect, useRef } from 'react';
import './index.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  audioUrl?: string;
}

interface Voice {
  voice_id: string;
  name: string;
}

const App: React.FC = () => {
  const [recording, setRecording] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState('21m00Tcm4TlvDq8ikWAM');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const conversationContainerRef = useRef<HTMLDivElement>(null);
  
  // Fetch available voices on component mount
  useEffect(() => {
    fetchVoices();
  }, []);

  // Scroll to bottom of conversation when messages change
  useEffect(() => {
    if (conversationContainerRef.current) {
      conversationContainerRef.current.scrollTop = conversationContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchVoices = async () => {
    try {
      const response = await fetch('/api/voice/voices');
      if (!response.ok) throw new Error('Failed to fetch voices');
      
      const data = await response.json();
      setVoices(data.voices || []);
    } catch (error) {
      setError('Could not load voices. Using default voice.');
      console.error('Error fetching voices:', error);
    }
  };

  const startRecording = async () => {
    try {
      setError('');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorder.onstop = processAudio;
      
      mediaRecorder.start();
      setRecording(true);
      setStatus('Recording... Speak now');
    } catch (error) {
      setError('Could not access microphone. Please check permissions.');
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setStatus('Processing audio...');
      
      // Stop all tracks in the stream
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
    }
  };

  const processAudio = async () => {
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Create form data for the API request
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');
      
      // Transcribe the audio
      setStatus('Transcribing audio...');
      const transcriptionResponse = await fetch('/api/voice/transcribe', {
        method: 'POST',
        body: formData
      });
      
      if (!transcriptionResponse.ok) throw new Error('Failed to transcribe audio');
      
      const transcriptionData = await transcriptionResponse.json();
      const transcribedText = transcriptionData.text;
      
      // Add user message to conversation
      addMessage('user', transcribedText);
      
      // Get AI response
      await getAIResponse(transcribedText);
    } catch (error) {
      setError('Error processing audio. Please try again.');
      setStatus('');
      console.error('Error processing audio:', error);
    }
  };

  const sendTextMessage = async () => {
    if (inputText.trim()) {
      // Add user message to conversation
      addMessage('user', inputText);
      
      // Get AI response
      await getAIResponse(inputText);
      
      // Clear input
      setInputText('');
    }
  };

  const getAIResponse = async (message: string) => {
    try {
      setStatus('Getting AI response...');
      
      // Create conversation history in the format expected by the API
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      const response = await fetch('/api/voice/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message,
          conversation_history: history,
          voice_id: selectedVoice
        })
      });
      
      if (!response.ok) throw new Error('Failed to get AI response');
      
      const data = await response.json();
      
      // Add AI message to conversation
      addMessage('assistant', data.response, data.audio_url);
      
      // Update status
      setStatus('');
    } catch (error) {
      setError('Error getting AI response. Please try again.');
      setStatus('');
      console.error('Error getting AI response:', error);
    }
  };

  const addMessage = (role: 'user' | 'assistant', content: string, audioUrl?: string) => {
    setMessages(prev => [...prev, { role, content, audioUrl }]);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendTextMessage();
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Voice AI Assistant</h1>
        <p>Speak or type to interact with your AI assistant</p>
      </header>
      
      <main>
        <div className="container">
          <div className="controls">
            <div>
              <h2>Voice Input</h2>
              <div className="btn-container">
                <button 
                  onClick={startRecording} 
                  disabled={recording}
                  className="btn-primary"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0V3z"/>
                    <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/>
                  </svg>
                  Start Recording
                </button>
                <button 
                  onClick={stopRecording} 
                  disabled={!recording}
                  className="btn-secondary"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 3.5h6A1.5 1.5 0 0 1 12.5 5v6a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 11V5A1.5 1.5 0 0 1 5 3.5z"/>
                  </svg>
                  Stop Recording
                </button>
              </div>
              <div className={`record-indicator ${recording ? 'visible' : ''}`}>Recording...</div>
            </div>
            
            <div>
              <h2>Or Type Your Message</h2>
              <textarea 
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here..."
              />
              <div className="btn-container" style={{ justifyContent: 'flex-end', marginTop: '1rem' }}>
                <button 
                  onClick={sendTextMessage}
                  className="btn-outline"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855H.766l-.452.18a.5.5 0 0 0-.082.887l.41.26.001.002 4.995 3.178 3.178 4.995.002.002.26.41a.5.5 0 0 0 .886-.083l6-15Zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178Z"/>
                  </svg>
                  Send
                </button>
              </div>
            </div>
            
            <div className="voice-selector">
              <h2>Choose Voice</h2>
              <select 
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
              >
                <option value="21m00Tcm4TlvDq8ikWAM">Rachel (Default)</option>
                {voices.map(voice => (
                  voice.voice_id !== '21m00Tcm4TlvDq8ikWAM' && (
                    <option key={voice.voice_id} value={voice.voice_id}>
                      {voice.name}
                    </option>
                  )
                ))}
              </select>
            </div>
          </div>
          
          <div className={`status-message ${error ? 'error-message' : ''}`}>
            {error || status}
          </div>
        </div>
        
        <div className="container">
          <h2>Conversation</h2>
          <div ref={conversationContainerRef} className="message-container">
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                <div className="message-label">
                  {message.role === 'user' ? 'You' : 'Assistant'}
                </div>
                <p>{message.content}</p>
                {message.audioUrl && (
                  <audio 
                    controls 
                    src={message.audioUrl}
                    className="audio-player"
                    autoPlay
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
      
      <footer>
        <p>&copy; 2023 Voice AI Assistant | Powered by OpenAI & ElevenLabs</p>
      </footer>
    </div>
  );
};

export default App;