/**
 * File upload state management
 */
export enum UploadState {
  IDLE = 'idle',
  UPLOADING = 'uploading',
  SUCCESS = 'success',
  ERROR = 'error',
}

/**
 * File data interface - serializable metadata only (no File objects)
 */
export interface FileData {
  name: string;
  size: number;
  type: string;
  lastModified: number;
  preview?: string; // For image preview (base64 or URL)
}

/**
 * Upload progress interface
 */
export interface UploadProgress {
  state: UploadState;
  progress: number; // 0 to 100
  error?: string;
  url?: string;
}

/**
 * File upload response from server
 */
export interface FileUploadResponse {
  file_path: string;
  filename: string;
  size: number;
  content_type: string;
  uploaded_at: string;
}

