import { apiClient } from '../../core/network/apiClient';
import type {
  EmailAccount,
  EmailAccountResponse,
  EmailProviderCredentials,
  EmailProviderCredentialsCreate,
  EmailProviderStatus,
  EmailSyncStatusResponse,
  OAuthUrlResponse,
} from '../../features/settings/types';

export class EmailIntegrationApi {
  static async saveProviderCredentials(payload: EmailProviderCredentialsCreate): Promise<EmailProviderCredentials> {
    return apiClient.post<EmailProviderCredentials>('/api/email/provider-credentials', payload);
  }

  static async getProviderCredentials(provider: string): Promise<EmailProviderCredentials> {
    return apiClient.get<EmailProviderCredentials>(`/api/email/provider-credentials/${provider}`);
  }

  static async getProviderStatus(provider: string): Promise<EmailProviderStatus> {
    return apiClient.get<EmailProviderStatus>(`/api/email/provider-status/${provider}`);
  }

  static async getOAuthUrl(userId: string, provider: string = 'gmail'): Promise<OAuthUrlResponse> {
    return apiClient.get<OAuthUrlResponse>(`/api/email/${userId}/oauth-url`, { params: { provider } });
  }

  static async getAccounts(userId: string): Promise<EmailAccount[]> {
    return apiClient.get<EmailAccount[]>(`/api/email/accounts/${userId}`);
  }

  static async disconnectAccount(accountId: string): Promise<EmailAccountResponse> {
    return apiClient.delete<EmailAccountResponse>(`/api/email/accounts/id/${accountId}`);
  }

  static async startSync(accountId: string): Promise<{ status: string }> {
    return apiClient.post<{ status: string }>(`/api/email/accounts/id/${accountId}/sync`);
  }

  static async getSyncStatus(accountId: string): Promise<EmailSyncStatusResponse> {
    return apiClient.get<EmailSyncStatusResponse>(`/api/email/accounts/id/${accountId}/sync-status`);
  }

  static async importFile(userId: string, file: File): Promise<{ status: string; account_id: string }> {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('file', file);
    return apiClient.post<{ status: string; account_id: string }>('/api/email/import-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }
}
