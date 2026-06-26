import { logger } from '../../../core/logger';
import type { FileUploadResponse, UploadProgress } from '../types/fileUpload.types';
import { UploadState } from '../types/fileUpload.types';

/**
 * File Upload Service
 * Handles file uploads to the server with progress tracking
 */
export class FileUploadService {
  private baseURL: string;

  constructor(baseURL: string = 'http://127.0.0.1:8001/api') {
    this.baseURL = baseURL;
  }

  /**
   * Upload a file with progress tracking
   */
  async uploadFile(
    file: File,
    sessionId: string,
    userId:string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<FileUploadResponse> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();

      // Add file to form data
      formData.append('file', file);
      formData.append('filename', file.name);
      formData.append('filesize', file.size.toString());
      formData.append('mimetype', file.type);
      formData.append('session_id', sessionId);
      formData.append('user_id', userId);

      // Track upload progress
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          logger.info('File upload progress', { progress, loaded: event.loaded, total: event.total });

          if (onProgress) {
            onProgress({
              state: UploadState.UPLOADING,
              progress,
            });
          }
        }
      });

      // Handle successful upload
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response: FileUploadResponse = JSON.parse(xhr.responseText);
            logger.info('File uploaded successfully', response);

            if (onProgress) {
              onProgress({
                state: UploadState.SUCCESS,
                progress: 100,
                url: response.file_path,
              });
            }

            resolve(response);
          } catch (error) {
            const errorMsg = 'Failed to parse upload response';
            logger.error(errorMsg, error);

            if (onProgress) {
              onProgress({
                state: UploadState.ERROR,
                progress: 0,
                error: errorMsg,
              });
            }

            reject(new Error(errorMsg));
          }
        } else {
          const errorMsg = `Upload failed with status: ${xhr.status}`;
          logger.error(errorMsg);

          if (onProgress) {
            onProgress({
              state: UploadState.ERROR,
              progress: 0,
              error: errorMsg,
            });
          }

          reject(new Error(errorMsg));
        }
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        const errorMsg = 'Network error during file upload';
        logger.error(errorMsg);

        if (onProgress) {
          onProgress({
            state: UploadState.ERROR,
            progress: 0,
            error: errorMsg,
          });
        }

        reject(new Error(errorMsg));
      });

      // Handle abort
      xhr.addEventListener('abort', () => {
        const errorMsg = 'File upload aborted';
        logger.warn(errorMsg);

        if (onProgress) {
          onProgress({
            state: UploadState.ERROR,
            progress: 0,
            error: errorMsg,
          });
        }

        reject(new Error(errorMsg));
      });

      // Send the request
      const uploadUrl = `${this.baseURL}/uploadfile?session_id=${sessionId}&user_id=${userId}`;
      xhr.open('POST', uploadUrl, true);

      logger.info('Starting file upload', {
        filename: file.name,
        size: file.size,
        url: uploadUrl
      });

      if (onProgress) {
        onProgress({
          state: UploadState.UPLOADING,
          progress: 0,
        });
      }

      xhr.send(formData);
    });
  }

  /**
   * Update the base URL
   */
  updateBaseURL(url: string): void {
    this.baseURL = url;
    logger.info('File upload base URL updated', { url });
  }
}

// Export singleton instance
export const fileUploadService = new FileUploadService();

