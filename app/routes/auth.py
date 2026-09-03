from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/inscription", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.feed"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        subject = request.form.get("subject", "").strip()
        user_type = request.form.get("user_type", "eleve")
        classroom = request.form.get("classroom", "").strip()

        allowed_domain = current_app.config.get("ALLOWED_EMAIL_DOMAIN")
        if allowed_domain and not email.endswith("@" + allowed_domain):
            flash(f"Seuls les emails @{allowed_domain} peuvent s'inscrire.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet email.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            full_name=full_name,
            email=email,
            subject=subject if user_type == "enseignant" else None,
            user_type=user_type,
            classroom=classroom if user_type == "eleve" else None,
            role="Enseignant" if user_type == "enseignant" else "Élève",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Compte créé ! Il doit être validé par un administrateur avant la connexion.", "info")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/connexion", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.feed"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Email ou mot de passe incorrect.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_approved:
            flash("Votre compte est en attente de validation par un administrateur.", "warning")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("main.feed"))

    return render_template("login.html")


@auth_bp.route("/deconnexion")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
