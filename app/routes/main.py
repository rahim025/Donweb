from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user

from app import db
from app.models import Post, Comment, Like, User, Friendship, Announcement

main_bp = Blueprint("main", __name__)

DON_BOSCO_QUOTES = [
    "L'éducation est une affaire de cœur.",
    "Il suffit que vous soyez jeunes pour que je vous aime.",
    "Aimez ce qu'aiment les jeunes, afin que les jeunes aiment ce que vous aimez.",
    "Ne remettez jamais à demain le bien que vous pouvez faire aujourd'hui.",
    "La gaieté est fille de la vertu et signe d'un cœur qui aime Dieu.",
    "Pour être aimé, il faut aimer soi-même.",
    "Le meilleur moyen d'être heureux, c'est de donner du bonheur aux autres.",
    "Sois toujours joyeux, autant que tu le peux.",
]


def quote_of_the_day():
    index = date.today().toordinal() % len(DON_BOSCO_QUOTES)
    return DON_BOSCO_QUOTES[index]


@main_bp.route("/admin/reset-db/<secret>")
def reset_db(secret):
    """Route temporaire : réinitialise les tables (à utiliser une seule fois après une
    modification des modèles, puis à supprimer)."""
    if secret != current_app.config.get("SECRET_KEY"):
        abort(404)
    db.drop_all()
    db.create_all()
    return "Base de données réinitialisée avec la nouvelle structure."


@main_bp.route("/mode/basculer", methods=["POST"])
@login_required
def toggle_data_mode():
    current_user.data_mode = "economique" if current_user.data_mode == "complet" else "complet"
    db.session.commit()
    return redirect(request.referrer or url_for("main.feed"))


@main_bp.route("/")
def home():
    """Page d'accueil publique, visible même sans être connecté."""
    if current_user.is_authenticated:
        return redirect(url_for("main.feed"))
    return render_template("landing.html", quote=quote_of_the_day())


@main_bp.route("/fil-actualite")
@login_required
def feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()

    # Statistiques rapides
    stats = {
        "teachers": User.query.filter_by(user_type="enseignant", is_approved=True).count(),
        "students": User.query.filter_by(user_type="eleve", is_approved=True).count(),
        "posts_today": Post.query.filter(db.func.date(Post.created_at) == date.today()).count(),
    }

    # Suggestions : utilisateurs approuvés, hors soi-même et hors relations déjà existantes
    existing_ids = {current_user.id}
    for f in Friendship.query.filter(
        (Friendship.requester_id == current_user.id) | (Friendship.receiver_id == current_user.id)
    ):
        existing_ids.add(f.requester_id)
        existing_ids.add(f.receiver_id)

    suggestions = (
        User.query.filter(User.is_approved == True, ~User.id.in_(existing_ids))
        .order_by(User.created_at.desc())
        .limit(5)
        .all()
    )

    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()

    return render_template(
        "feed.html",
        posts=posts,
        stats=stats,
        suggestions=suggestions,
        announcements=announcements,
        quote=quote_of_the_day(),
    )


@main_bp.route("/annonce/nouvelle", methods=["POST"])
@login_required
def create_announcement():
    if not current_user.is_admin:
        abort(403)
    content = request.form.get("content", "").strip()
    if content:
        db.session.add(Announcement(author_id=current_user.id, content=content))
        db.session.commit()
    return redirect(url_for("main.feed"))


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
