from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    """Service layer for user management"""

    @staticmethod
    def create_user(username, email, password, role='student'):
        """Create a new user with hashed password"""
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return None, "Username sudah digunakan"
        
        if User.query.filter_by(email=email).first():
            return None, "Email sudah terdaftar"
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            return user, "Pendaftaran berhasil"
        except Exception as e:
            db.session.rollback()
            return None, f"Error: {str(e)}"

    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user by email and password"""
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            return None, "Email tidak terdaftar"
        
        if not user.check_password(password):
            return None, "Password salah"
        
        return user, "Login berhasil"

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """Update user profile"""
        user = User.query.get(user_id)
        
        if not user:
            return None, "User tidak ditemukan"
        
        allowed_fields = ['username', 'email']
        
        try:
            for key, value in kwargs.items():
                if key in allowed_fields and value:
                    setattr(user, key, value)
            
            db.session.commit()
            return user, "Profile berhasil diupdate"
        except Exception as e:
            db.session.rollback()
            return None, f"Error: {str(e)}"

    @staticmethod
    def get_all_users(role=None):
        """Get all users, optionally filtered by role"""
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        return query.all()

    @staticmethod
    def delete_user(user_id):
        """Delete user by ID"""
        user = User.query.get(user_id)
        
        if not user:
            return False, "User tidak ditemukan"
        
        try:
            db.session.delete(user)
            db.session.commit()
            return True, "User berhasil dihapus"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
