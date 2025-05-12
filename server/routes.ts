import express from 'express';
import multer from 'multer';
import fetch from 'node-fetch';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import { IStorage } from './storage';

dotenv.config();

// Environment variables
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Default voice ID (Rachel)

// Define file upload directories
const UPLOADS_DIR = path.join(__dirname, '../uploads');
const AUDIO_OUTPUT_DIR = path.join(__dirname, '../audio');

// Create directories if they don't exist
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}
if (!fs.existsSync(AUDIO_OUTPUT_DIR)) {
  fs.mkdirSync(AUDIO_OUTPUT_DIR, { recursive: true });
}

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, UPLOADS_DIR);
  },
  filename: function (req, file, cb) {
    const filename = uuidv4() + path.extname(file.originalname);
    cb(null, filename);
  }
});

const upload = multer({ storage });

// Create router
export const setupRoutes = (app: express.Express, storage: IStorage) => {
  // Voice routes
  const voiceRoutes = express.Router();
  
  // Transcribe audio
  voiceRoutes.post('/transcribe', upload.single('file'), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const filePath = req.file.path;
      
      // Convert audio to text using OpenAI's Whisper API
      const formData = new FormData();
      formData.append('file', fs.createReadStream(filePath));
      formData.append('model', 'whisper-1');

      const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
        },
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`OpenAI API error: ${errorText}`);
      }

      const data = await response.json();
      
      // Clean up the uploaded file
      fs.unlinkSync(filePath);
      
      return res.json({ text: data.text });
    } catch (error) {
      console.error('Error transcribing audio:', error);
      return res.status(500).json({ error: 'Error transcribing audio' });
    }
  });

  // Chat completion and text-to-speech
  voiceRoutes.post('/chat', async (req, res) => {
    try {
      const { message, conversation_history = [], voice_id = DEFAULT_VOICE_ID } = req.body;

      if (!message) {
        return res.status(400).json({ error: 'Message is required' });
      }

      // Format conversation history
      const systemMessage = {
        role: "system", 
        content: "You are a helpful voice assistant. Provide concise and useful responses."
      };
      
      const messages = [systemMessage];
      
      // Add conversation history
      if (conversation_history && Array.isArray(conversation_history)) {
        conversation_history.forEach(msg => {
          if (msg.role && msg.content) {
            messages.push({
              role: msg.role,
              content: msg.content
            });
          }
        });
      }
      
      // Add the new user message
      messages.push({ role: "user", content: message });

      // Get chat completion from OpenAI
      const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-4-turbo',
          messages: messages,
          max_tokens: 300,
          temperature: 0.7
        })
      });

      if (!openaiResponse.ok) {
        const errorText = await openaiResponse.text();
        throw new Error(`OpenAI API error: ${errorText}`);
      }

      const openaiData = await openaiResponse.json();
      const responseText = openaiData.choices[0].message.content;
      
      // Convert text to speech using ElevenLabs
      const elevenLabsResponse = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice_id}/stream`, {
        method: 'POST',
        headers: {
          'xi-api-key': ELEVENLABS_API_KEY,
          'Content-Type': 'application/json',
          'Accept': 'audio/mpeg'
        },
        body: JSON.stringify({
          text: responseText,
          model_id: 'eleven_monolingual_v1',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75
          }
        })
      });

      if (!elevenLabsResponse.ok) {
        const errorText = await elevenLabsResponse.text();
        throw new Error(`ElevenLabs API error: ${errorText}`);
      }

      // Save the audio file
      const audioBuffer = await elevenLabsResponse.buffer();
      const audioFilename = `${uuidv4()}.mp3`;
      const audioFilePath = path.join(AUDIO_OUTPUT_DIR, audioFilename);
      
      fs.writeFileSync(audioFilePath, audioBuffer);
      
      // Audio URL for the client
      const audioUrl = `/audio/${audioFilename}`;
      
      return res.json({
        response: responseText,
        audio_url: audioUrl
      });
    } catch (error) {
      console.error('Error in chat completion:', error);
      return res.status(500).json({ error: 'Error processing chat' });
    }
  });

  // Text to speech only
  voiceRoutes.post('/text-to-speech', async (req, res) => {
    try {
      const { text, voice_id = DEFAULT_VOICE_ID } = req.body;

      if (!text) {
        return res.status(400).json({ error: 'Text is required' });
      }

      // Convert text to speech using ElevenLabs
      const elevenLabsResponse = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice_id}/stream`, {
        method: 'POST',
        headers: {
          'xi-api-key': ELEVENLABS_API_KEY,
          'Content-Type': 'application/json',
          'Accept': 'audio/mpeg'
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_monolingual_v1',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75
          }
        })
      });

      if (!elevenLabsResponse.ok) {
        const errorText = await elevenLabsResponse.text();
        throw new Error(`ElevenLabs API error: ${errorText}`);
      }

      // Save the audio file
      const audioBuffer = await elevenLabsResponse.buffer();
      const audioFilename = `${uuidv4()}.mp3`;
      const audioFilePath = path.join(AUDIO_OUTPUT_DIR, audioFilename);
      
      fs.writeFileSync(audioFilePath, audioBuffer);
      
      // Audio URL for the client
      const audioUrl = `/audio/${audioFilename}`;
      
      return res.json({ audio_url: audioUrl });
    } catch (error) {
      console.error('Error in text-to-speech:', error);
      return res.status(500).json({ error: 'Error converting text to speech' });
    }
  });

  // Get available voices
  voiceRoutes.get('/voices', async (req, res) => {
    try {
      const response = await fetch('https://api.elevenlabs.io/v1/voices', {
        headers: {
          'xi-api-key': ELEVENLABS_API_KEY
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`ElevenLabs API error: ${errorText}`);
      }

      const data = await response.json();
      
      return res.json({ voices: data.voices });
    } catch (error) {
      console.error('Error fetching voices:', error);
      return res.status(500).json({ error: 'Error fetching voices' });
    }
  });

  // Register the routes
  app.use('/api/voice', voiceRoutes);
  
  // Serve static audio files
  app.use('/audio', express.static(AUDIO_OUTPUT_DIR));
  
  // Health check
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok' });
  });

  return app;
};