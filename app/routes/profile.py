import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import User, Post, Friendship

profile_bp = Blueprint("profile", __name__)


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@profile_bp.route("/profil/<int:user_id>")
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()

    friendship = Friendship.query.filter(
        ((Friendship.requester_id == current_user.id) & (Friendship.receiver_id == user.id))
        | ((Friendship.requester_id == user.id) & (Friendship.receiver_id == current_user.id))
    ).first()

    return render_template("profile.html", profile_user=user, posts=posts, friendship=friendship)


@profile_bp.route("/profil/modifier", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", current_user.full_name)
        current_user.subject = request.form.get("subject", current_user.subject)
        current_user.role = request.form.get("role", current_user.role)
        current_user.bio = request.form.get("bio", current_user.bio)

        file = request.files.get("profile_picture")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"user_{current_user.id}_{file.filename}")
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            current_user.profile_picture = filename

        db.session.commit()
        flash("Profil mis à jour.", "success")
        return redirect(url_for("profile.view_profile", user_id=current_user.id))

    return render_template("edit_profile.html")


@profile_bp.route("/collegue/<int:user_id>/demande", methods=["POST"])
@login_required
def send_friend_request(user_id):
    if user_id != current_user.id:
        existing = Friendship.query.filter_by(requester_id=current_user.id, receiver_id=user_id).first()
        if not existing:
            db.session.add(Friendship(requester_id=current_user.id, receiver_id=user_id, status="pending"))
            db.session.commit()
    return redirect(url_for("profile.view_profile", user_id=user_id))


@profile_bp.route("/collegue/<int:friendship_id>/accepter", methods=["POST"])
@login_required
def accept_friend_request(friendship_id):
    friendship = Friendship.query.get_or_404(friendship_id)
    if friendship.receiver_id == current_user.id:
        friendship.status = "accepted"
        db.session.commit()
    return redirect(url_for("profile.view_profile", user_id=friendship.requester_id))
