import { z } from 'zod';
import { createInsertSchema } from 'drizzle-zod';

// Define the schema for the Voice API
export const messageSchema = z.object({
  role: z.enum(['user', 'assistant']),
  content: z.string(),
});

export const conversationHistorySchema = z.array(messageSchema);

export const transcriptionRequestSchema = z.object({
  file: z.any(), // This will be handled by the file upload middleware
});

export const transcriptionResponseSchema = z.object({
  text: z.string(),
});

export const chatRequestSchema = z.object({
  message: z.string(),
  conversation_history: conversationHistorySchema.optional(),
  voice_id: z.string().optional(),
});

export const chatResponseSchema = z.object({
  response: z.string(),
  audio_url: z.string().optional(),
});

export const textToSpeechRequestSchema = z.object({
  text: z.string(),
  voice_id: z.string().optional(),
});

export const textToSpeechResponseSchema = z.object({
  audio_url: z.string(),
});

export const voiceSchema = z.object({
  voice_id: z.string(),
  name: z.string(),
});

export const voicesResponseSchema = z.object({
  voices: z.array(voiceSchema),
});

// Types
export type Message = z.infer<typeof messageSchema>;
export type ConversationHistory = z.infer<typeof conversationHistorySchema>;
export type TranscriptionRequest = z.infer<typeof transcriptionRequestSchema>;
export type TranscriptionResponse = z.infer<typeof transcriptionResponseSchema>;
export type ChatRequest = z.infer<typeof chatRequestSchema>;
export type ChatResponse = z.infer<typeof chatResponseSchema>;
export type TextToSpeechRequest = z.infer<typeof textToSpeechRequestSchema>;
export type TextToSpeechResponse = z.infer<typeof textToSpeechResponseSchema>;
export type Voice = z.infer<typeof voiceSchema>;
export type VoicesResponse = z.infer<typeof voicesResponseSchema>;