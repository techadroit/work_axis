export interface EmailProviderCredentialsCreate {
  provider: string;
  client_id: string;
  client_secret: string;
  redirect_uri: string;
}

export interface EmailProviderCredentials {
  id: string;
  provider: string;
  client_id: string;
  redirect_uri: string;
  created_at: string;
  updated_at: string;
}

export interface EmailAccount {
  id: string;
  user_id: string;
  provider: string;
  email_address: string;
  display_name: string | null;
  scopes: string | null;
  status: string;
  last_sync_status: string | null;
  last_sync_error: string | null;
  last_synced_at: string | null;
  total_messages_synced: number;
  created_at: string;
  updated_at: string;
}

export interface EmailAccountResponse {
  success: boolean;
  message: string;
  data: EmailAccount | null;
}

export interface EmailSyncStatusResponse {
  account_id: string;
  status: string;
  last_synced_at: string | null;
  total_messages_synced: number;
  last_sync_error: string | null;
}

export interface OAuthUrlResponse {
  auth_url: string;
  state: string;
}
