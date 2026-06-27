#!/usr/bin/env python3
"""
Secret Manager module
Secure storage and retrieval of secrets
"""

import os
from dataclasses import dataclass
from pathlib import Path

from cryptography.fernet import Fernet


class SecretManagerError(Exception):
    """Base exception for secret manager errors"""

    pass


class SecretNotFoundError(SecretManagerError):
    """Raised when secret is not found"""

    pass


@dataclass
class SecretMetadata:
    """Metadata for a stored secret"""

    key: str
    created_at: float
    updated_at: float | None = None


class SecretManager:
    """
    Secure secret storage with encryption

    Examples:
        >>> manager = SecretManager(project_root=Path("/tmp"))
        >>> manager.store_secret("api_key", "my-secret")
        >>> value = manager.get_secret("api_key")
    """

    def __init__(self, project_root: Path | None = None, encryption_key: bytes | None = None):
        self.project_root = project_root or Path.cwd()
        self._secrets_dir = self.project_root / ".secrets"
        self._secrets_dir.mkdir(parents=True, exist_ok=True)

        if encryption_key is None:
            # Try to load from environment or file
            env_key = os.environ.get("SECRET_MANAGER_KEY")
            if env_key:
                # env_key is base64 encoded Fernet key
                self._key = env_key.encode() if isinstance(env_key, str) else env_key
            else:
                # Generate new key
                self._key = self.generate_key()
        else:
            # encryption_key is bytes or str - normalize to str for Fernet
            self._key = encryption_key.decode() if isinstance(encryption_key, bytes) else encryption_key

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key (Fernet-compatible, 44-char base64 encoded)"""
        from cryptography.fernet import Fernet

        return Fernet.generate_key()

    @staticmethod
    def mask_secret(secret: str, visible_chars: int = 4) -> str:
        """Mask a secret for logging, showing only first/last chars"""
        if len(secret) <= visible_chars * 2:
            return "*" * len(secret)
        # Show visible_chars at start, visible_chars at end, mask the rest with **** suffix
        result = secret[:visible_chars] + "*" * (len(secret) - visible_chars * 2) + secret[-visible_chars:]
        return result + "*" * 4

    @staticmethod
    def hash_secret(secret: str) -> str:
        """Hash a secret for storage without encryption"""
        import hashlib

        return hashlib.md5(secret.encode()).hexdigest()[:16]

    def _get_cipher(self):
        """Get cipher for encryption/decryption (legacy method, kept for compatibility)"""
        # Fernet handles everything internally
        return None

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a secret"""
        fernet = Fernet(self._key)
        return fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a secret"""
        try:
            fernet = Fernet(self._key)
            return fernet.decrypt(ciphertext.encode()).decode()
        except Exception as e:
            raise SecretManagerError(f"Decryption failed: {e}") from e

    def store_secret(self, key: str, value: str, encrypt: bool = True, persist: bool = True) -> None:
        """Store a secret"""
        encrypted_value = self.encrypt(value) if encrypt else value

        secret_file = self._secrets_dir / f"{key}.enc"
        if persist:
            secret_file.write_text(encrypted_value)

    def get_secret(self, key: str, default: str | None = None, encrypt: bool = True) -> str:
        """Get a secret"""
        secret_file = self._secrets_dir / f"{key}.enc"

        if not secret_file.exists():
            if default is not None:
                return default
            raise SecretNotFoundError(f"Secret '{key}' not found")

        encrypted_value = secret_file.read_text()

        if encrypt:
            return self.decrypt(encrypted_value)
        return encrypted_value

    def delete_secret(self, key: str) -> bool:
        """Delete a secret"""
        secret_file = self._secrets_dir / f"{key}.enc"
        if secret_file.exists():
            secret_file.unlink()
            return True
        return False

    def list_secrets(self) -> list:
        """List all secret keys"""
        return [f.stem for f in self._secrets_dir.glob("*.enc")]

    def secret_exists(self, key: str) -> bool:
        """Check if a secret exists"""
        return (self._secrets_dir / f"{key}.enc").exists()

    def update_secret(self, key: str, new_value: str) -> bool:
        """Update an existing secret"""
        if not self.secret_exists(key):
            return False
        self.store_secret(key, new_value)
        return True


class EnvironmentSecretLoader:
    """Loader for secrets from environment variables"""

    @staticmethod
    def load_secret(key: str, required: bool = False, default: str | None = None) -> str:
        """Load a secret from environment"""
        value = os.environ.get(key)

        if value is None:
            if required:
                raise SecretNotFoundError(f"Required secret '{key}' not found in environment")
            return default

        return value

    @staticmethod
    def load_all_secrets(prefix: str) -> dict[str, str]:
        """Load all secrets with given prefix"""
        secrets = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                secret_key = key[len(prefix) :]
                secrets[secret_key] = value
        return secrets
