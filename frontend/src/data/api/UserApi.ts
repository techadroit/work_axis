import { apiClient } from '../../core/network/apiClient.ts';
import type {
  AnonymousUserResponse,
  UserCreateRequest,
  UserCreateResponse,
  UserResponse,
  UserUpdateRequest,
  UserOperationResponse,
  UserListResponse,
  UserLoginRequest,
  UserLoginResponse,
} from '../../shared/types/user.types.ts';

/**
 * User API - API calls related to user operations
 * Equivalent to UserRepository in Kotlin
 */
export class UserApi {
  /**
   * Create a new user
   */
  static async createUser(request: UserCreateRequest): Promise<UserCreateResponse> {
    return apiClient.post<UserCreateResponse>('/api/users/create', request);
  }

  /**
   * Login as anonymous user
   */
  static async loginAsAnonymous(): Promise<AnonymousUserResponse> {
    return apiClient.post<AnonymousUserResponse>('/api/users/anonymous');
  }

  /**
   * Get a user by their ID
   */
  static async getUser(userId: string): Promise<UserResponse> {
    return apiClient.get<UserResponse>(`/api/users/${userId}`);
  }

  /**
   * Update a user's information
   */
  static async updateUser(userId: string, request: UserUpdateRequest): Promise<UserOperationResponse> {
    return apiClient.put<UserOperationResponse>(`/api/users/${userId}`, request);
  }

  /**
   * Permanently delete a user and all associated data
   */
  static async deleteUser(userId: string): Promise<UserOperationResponse> {
    return apiClient.delete<UserOperationResponse>(`/api/users/${userId}`);
  }

  /**
   * Get all users
   */
  static async getAllUsers(includeInactive: boolean = false): Promise<UserListResponse> {
    return apiClient.get<UserListResponse>('/api/users', {
      params: { include_inactive: includeInactive.toString() }
    });
  }

  /**
   * Deactivate a user (soft delete)
   */
  static async deactivateUser(userId: string): Promise<UserOperationResponse> {
    return apiClient.put<UserOperationResponse>(`/api/users/${userId}/deactivate`);
  }

  /**
   * Authenticate a user
   */
  static async login(request: UserLoginRequest): Promise<UserLoginResponse> {
    return apiClient.post<UserLoginResponse>('/api/users/auth/login', request);
  }

  /**
   * Legacy login endpoint (kept for backwards compatibility)
   */
  static async legacyLogin(request: UserLoginRequest): Promise<UserLoginResponse> {
    return apiClient.post<UserLoginResponse>('/api/login', request);
  }

  /**
   * Legacy get user ID endpoint (kept for backwards compatibility)
   */
  static async getUserId(): Promise<string> {
    return apiClient.get<string>('/api/login/get_user_id');
  }
}
