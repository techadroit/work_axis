import threading

from cryptography.fernet import Fernet, InvalidToken

from core.utils.file_util import get_keys_path
from src.app.utils.logger_util import log_debug

_KEY_FILENAME = "email_secret.key"

_fernet: "Fernet | None" = None
_fernet_lock = threading.Lock()


def _get_or_create_fernet_key() -> bytes:
    key_path = get_keys_path() / _KEY_FILENAME
    if key_path.exists():
        return key_path.read_bytes()

    key_path.parent.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    key_path.write_bytes(key)
    try:
        # Best-effort - os.chmod is a no-op on Windows/NTFS, so this does not
        # meaningfully restrict access there. Kept for POSIX deployments.
        key_path.chmod(0o600)
    except OSError:
        pass
    log_debug(f"Generated new email token encryption key at {key_path}")
    return key


def provide_fernet() -> Fernet:
    """Singleton Fernet instance backed by a locally-generated, persisted key."""
    global _fernet
    if _fernet is None:
        with _fernet_lock:
            if _fernet is None:
                _fernet = Fernet(_get_or_create_fernet_key())
    return _fernet


def encrypt_secret(plaintext: str | None) -> str | None:
    """Encrypt a secret string for storage. None-safe."""
    if plaintext is None:
        return None
    return provide_fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str | None) -> str | None:
    """Decrypt a secret string read from storage. None-safe."""
    if ciphertext is None:
        return None
    try:
        return provide_fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken as e:
        raise ValueError(
            "Failed to decrypt stored credential - the encryption key file may have "
            "changed or been deleted."
        ) from e
