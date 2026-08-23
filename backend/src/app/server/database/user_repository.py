"""User repository for managing user CRUD operations"""
from typing import Optional, List
import uuid

from sqlalchemy import select, func

from src.app.server.database.db_session import get_db_session
from src.app.server.database.orm_models import UserORM, ChatSessionORM, ChatMessageORM
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
            user_id = user_create.user_id if user_create.user_id else str(uuid.uuid4())

            with get_db_session() as session:
                user = UserORM(
                    user_id=user_id,
                    username=user_create.username,
                    email=user_create.email,
                    password_hash=user_create.password_hash,
                    full_name=user_create.full_name,
                )
                session.add(user)

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
            with get_db_session() as session:
                user = session.get(UserORM, user_id)
                return User.model_validate(user) if user else None

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
            with get_db_session() as session:
                user = session.execute(
                    select(UserORM).where(UserORM.username == username)
                ).scalar_one_or_none()
                return User.model_validate(user) if user else None

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
            with get_db_session() as session:
                user = session.execute(
                    select(UserORM).where(UserORM.email == email)
                ).scalar_one_or_none()
                return User.model_validate(user) if user else None

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
            with get_db_session() as session:
                query = select(UserORM)
                if not include_inactive:
                    query = query.where(UserORM.is_active.is_(True))
                query = query.order_by(UserORM.created_at.desc())

                results = session.execute(query).scalars().all()
                users = [User.model_validate(row) for row in results]

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
            with get_db_session() as session:
                user = session.get(UserORM, user_id)
                if user is None:
                    log_debug(f"User {user_id} not found for update")
                    return False

                update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
                if not update_data:
                    log_debug(f"No fields to update for user {user_id}")
                    return True

                for field, value in update_data.items():
                    setattr(user, field, value)
                user.updated_at = func.current_timestamp()

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
            with get_db_session() as session:
                session_ids = session.execute(
                    select(ChatSessionORM.chat_session_id).where(ChatSessionORM.user_id == user_id)
                ).scalars().all()

                if session_ids:
                    session.execute(
                        ChatMessageORM.__table__.delete().where(
                            ChatMessageORM.chat_session_id.in_(session_ids)
                        )
                    )

                session.execute(
                    ChatSessionORM.__table__.delete().where(ChatSessionORM.user_id == user_id)
                )

                session.execute(
                    UserORM.__table__.delete().where(UserORM.user_id == user_id)
                )

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
            with get_db_session() as session:
                user = session.get(UserORM, user_id)
                if user is None:
                    return False
                user.is_active = False
                user.updated_at = func.current_timestamp()

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
            with get_db_session() as session:
                user = session.get(UserORM, user_id)
                if user is None:
                    return False
                user.last_login = func.current_timestamp()
                user.updated_at = func.current_timestamp()

            log_debug(f"Updated last login for user {user_id}")
            return True

        except Exception as e:
            log_error(f"Error updating last login for user {user_id}: {e}")
            return False

    @staticmethod
    def check_user_exists(user_id: str) -> bool:
        """
        Check if a user with the given user_id exists.

        Args:
            user_id: The user_id to check

        Returns:
            True if the user exists, False otherwise
        """
        try:
            with get_db_session() as session:
                count = session.execute(
                    select(func.count()).select_from(UserORM).where(UserORM.user_id == user_id)
                ).scalar_one()
                return count > 0
        except Exception as e:
            log_error(f"Error checking user existence: {e}")
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
            with get_db_session() as session:
                count = session.execute(
                    select(func.count()).select_from(UserORM).where(UserORM.username == username)
                ).scalar_one()
                return count > 0
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
            with get_db_session() as session:
                count = session.execute(
                    select(func.count()).select_from(UserORM).where(UserORM.email == email)
                ).scalar_one()
                return count > 0
        except Exception as e:
            log_error(f"Error checking email existence: {e}")
            return False

    @staticmethod
    def create_anonymous_user(device_id: Optional[str] = None) -> str:
        """
        Create a guest user with an auto-generated username/email.

        Args:
            device_id: Optional device identifier, folded into the generated username

        Returns:
            The user_id of the newly created anonymous user
        """
        suffix = device_id or uuid.uuid4().hex[:12]
        user_create = UserCreate(
            username=f"guest_{uuid.uuid4().hex[:12]}",
            email=f"anon_{suffix}_{uuid.uuid4().hex[:8]}@anon.personalai.internal",
            password_hash="",
        )
        return UserRepository.create_user(user_create)

    @staticmethod
    def is_anonymous_user(user_id: str) -> bool:
        """
        Check whether a user_id refers to a guest account created via
        create_anonymous_user (identified by its "@anon.personalai.internal" email domain).

        Args:
            user_id: The user_id to check

        Returns:
            True if the user is an anonymous/guest user, False otherwise
        """
        try:
            with get_db_session() as session:
                user = session.get(UserORM, user_id)
                return bool(user and user.email.endswith("@anon.personalai.internal"))
        except Exception as e:
            log_error(f"Error checking anonymous status for user {user_id}: {e}")
            return False

    @staticmethod
    def migrate_user_data(from_user_id: str, to_user_id: str) -> bool:
        """
        Reassign chat sessions (and their messages, via the FK) from an
        anonymous user to a real user.

        Args:
            from_user_id: The anonymous user_id to migrate data from
            to_user_id: The user_id to migrate data to

        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                session.execute(
                    ChatSessionORM.__table__.update()
                    .where(ChatSessionORM.user_id == from_user_id)
                    .values(user_id=to_user_id)
                )
            log_info(f"Migrated chat sessions from user {from_user_id} to {to_user_id}")
            return True
        except Exception as e:
            log_error(f"Error migrating data from {from_user_id} to {to_user_id}: {e}")
            return False

    @staticmethod
    def delete_anonymous_user(user_id: str) -> bool:
        """
        Delete an anonymous user row after its data has been migrated.

        Args:
            user_id: The anonymous user_id to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                session.execute(
                    UserORM.__table__.delete().where(UserORM.user_id == user_id)
                )
            log_info(f"Deleted anonymous user {user_id}")
            return True
        except Exception as e:
            log_error(f"Error deleting anonymous user {user_id}: {e}")
            return False
