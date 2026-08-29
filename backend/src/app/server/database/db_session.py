import threading
from pathlib import Path

import duckdb

from core.utils.file_util import get_data_path
from src.app.utils.logger_util import log_info, log_error, log_debug

_path = get_data_path()/"database"/"app.db"
log_debug(_path)
DB_PATH = Path(_path)

# DuckDB only allows a single OS-level connection to a database file at a time,
# even from within the same process. Repositories open/close a connection per
# call, so concurrent requests must share one underlying connection and hand
# out cursors (independent, thread-safe handles onto that same connection)
# instead of re-opening the file, or they collide with "file is being used by
# another process" and silently lose writes.
_main_connection: "duckdb.DuckDBPyConnection | None" = None
_main_connection_lock = threading.Lock()


def _get_main_connection() -> "duckdb.DuckDBPyConnection":
    global _main_connection
    if _main_connection is None:
        with _main_connection_lock:
            if _main_connection is None:
                _main_connection = duckdb.connect(str(DB_PATH))
    return _main_connection

TABLE_CHAT_SESSIONS = "chat_sessions"
TABLE_CHAT_MESSAGES = "chat_messages"
TABLE_USERS = "users"
TABLE_MODEL_PROVIDERS = "model_providers"
TABLE_EMAIL_PROVIDER_CREDENTIALS = "email_provider_credentials"
TABLE_EMAIL_ACCOUNTS = "email_accounts"


def initialize_database():
    """
    Initialize DuckDB database with required tables on startup.
    Creates: users, chat_sessions, chat_messages tables
    """
    try:
        # Ensure the database directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Connect to DuckDB
        conn = duckdb.connect(str(DB_PATH))

        # Create users table
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
                user_id VARCHAR PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL,
                email VARCHAR UNIQUE NOT NULL,
                password_hash VARCHAR NOT NULL,
                full_name VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP
            )
        """)

        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_CHAT_SESSIONS} (
                chat_session_id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                title VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_archived BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Create chat_messages table
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_CHAT_MESSAGES} (
                message_id VARCHAR PRIMARY KEY,
                chat_session_id VARCHAR NOT NULL,
                utc_time VARCHAR NOT NULL,
                sender VARCHAR NOT NULL,
                receiver VARCHAR NOT NULL,
                messages TEXT NOT NULL,
                content_type TEXT NOT NULL,
                message_type TEXT NOT NULL,
                mode VARCHAR DEFAULT 'none',
                file_name VARCHAR,
                file_path VARCHAR,
                mime_type VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(chat_session_id)
            )
        """)

        # Deliberately no explicit secondary indexes here (previously:
        # idx_chat_sessions_user_id, idx_chat_messages_chat_session_id,
        # idx_chat_messages_created_at). Hit a reproducible DuckDB (1.5.2)
        # ART index corruption bug where combining a foreign key's implicit
        # index with additional secondary indexes on the same table, under a
        # delete-heavy workload (deleting a chat session cascades to
        # deleting its messages), poisons the shared connection for the
        # whole app until restart. See the same fix applied to
        # email_accounts above. These tables are small (personal local use),
        # so the PK/FK indexes alone are sufficient - the extra indexes
        # weren't worth the corruption risk.

        # Create model_providers table
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_MODEL_PROVIDERS} (
                id VARCHAR PRIMARY KEY,
                provider_name VARCHAR NOT NULL,
                api_key VARCHAR,
                base_url VARCHAR,
                api_version VARCHAR,
                deployment_name VARCHAR,
                aws_access_key_id VARCHAR,
                aws_secret_access_key VARCHAR,
                region VARCHAR,
                config_json TEXT,
                model_list TEXT,
                model_provider VARCHAR,
                selected_model VARCHAR,
                is_primary INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create email_provider_credentials table (one row per provider,
        # e.g. 'gmail' - holds the user's own OAuth Client ID/Secret)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_EMAIL_PROVIDER_CREDENTIALS} (
                id VARCHAR PRIMARY KEY,
                provider VARCHAR NOT NULL UNIQUE,
                client_id VARCHAR NOT NULL,
                client_secret_encrypted VARCHAR NOT NULL,
                redirect_uri VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create email_accounts table (one row per connected mailbox or
        # file-import batch)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_EMAIL_ACCOUNTS} (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                provider VARCHAR NOT NULL DEFAULT 'gmail',
                email_address VARCHAR NOT NULL,
                display_name VARCHAR,
                access_token_encrypted VARCHAR,
                refresh_token_encrypted VARCHAR,
                token_expiry TIMESTAMP,
                scopes VARCHAR,
                status VARCHAR NOT NULL DEFAULT 'connected',
                last_sync_status VARCHAR DEFAULT 'idle',
                last_sync_error TEXT,
                last_synced_at TIMESTAMP,
                last_history_id VARCHAR,
                total_messages_synced INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE (user_id, provider, email_address)
            )
        """)
        # Deliberately no separate index on user_id here: this table hit a
        # reproducible DuckDB (1.5.2) ART index corruption bug in testing
        # when combining this UNIQUE constraint's implicit index with a
        # second explicit index on an UPDATE-then-DELETE row lifecycle
        # (repeatable: insert -> update(mark_synced_now COALESCE pattern) ->
        # delete). The UNIQUE constraint's index already covers user_id
        # lookups reasonably for this table's expected small row count, so
        # the extra index isn't worth the corruption risk.

        # Sync jobs run in-process (asyncio.to_thread), so a crash/restart
        # mid-sync leaves last_sync_status='running' with no worker attached
        # - the UI would show "syncing" forever. Any row still 'running' at
        # startup is by definition orphaned; mark it failed so the user can
        # retry.
        conn.execute(f"""
            UPDATE {TABLE_EMAIL_ACCOUNTS}
            SET last_sync_status = 'error',
                last_sync_error = 'Sync interrupted by app restart - please sync again.'
            WHERE last_sync_status = 'running'
        """)

        log_info(f"Database initialized successfully at {DB_PATH}")

        conn.close()

    except Exception as e:
        log_error(f"Failed to initialize database: {e}")
        raise


def get_db_connection():
    """
    Get a connection to the DuckDB database.
    Returns a cursor (independent handle) on the shared connection so callers
    can use and close() it per-request without contending for the file lock.
    """
    return _get_main_connection().cursor()


# if __name__ == "__main__":
#     initialize_database()
