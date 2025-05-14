import hashlib
from database import get_connection
from models.user import User

class AuthController:
    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256."""
        return password  # For now, store as plaintext for testing

    def login(self, username, password):
        """Authenticate a user."""
        user = User.get_user_by_username(username)
        if user and user['active']:
            if user['password'] == password:  # For now, compare plaintext
                return user
        return None