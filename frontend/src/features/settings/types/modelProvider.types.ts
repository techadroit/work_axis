/**
 * Field configuration for a model provider
 */
export interface ProviderField {
  name: string;
  label: string;
  description?: string;
  type: 'text' | 'password';
  required: boolean;
  default?: string;
  placeholder?: string;
  doc_link?: string;
}

/**
 * Model Provider configuration
 */
export interface ModelProvider {
  name: string;
  model_list: string;
  fields: ProviderField[];
}

/**
 * Response type for model providers API
 */
export type ModelProvidersResponse = ModelProvider[];

/**
 * Saved Provider Configuration - returned from API
 */
export interface SavedProviderConfig {
  id: string;
  provider_name: string;
  api_key: string | null;
  base_url: string | null;
  api_version: string | null;
  deployment_name: string | null;
  aws_access_key_id: string | null;
  aws_secret_access_key: string | null;
  model_provider: string | null;
  region: string | null;
  config_json: string | null;
  model_list: string[];
  selected_model: string | null;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Response type for saved providers API
 */
export type SavedProvidersResponse = SavedProviderConfig[];

/**
 * Request payload for saving provider configurations
 */
export interface SaveProviderRequest {
  provider_name: string;
  api_key?: string | null;
  base_url?: string | null;
  api_version?: string | null;
  deployment_name?: string | null;
  aws_access_key_id?: string | null;
  aws_secret_access_key?: string | null;
  model_provider?: string | null;
  region?: string | null;
  config_json?: string | null;
  model_list?: string[];
  selected_model?: string | null;
  is_primary?: boolean;
}

/**
 * Array of provider configurations to save
 */
export type SaveProvidersPayload = SaveProviderRequest[];

