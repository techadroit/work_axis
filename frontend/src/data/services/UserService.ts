import { UserRepository } from '../local/UserRepository';
import { UserApi } from '../api/UserApi';
import { logger } from '../../core/logger';

/**
 * User Service
 * Business logic layer for user operations
 */
export class UserService {
  private userRepository: UserRepository;

  constructor() {
    this.userRepository = new UserRepository();
  }

  /**
   * Load or create user
   * - Checks local storage for existing user
   * - If user exists, returns the user ID
   * - If user doesn't exist, calls UserApi.loginAsAnonymous() to create an anonymous user
   * - Saves the user ID to local storage
   * - Returns the user ID
   */
  async loadOrCreateUser(): Promise<string> {
    try {
      // Check if user exists in local storage
      const allUsers = await this.userRepository.getAllUserDetails();

      if (allUsers.length > 0) {
        // User exists, return the first user ID
        const userId = allUsers[0].userId;
        return userId;
      }

      const response = await UserApi.loginAsAnonymous();
      const userId = response.user_id;

      // Save user ID to local storage
      await this.userRepository.upsertUserDetail(userId);
      return userId;
    } catch (error) {
      logger.error('Failed to load or create user', error);
      throw error;
    }
  }

  /**
   * Get current user ID from local storage
   */
  async getCurrentUserId(): Promise<string | null> {
    const allUsers = await this.userRepository.getAllUserDetails();
    return allUsers.length > 0 ? allUsers[0].userId : null;
  }

  /**
   * Clear current user from local storage
   */
  async clearCurrentUser(): Promise<void> {
    await this.userRepository.clearAllUserDetails();
    logger.info('User cleared from local storage');
  }
}

