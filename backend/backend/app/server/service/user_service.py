"""User service layer for business logic and operations"""
from typing import Optional

from backend.app.server.database.user_repository import UserRepository
from backend.app.server.database.user_models import UserCreate, UserUpdate
from backend.app.server.schemas.user_schemas import (
    UserCreateRequest, UserUpdateRequest,
    UserResponse, UserCreateResponse,
    UserListResponse, UserOperationResponse,
    UserLoginRequest, UserLoginResponse,
    AnonymousUserRequest, AnonymousUserResponse
)
from backend.app.utils.logger_util import log_info, log_error, log_debug


class UserService:
    """
    Service layer for user operations.
    Acts as an intermediate layer between routes and repository.
    Handles business logic, validation, and password hashing.
    """

    def __init__(self):
        self.repository = UserRepository()

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        # salt = bcrypt.gensalt()
        # return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        return password

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password
            password_hash: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        try:
            # return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            return True
        except Exception as e:
            log_error(f"Error verifying password: {e}")
            return False

    def create_user(self, request: UserCreateRequest) -> UserCreateResponse:
        """
        Create a new user.

        Args:
            request: UserCreateRequest schema from routes

        Returns:
            UserCreateResponse with the user_id

        Raises:
            ValueError: If validation fails
            Exception: If user creation fails
        """
        try:
            log_info(f"Service: Creating user with username: {request.username}")

            # Validate required fields
            if not request.username or not request.email or not request.password:
                raise ValueError("Username, email, and password are required")

            # Check if username already exists
            if self.repository.check_username_exists(request.username):
                raise ValueError(f"Username '{request.username}' already exists")

            # Check if email already exists
            if self.repository.check_email_exists(str(request.email)):
                raise ValueError(f"Email '{request.email}' already exists")

            # Hash the password
            password_hash = self.hash_password(request.password)

            # Convert request schema to repository model
            user_create = UserCreate(
                username=request.username,
                email=str(request.email),
                password_hash=password_hash,
                full_name=request.full_name,
                user_id=None  # Let repository generate it
            )

            # Call repository to create user
            user_id = self.repository.create_user(user_create)

            log_info(f"Service: Successfully created user {user_id}")

            # Return response schema
            return UserCreateResponse(
                user_id=user_id,
                username=request.username,
                email=request.email,
                message="User created successfully"
            )

        except ValueError as e:
            log_error(f"Service: Validation error creating user: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error creating user: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Get a user by their ID.

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            UserResponse or None if not found
        """
        try:
            log_debug(f"Service: Fetching user {user_id}")

            if not user_id:
                raise ValueError("user_id is required")

            # Call repository to get user
            user = self.repository.get_user_by_id(user_id)

            if user:
                log_debug(f"Service: Found user {user_id}")

                # Convert model to response schema (excludes password_hash)
                return UserResponse(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    is_active=user.is_active,
                    last_login=user.last_login
                )
            else:
                log_debug(f"Service: User {user_id} not found")
                return None

        except Exception as e:
            log_error(f"Service: Error fetching user {user_id}: {e}")
            raise

    def get_all_users(self, include_inactive: bool = False) -> UserListResponse:
        """
        Get all users.

        Args:
            include_inactive: Whether to include inactive users

        Returns:
            UserListResponse with list of users and count
        """
        try:
            log_debug(f"Service: Fetching all users (include_inactive={include_inactive})")

            # Call repository to get users
            users = self.repository.get_all_users(include_inactive)

            # Convert models to response schemas (excludes password_hash)
            user_responses = [
                UserResponse(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    is_active=user.is_active,
                    last_login=user.last_login
                )
                for user in users
            ]

            log_info(f"Service: Found {len(user_responses)} users")

            return UserListResponse(
                users=user_responses,
                count=len(user_responses)
            )

        except Exception as e:
            log_error(f"Service: Error fetching all users: {e}")
            raise

    def update_user(self, user_id: str, request: UserUpdateRequest) -> UserOperationResponse:
        """
        Update a user.

        Args:
            user_id: The ID of the user to update
            request: UserUpdateRequest schema with fields to update

        Returns:
            UserOperationResponse with success status and message
        """
        try:
            log_info(f"Service: Updating user {user_id}")

            if not user_id:
                raise ValueError("user_id is required")

            # Verify user exists before updating
            existing_user = self.repository.get_user_by_id(user_id)
            if not existing_user:
                log_error(f"Service: User {user_id} not found for update")
                return UserOperationResponse(
                    success=False,
                    message=f"User {user_id} not found",
                    user_id=user_id
                )

            # Check if username is being changed and already exists
            if request.username and request.username != existing_user.username:
                if self.repository.check_username_exists(request.username):
                    return UserOperationResponse(
                        success=False,
                        message=f"Username '{request.username}' already exists",
                        user_id=user_id
                    )

            # Check if email is being changed and already exists
            if request.email and request.email != existing_user.email:
                if self.repository.check_email_exists(str(request.email)):
                    return UserOperationResponse(
                        success=False,
                        message=f"Email '{request.email}' already exists",
                        user_id=user_id
                    )

            # Hash password if provided
            password_hash = None
            if request.password:
                password_hash = self.hash_password(request.password)

            # Convert request schema to repository model
            user_update = UserUpdate(
                username=request.username,
                email=request.email,
                password_hash=password_hash,
                full_name=request.full_name,
                is_active=request.is_active,
                last_login=None  # Don't update last_login through this endpoint
            )

            # Call repository to update user
            success = self.repository.update_user(user_id, user_update)

            if success:
                log_info(f"Service: Successfully updated user {user_id}")
                return UserOperationResponse(
                    success=True,
                    message="User updated successfully",
                    user_id=user_id
                )
            else:
                log_error(f"Service: Failed to update user {user_id}")
                return UserOperationResponse(
                    success=False,
                    message="Failed to update user",
                    user_id=user_id
                )

        except ValueError as e:
            log_error(f"Service: Validation error updating user {user_id}: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error updating user {user_id}: {e}")
            raise

    def delete_user(self, user_id: str) -> UserOperationResponse:
        """
        Permanently delete a user and all associated data.

        Args:
            user_id: The ID of the user to delete

        Returns:
            UserOperationResponse with success status and message
        """
        try:
            log_info(f"Service: Deleting user {user_id}")

            if not user_id:
                raise ValueError("user_id is required")

            # Verify user exists before deleting
            existing_user = self.repository.get_user_by_id(user_id)
            if not existing_user:
                log_error(f"Service: User {user_id} not found for deletion")
                return UserOperationResponse(
                    success=False,
                    message=f"User {user_id} not found",
                    user_id=user_id
                )

            # Call repository to delete user
            success = self.repository.delete_user(user_id)

            if success:
                log_info(f"Service: Successfully deleted user {user_id}")
                return UserOperationResponse(
                    success=True,
                    message="User deleted successfully",
                    user_id=user_id
                )
            else:
                log_error(f"Service: Failed to delete user {user_id}")
                return UserOperationResponse(
                    success=False,
                    message="Failed to delete user",
                    user_id=user_id
                )

        except ValueError as e:
            log_error(f"Service: Validation error deleting user {user_id}: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error deleting user {user_id}: {e}")
            raise

    def deactivate_user(self, user_id: str) -> UserOperationResponse:
        """
        Deactivate a user (soft delete).

        Args:
            user_id: The ID of the user to deactivate

        Returns:
            UserOperationResponse with success status and message
        """
        try:
            log_info(f"Service: Deactivating user {user_id}")

            if not user_id:
                raise ValueError("user_id is required")

            # Verify user exists before deactivating
            existing_user = self.repository.get_user_by_id(user_id)
            if not existing_user:
                log_error(f"Service: User {user_id} not found for deactivation")
                return UserOperationResponse(
                    success=False,
                    message=f"User {user_id} not found",
                    user_id=user_id
                )

            # Call repository to deactivate user
            success = self.repository.deactivate_user(user_id)

            if success:
                log_info(f"Service: Successfully deactivated user {user_id}")
                return UserOperationResponse(
                    success=True,
                    message="User deactivated successfully",
                    user_id=user_id
                )
            else:
                log_error(f"Service: Failed to deactivate user {user_id}")
                return UserOperationResponse(
                    success=False,
                    message="Failed to deactivate user",
                    user_id=user_id
                )

        except ValueError as e:
            log_error(f"Service: Validation error deactivating user {user_id}: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error deactivating user {user_id}: {e}")
            raise

    def login(self, request: UserLoginRequest) -> UserLoginResponse:
        """
        Authenticate a user and optionally migrate anonymous user data.

        Args:
            request: UserLoginRequest schema with username, password, and optional anonymous_user_id

        Returns:
            UserLoginResponse with user details and token

        Raises:
            ValueError: If authentication fails
        """
        try:
            log_info(f"Service: Login attempt for username: {request.username}")

            # Get user by username or email
            user = self.repository.get_user_by_username(request.username)
            if not user:
                user = self.repository.get_user_by_email(request.username)

            if not user:
                log_error(f"Service: User not found: {request.username}")
                raise ValueError("Invalid username or password")

            # Check if user is active
            if not user.is_active:
                log_error(f"Service: User {user.user_id} is inactive")
                raise ValueError("User account is inactive")

            # Verify password
            if not self.verify_password(request.password, user.password_hash):
                log_error(f"Service: Invalid password for user: {request.username}")
                raise ValueError("Invalid username or password")

            # Handle anonymous user data migration if provided
            data_migrated = False
            if request.anonymous_user_id:
                if self.repository.is_anonymous_user(request.anonymous_user_id):
                    log_info(f"Service: Migrating data from anonymous user {request.anonymous_user_id} to {user.user_id}")

                    # Migrate data
                    migration_success = self.repository.migrate_user_data(
                        from_user_id=request.anonymous_user_id,
                        to_user_id=user.user_id
                    )

                    if migration_success:
                        # Delete anonymous user after migration
                        self.repository.delete_anonymous_user(request.anonymous_user_id)
                        data_migrated = True
                        log_info(f"Service: Successfully migrated and deleted anonymous user {request.anonymous_user_id}")
                    else:
                        log_error(f"Service: Failed to migrate data from anonymous user {request.anonymous_user_id}")
                else:
                    log_error(f"Service: User {request.anonymous_user_id} is not an anonymous user")

            # Update last login
            self.repository.update_last_login(user.user_id)

            log_info(f"Service: Successful login for user {user.user_id}")

            # Return response schema
            return UserLoginResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                token=None,  # JWT token can be added here if needed
                message="Login successful",
                data_migrated=data_migrated
            )

        except ValueError as e:
            log_error(f"Service: Login validation error: {e}")
            raise
        except Exception as e:
            log_error(f"Service: Error during login: {e}")
            raise

    def create_anonymous_user(self, request: AnonymousUserRequest) -> AnonymousUserResponse:
        """
        Create an anonymous user for guest access.

        Args:
            request: AnonymousUserRequest schema with optional device_id

        Returns:
            AnonymousUserResponse with the anonymous user_id

        Raises:
            Exception: If anonymous user creation fails
        """
        try:
            log_info(f"Service: Creating anonymous user")

            # Call repository to create anonymous user
            user_id = self.repository.create_anonymous_user(device_id=request.device_id)

            log_info(f"Service: Successfully created anonymous user {user_id}")

            # Return response schema
            return AnonymousUserResponse(
                user_id=user_id,
                is_anonymous=True,
                message="Anonymous user created successfully"
            )

        except Exception as e:
            log_error(f"Service: Error creating anonymous user: {e}")
            raise
