"""SQLAlchemy declarative ORM models mirroring the tables previously created
via raw SQL in db_session.py: users, chat_sessions, chat_messages,
model_providers.

Secondary indexes on chat_sessions.user_id, chat_messages.chat_session_id and
chat_messages.created_at mirror the CREATE INDEX statements from the
original raw-SQL initialize_database().
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    last_login: Mapped[datetime | None] = mapped_column(nullable=True)


class ChatSessionORM(Base):
    __tablename__ = "chat_sessions"

    chat_session_id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    is_archived: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))


class ChatMessageORM(Base):
    __tablename__ = "chat_messages"

    message_id: Mapped[str] = mapped_column(Text, primary_key=True)
    chat_session_id: Mapped[str] = mapped_column(
        ForeignKey("chat_sessions.chat_session_id"), nullable=False, index=True
    )
    utc_time: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    receiver: Mapped[str] = mapped_column(Text, nullable=False)
    messages: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(Text, server_default=text("'none'"))
    file_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"), index=True)


class ModelProviderORM(Base):
    __tablename__ = "model_providers"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    provider_name: Mapped[str] = mapped_column(Text, nullable=False)
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    api_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    deployment_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    aws_access_key_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    aws_secret_access_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_provider: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_primary: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
