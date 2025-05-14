import hashlib
from database import get_connection
from models.user import User

class AuthController:
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt."""
        return User._hash_password(None, password)

    def login(self, username, password):
        """Authenticate a user."""
        user = User.get_user_by_username(username)
        if user and user['active']:
            if User.verify_password(password, user['password']):
                # Update last login timestamp could be added here
                return user
        return None