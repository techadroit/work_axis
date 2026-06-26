from pathlib import Path

import duckdb

from core.utils.file_util import get_data_path
from backend.app.utils.logger_util import log_info, log_error, log_debug

_path = get_data_path()/"database"/"app.db"
log_debug(_path)
DB_PATH = Path(_path)

TABLE_CHAT_SESSIONS = "chat_sessions"
TABLE_CHAT_MESSAGES = "chat_messages"
TABLE_USERS = "users"
TABLE_MODEL_PROVIDERS = "model_providers"


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

        # Create indexes for better query performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_session_id ON chat_messages(chat_session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at)")

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

        log_info(f"Database initialized successfully at {DB_PATH}")

        conn.close()

    except Exception as e:
        log_error(f"Failed to initialize database: {e}")
        raise


def get_db_connection():
    """
    Get a connection to the DuckDB database.
    Returns a duckdb.DuckDBPyConnection object.
    """
    return duckdb.connect(str(DB_PATH))


# if __name__ == "__main__":
#     initialize_database()
