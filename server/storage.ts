// Interface for storage operations
export interface IStorage {
  // We don't need specific storage methods for this application
  // since we're storing files on the filesystem directly
}

// In-memory storage implementation
export const storage: IStorage = {};