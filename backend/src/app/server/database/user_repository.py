"""User repository for managing user CRUD operations"""
from typing import Optional, List
import uuid

from src.app.server.database.db_session import get_db_connection
from src.app.server.database.user_models import (
    User, UserCreate, UserUpdate
)
from src.app.utils.logger_util import log_info, log_error, log_debug


class UserRepository:
    """Repository for managing user database operations"""

    @staticmethod
    def create_user(user_create: UserCreate) -> str:
        """
        Create a new user.

        Args:
            user_create: UserCreate model containing user data

        Returns:
            The user_id of the newly created user

        Raises:
            Exception: If user creation fails
        """
        try:
            conn = get_db_connection()

            user_id = user_create.user_id if user_create.user_id else str(uuid.uuid4())

            conn.execute("""
                INSERT INTO users (
                    user_id, username, email, password_hash, full_name,
                    created_at, updated_at, is_active, last_login
                )
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE, NULL)
            """, [
                user_id,
                user_create.username,
                user_create.email,
                user_create.password_hash,
                user_create.full_name
            ])

            conn.close()
            log_info(f"Created new user: {user_id} with username: {user_create.username}")
            return user_id

        except Exception as e:
            log_error(f"Error creating user: {e}")
            raise

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            User model or None if not found
        """
        try:
            conn = get_db_connection()

            result = conn.execute("""
                SELECT user_id, username, email, password_hash, full_name,
                       created_at, updated_at, is_active, last_login
                FROM users
                WHERE user_id = ?
            """, [user_id]).fetchone()

            conn.close()

            if result:
                return User(
                    user_id=result[0],
                    username=result[1],
                    email=result[2],
                    password_hash=result[3],
                    full_name=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    is_active=result[7],
                    last_login=result[8]
                )
            return None

        except Exception as e:
            log_error(f"Error getting user by ID {user_id}: {e}")
            raise

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Get a user by their username.

        Args:
            username: The username to search for

        Returns:
            User model or None if not found
        """
        try:
            conn = get_db_connection()

            result = conn.execute("""
                SELECT user_id, username, email, password_hash, full_name,
                       created_at, updated_at, is_active, last_login
                FROM users
                WHERE username = ?
            """, [username]).fetchone()

            conn.close()

            if result:
                return User(
                    user_id=result[0],
                    username=result[1],
                    email=result[2],
                    password_hash=result[3],
                    full_name=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    is_active=result[7],
                    last_login=result[8]
                )
            return None

        except Exception as e:
            log_error(f"Error getting user by username {username}: {e}")
            raise

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get a user by their email.

        Args:
            email: The email to search for

        Returns:
            User model or None if not found
        """
        try:
            conn = get_db_connection()

            result = conn.execute("""
                SELECT user_id, username, email, password_hash, full_name,
                       created_at, updated_at, is_active, last_login
                FROM users
                WHERE email = ?
            """, [email]).fetchone()

            conn.close()

            if result:
                return User(
                    user_id=result[0],
                    username=result[1],
                    email=result[2],
                    password_hash=result[3],
                    full_name=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    is_active=result[7],
                    last_login=result[8]
                )
            return None

        except Exception as e:
            log_error(f"Error getting user by email {email}: {e}")
            raise

    @staticmethod
    def get_all_users(include_inactive: bool = False) -> List[User]:
        """
        Get all users.

        Args:
            include_inactive: Whether to include inactive users

        Returns:
            List of User models
        """
        try:
            conn = get_db_connection()

            if include_inactive:
                query = """
                    SELECT user_id, username, email, password_hash, full_name,
                           created_at, updated_at, is_active, last_login
                    FROM users
                    ORDER BY created_at DESC
                """
            else:
                query = """
                    SELECT user_id, username, email, password_hash, full_name,
                           created_at, updated_at, is_active, last_login
                    FROM users
                    WHERE is_active = TRUE
                    ORDER BY created_at DESC
                """

            results = conn.execute(query).fetchall()
            conn.close()

            users = []
            for row in results:
                users.append(User(
                    user_id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    full_name=row[4],
                    created_at=row[5],
                    updated_at=row[6],
                    is_active=row[7],
                    last_login=row[8]
                ))

            log_debug(f"Retrieved {len(users)} users")
            return users

        except Exception as e:
            log_error(f"Error getting all users: {e}")
            raise

    @staticmethod
    def update_user(user_id: str, user_update: UserUpdate) -> bool:
        """
        Update a user.

        Args:
            user_id: The ID of the user to update
            user_update: UserUpdate model with fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            # Build dynamic update query based on what fields are provided
            update_fields = []
            values = []

            if user_update.username is not None:
                update_fields.append("username = ?")
                values.append(user_update.username)

            if user_update.email is not None:
                update_fields.append("email = ?")
                values.append(user_update.email)

            if user_update.password_hash is not None:
                update_fields.append("password_hash = ?")
                values.append(user_update.password_hash)

            if user_update.full_name is not None:
                update_fields.append("full_name = ?")
                values.append(user_update.full_name)

            if user_update.is_active is not None:
                update_fields.append("is_active = ?")
                values.append(user_update.is_active)

            if user_update.last_login is not None:
                update_fields.append("last_login = ?")
                values.append(user_update.last_login)

            if not update_fields:
                log_debug(f"No fields to update for user {user_id}")
                return True

            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)

            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
            conn.execute(query, values)

            conn.close()
            log_info(f"Updated user {user_id}")
            return True

        except Exception as e:
            log_error(f"Error updating user {user_id}: {e}")
            return False

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        Permanently delete a user and all associated data.

        Args:
            user_id: The ID of the user to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            # Delete user's chat messages first
            conn.execute("DELETE FROM chat_messages WHERE chat_id IN (SELECT chat_id FROM chats WHERE user_id = ?)", [user_id])

            # Delete user's chats
            conn.execute("DELETE FROM chats WHERE user_id = ?", [user_id])

            # Delete the user
            conn.execute("DELETE FROM users WHERE user_id = ?", [user_id])

            conn.close()
            log_info(f"Permanently deleted user {user_id} and associated data")
            return True

        except Exception as e:
            log_error(f"Error deleting user {user_id}: {e}")
            return False

    @staticmethod
    def deactivate_user(user_id: str) -> bool:
        """
        Deactivate a user (soft delete).

        Args:
            user_id: The ID of the user to deactivate

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            conn.execute("""
                UPDATE users
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, [user_id])

            conn.close()
            log_info(f"Deactivated user {user_id}")
            return True

        except Exception as e:
            log_error(f"Error deactivating user {user_id}: {e}")
            return False

    @staticmethod
    def update_last_login(user_id: str) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: The ID of the user

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_db_connection()

            conn.execute("""
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, [user_id])

            conn.close()
            log_debug(f"Updated last login for user {user_id}")
            return True

        except Exception as e:
            log_error(f"Error updating last login for user {user_id}: {e}")
            return False

    @staticmethod
    def check_username_exists(username: str) -> bool:
        """
        Check if a username already exists.

        Args:
            username: The username to check

        Returns:
            True if username exists, False otherwise
        """
        try:
            conn = get_db_connection()
            result = conn.execute("SELECT COUNT(*) FROM users WHERE username = ?", [username]).fetchone()
            conn.close()
            return result[0] > 0
        except Exception as e:
            log_error(f"Error checking username existence: {e}")
            return False

    @staticmethod
    def check_email_exists(email: str) -> bool:
        """
        Check if an email already exists.

        Args:
            email: The email to check

        Returns:
            True if email exists, False otherwise
        """
        try:
            conn = get_db_connection()
            result = conn.execute("SELECT COUNT(*) FROM users WHERE email = ?", [email]).fetchone()
            conn.close()
            return result[0] > 0
        except Exception as e:
            log_error(f"Error checking email existence: {e}")
            return False

    @staticmethod
    def create_anonymous_user(device_id: Optional[str] = None) -> str:
        """
        Create an anonymous user.

        Args:
            device_id: Optional device identifier (for logging purposes only, not stored)

        Returns:
            The user_id of the newly created anonymous user
        """
        try:
            conn = get_db_connection()

            user_id =str(uuid.uuid4())
            username = f"anonymous_{str(uuid.uuid4())[:8]}"
            email = f"{username}@anonymous.local"
            password_hash = "ANONYMOUS_USER_NO_PASSWORD"
            full_name = None  # Keep full_name empty for anonymous users

            conn.execute("""
                INSERT INTO users (
                    user_id, username, email, password_hash, full_name,
                    created_at, updated_at, is_active, last_login
                )
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE, NULL)
            """, [user_id, username, email, password_hash, full_name])

            conn.close()
            log_info(f"Created anonymous user: {user_id} (device_id: {device_id if device_id else 'none'})")
            return user_id

        except Exception as e:
            log_error(f"Error creating anonymous user: {e}")
            raise

    @staticmethod
    def check_user_exists(user_id: str) -> bool:
        """
        Check if a user ID exists.

        Args:
            user_id: The user ID to check

        Returns:
            True if user exists, False otherwise
        """
        try:
            conn = get_db_connection()
            result = conn.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", [user_id]).fetchone()
            conn.close()
            return result[0] > 0
        except Exception as e:
            log_error(f"Error checking user existence: {e}")
            return False


