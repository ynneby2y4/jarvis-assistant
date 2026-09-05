"""
Credential Manager - Secure storage of API keys and credentials
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
from typing import Dict, Optional
from config import config
from utils.logger import get_logger

logger = get_logger("credential_manager")


class CredentialManager:
    """Manage encrypted credentials"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.getenv("MASTER_KEY", "default-key")
        self.cipher_suite = self._create_cipher()
        self.credentials_file = "data/credentials.enc"
        self.credentials = self._load_credentials()
    
    def _create_cipher(self) -> Fernet:
        """Create cipher suite from master key"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'jarvis-salt-123',
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def _load_credentials(self) -> Dict:
        """Load encrypted credentials from file"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'rb') as f:
                    encrypted_data = f.read()
                    decrypted = self.cipher_suite.decrypt(encrypted_data)
                    return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
        return {}
    
    def save_credential(self, key: str, value: str):
        """Save encrypted credential"""
        try:
            self.credentials[key] = value
            self._save_to_file()
            logger.info(f"Credential '{key}' saved successfully")
        except Exception as e:
            logger.error(f"Error saving credential: {e}")
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get credential"""
        return self.credentials.get(key)
    
    def delete_credential(self, key: str):
        """Delete credential"""
        if key in self.credentials:
            del self.credentials[key]
            self._save_to_file()
            logger.info(f"Credential '{key}' deleted")
    
    def _save_to_file(self):
        """Save credentials to encrypted file"""
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        json_data = json.dumps(self.credentials).encode()
        encrypted = self.cipher_suite.encrypt(json_data)
        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted)
    
    def load_exchange_credentials(self, exchange: str) -> Dict:
        """Load exchange API credentials"""
        api_key = self.get_credential(f"{exchange}_api_key")
        api_secret = self.get_credential(f"{exchange}_api_secret")
        
        if not api_key or not api_secret:
            logger.warning(f"Missing credentials for {exchange}")
            return {}
        
        return {
            "apiKey": api_key,
            "secret": api_secret
        }


# Global credential manager instance
credential_manager = CredentialManager()
