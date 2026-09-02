import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'donweb.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload des photos de profil / posts
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Mo
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Inscription restreinte : seuls les emails avec ce domaine peuvent s'inscrire.
    # Mets None pour désactiver la restriction.
    ALLOWED_EMAIL_DOMAIN = os.environ.get("ALLOWED_EMAIL_DOMAIN", "donbosco.edu")
