import { apiClient } from '../../core/network/apiClient';
import type { ModelProvidersResponse, SavedProvidersResponse, SaveProvidersPayload } from '../../features/settings/types';

/**
 * Model Provider API - API calls related to model provider operations
 */
export class ModelProviderApi {
  /**
   * Get all available model providers and their configuration fields
   */
  static async getAllModelProviders(): Promise<ModelProvidersResponse> {
    return apiClient.get<ModelProvidersResponse>('/api/settings/models');
  }

  /**
   * Get all saved provider configurations
   */
  static async getSavedProviders(): Promise<SavedProvidersResponse> {
    return apiClient.get<SavedProvidersResponse>('/api/settings/providers/');
  }

  /**
   * Save provider configurations
   * @param payload - Array of provider configurations to save
   */
  static async saveProviders(payload: SaveProvidersPayload): Promise<SavedProvidersResponse> {
    return apiClient.post<SavedProvidersResponse>('/api/settings/providers', payload);
  }

  /**
   * List models installed on the local (or configured remote) Ollama server
   */
  static async getOllamaLocalModels(baseUrl?: string): Promise<{ models: string[] }> {
    return apiClient.get<{ models: string[] }>('/api/settings/providers/ollama/models', {
      params: baseUrl ? { base_url: baseUrl } : undefined,
    });
  }
}

