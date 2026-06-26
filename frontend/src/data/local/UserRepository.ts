export interface UserDetailDocument {
  userId: string;
  timestamp: number;
}

/**
 * User Detail Database Service using localStorage
 * Provides methods to interact with user details stored in browser's localStorage
 */
export class UserRepository {
  private static readonly STORAGE_KEY = 'personal_ai_users';

  /**
   * Get all users from localStorage
   */
  private getAllUsersFromStorage(): UserDetailDocument[] {
    try {
      const data = localStorage.getItem(UserRepository.STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('[UserRepository] Error reading from localStorage:', error);
      return [];
    }
  }

  /**
   * Save users to localStorage
   */
  private saveUsersToStorage(users: UserDetailDocument[]): void {
    try {
      localStorage.setItem(UserRepository.STORAGE_KEY, JSON.stringify(users));
    } catch (error) {
      console.error('[UserRepository] Error writing to localStorage:', error);
    }
  }

  /**
   * Add or update user detail
   */
  async upsertUserDetail(userId: string): Promise<UserDetailDocument> {
    const timestamp = Date.now();
    const users = this.getAllUsersFromStorage();

    const existingIndex = users.findIndex(u => u.userId === userId);

    if (existingIndex !== -1) {
      // Update existing user
      users[existingIndex].timestamp = timestamp;
    } else {
      // Insert new user
      users.push({ userId, timestamp });
    }

    this.saveUsersToStorage(users);
    return { userId, timestamp };
  }

  /**
   * Get user detail by userId
   */
  async getUserDetail(userId: string): Promise<UserDetailDocument | null> {
    const users = this.getAllUsersFromStorage();
    const user = users.find(u => u.userId === userId);
    return user || null;
  }

  async getUser(): Promise<UserDetailDocument | null> {
    const users = this.getAllUsersFromStorage();
    return users.length > 0 ? users[0] : null;
  }

  /**
   * Get all user details
   */
  async getAllUserDetails(): Promise<UserDetailDocument[]> {
    const users = this.getAllUsersFromStorage();
    // Sort by timestamp descending (newest first)
    return users.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * Delete user detail
   */
  async deleteUserDetail(userId: string): Promise<boolean> {
    const users = this.getAllUsersFromStorage();
    const filteredUsers = users.filter(u => u.userId !== userId);

    if (filteredUsers.length === users.length) {
      return false; // User not found
    }

    this.saveUsersToStorage(filteredUsers);
    return true;
  }

  /**
   * Clear all user details
   */
  async clearAllUserDetails(): Promise<void> {
    localStorage.removeItem(UserRepository.STORAGE_KEY);
  }
}
