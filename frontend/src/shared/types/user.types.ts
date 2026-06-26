// Request Models

/**
 * Anonymous User Request
 */
export interface AnonymousUserRequest {
  device_id?: string;
}

/**
 * User Create Request
 */
export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string | null;
}

/**
 * User Update Request
 */
export interface UserUpdateRequest {
  username?: string | null;
  email?: string | null;
  password?: string | null;
  full_name?: string | null;
  is_active?: boolean | null;
}

/**
 * User Login Request
 */
export interface UserLoginRequest {
  username: string;
  password: string;
}

// Response Models

/**
 * Anonymous User Response
 */
export interface AnonymousUserResponse {
  user_id: string;
  is_anonymous: boolean;
  message: string;
}

/**
 * User Create Response
 */
export interface UserCreateResponse {
  user_id: string;
  username: string;
  email: string;
  message: string;
}

/**
 * User Login Response
 */
export interface UserLoginResponse {
  user_id: string;
  username: string;
  email: string;
  token?: string | null;
  message: string;
}

/**
 * User Response
 */
export interface UserResponse {
  user_id: string;
  username: string;
  email: string;
  full_name?: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  last_login?: string | null;
}

/**
 * User List Response
 */
export interface UserListResponse {
  users: UserResponse[];
  count: number;
}

/**
 * User Operation Response
 */
export interface UserOperationResponse {
  success: boolean;
  message: string;
  user_id?: string | null;
  data?: Record<string, string> | null;
}

// State Models (for Redux/State management if needed)

/**
 * Anonymous User State
 */
export interface AnonymousUserState {
  userId: string | null;
  isAnonymous: boolean;
  message: string | null;
  loading: boolean;
  error: string | null;
}

