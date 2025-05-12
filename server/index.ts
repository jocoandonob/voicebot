import express from 'express';
import { setupRoutes } from './routes';
import { storage } from './storage';
import { setupViteServer } from './vite';

const app = express();
app.use(express.json());

// Create necessary directories
import fs from 'fs';
import path from 'path';
const uploadsDir = path.join(__dirname, '../uploads');
const audioDir = path.join(__dirname, '../audio');
fs.mkdirSync(uploadsDir, { recursive: true });
fs.mkdirSync(audioDir, { recursive: true });

// Setup API routes
setupRoutes(app, storage);

// Setup Vite development server (in development mode)
if (process.env.NODE_ENV !== 'production') {
  setupViteServer(app);
}

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});