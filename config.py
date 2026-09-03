import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    # Render fournit une URL commençant par "postgres://", mais SQLAlchemy
    # attend "postgresql://" — on corrige automatiquement.
    _db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'donweb.db')}")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload des photos de profil / posts
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Mo
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Inscription restreinte : seuls les emails avec ce domaine peuvent s'inscrire.
    # Laisse vide (pas de valeur) pour autoriser n'importe quel email.
    ALLOWED_EMAIL_DOMAIN = os.environ.get("ALLOWED_EMAIL_DOMAIN") or None
