from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app import db
from app.models import Post, Comment, Like, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/mode/basculer", methods=["POST"])
@login_required
def toggle_data_mode():
    current_user.data_mode = "economique" if current_user.data_mode == "complet" else "complet"
    db.session.commit()
    return redirect(request.referrer or url_for("main.feed"))


@main_bp.route("/")
@login_required
def feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("feed.html", posts=posts)


@main_bp.route("/post/nouveau", methods=["POST"])
@login_required
def create_post():
    content = request.form.get("content", "").strip()
    if content:
        post = Post(user_id=current_user.id, content=content)
        db.session.add(post)
        db.session.commit()
    else:
        flash("Le post ne peut pas être vide.", "warning")
    return redirect(url_for("main.feed"))


@main_bp.route("/post/<int:post_id>/jaime", methods=["POST"])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(post_id=post.id, user_id=current_user.id).first()
    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(post_id=post.id, user_id=current_user.id))
    db.session.commit()
    return redirect(url_for("main.feed"))


@main_bp.route("/post/<int:post_id>/commentaire", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get("content", "").strip()
    if content:
        db.session.add(Comment(post_id=post.id, user_id=current_user.id, content=content))
        db.session.commit()
    return redirect(url_for("main.feed"))


@main_bp.route("/annuaire")
@login_required
def directory():
    """Annuaire des enseignants du lycée."""
    teachers = User.query.filter_by(is_approved=True).order_by(User.full_name).all()
    return render_template("directory.html", teachers=teachers)
