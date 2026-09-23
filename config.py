import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration settings."""
    BASE_DIR = BASE_DIR
    # Network & Server
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

    # Database configuration
    db_dir = os.path.join(BASE_DIR, 'database')
    os.makedirs(db_dir, exist_ok=True)
    db_file = os.path.join(db_dir, 'skillmap.db').replace('\\', '/')
    
    env_db = os.environ.get('DATABASE_URL', '')
    if env_db and not env_db.startswith('sqlite:///database/'):
        SQLALCHEMY_DATABASE_URI = env_db
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI Service Configuration
    AI_API_KEY = os.environ.get('AI_API_KEY', '').strip() or os.environ.get('OPENAI_API_KEY', '').strip()
    OPENAI_API_KEY = AI_API_KEY
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openai')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

    # Security & Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

    # Personalization & Branding
    DEVELOPER_NAME = os.environ.get('DEVELOPER_NAME', 'SANJAY')
