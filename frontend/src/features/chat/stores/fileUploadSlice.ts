import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { FileData, UploadProgress } from '../types/fileUpload.types';
import { UploadState } from '../types/fileUpload.types';
import { logger } from '../../../core/logger';

interface FileUploadState {
  uploads: Record<string, UploadProgress>; // fileId -> progress
  selectedFiles: FileData[];
  uploadingFiles: Array<FileData & { fileId: string; chatSessionId: string; uploadProgress: number }>; // Files being uploaded
}

const initialState: FileUploadState = {
  uploads: {},
  selectedFiles: [],
  uploadingFiles: [],
};

const fileUploadSlice = createSlice({
  name: 'fileUpload',
  initialState,
  reducers: {
    selectFile: (state, action: PayloadAction<FileData>) => {
      state.selectedFiles.push(action.payload);
      logger.info('File selected', { filename: action.payload.name });
    },
    removeFile: (state, action: PayloadAction<number>) => {
      const removedFile = state.selectedFiles[action.payload];
      state.selectedFiles.splice(action.payload, 1);
      logger.info('File removed', { filename: removedFile?.name });
    },
    clearFiles: (state) => {
      state.selectedFiles = [];
      logger.info('All files cleared');
    },
    updateUploadProgress: (state, action: PayloadAction<{ fileId: string; progress: UploadProgress }>) => {
      const { fileId, progress } = action.payload;
      state.uploads[fileId] = progress;

      if (progress.state === UploadState.SUCCESS) {
        // Remove from selected files when uploaded successfully
        state.selectedFiles = state.selectedFiles.filter(f => f.name !== fileId);
      }
    },
    clearUploadProgress: (state, action: PayloadAction<string>) => {
      delete state.uploads[action.payload];
    },
    startFileUpload: (state, action: PayloadAction<FileData & { fileId: string; chatSessionId: string }>) => {
      const fileData = action.payload;
      state.uploadingFiles.push({
        ...fileData,
        uploadProgress: 0,
      });
      logger.info('File upload started', { filename: fileData.name, fileId: fileData.fileId, chatSessionId: fileData.chatSessionId });
    },
    updateFileUploadProgress: (state, action: PayloadAction<{ fileId: string; progress: UploadProgress }>) => {
      const { fileId, progress } = action.payload;
      const file = state.uploadingFiles.find(f => f.fileId === fileId);
      if (file) {
        file.uploadProgress = progress.progress; // Extract numeric progress from UploadProgress object
      }
    },
    completeFileUpload: (state, action: PayloadAction<string>) => {
      const fileId = action.payload;
      state.uploadingFiles = state.uploadingFiles.filter(f => f.fileId !== fileId);
      logger.info('File upload completed', { fileId });
    },
  },
});

export const {
  selectFile,
  removeFile,
  clearFiles,
  updateUploadProgress,
  clearUploadProgress,
  startFileUpload,
  updateFileUploadProgress,
  completeFileUpload,
} = fileUploadSlice.actions;

export default fileUploadSlice.reducer;

