from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from app import db
from app.models import Message, User

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/messages")
@login_required
def inbox():
    # Liste des personnes avec qui l'utilisateur a échangé
    sent_to = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user.id)
    received_from = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user.id)
    contact_ids = {row[0] for row in sent_to.union(received_from).all()}
    contacts = User.query.filter(User.id.in_(contact_ids)).all()
    return render_template("inbox.html", contacts=contacts)


@messages_bp.route("/messages/<int:user_id>", methods=["GET", "POST"])
@login_required
def conversation(user_id):
    other = User.query.get_or_404(user_id)

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            db.session.add(Message(sender_id=current_user.id, receiver_id=other.id, content=content))
            db.session.commit()
        return redirect(url_for("messages.conversation", user_id=user_id))

    thread = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other.id),
            and_(Message.sender_id == other.id, Message.receiver_id == current_user.id),
        )
    ).order_by(Message.created_at.asc()).all()

    return render_template("conversation.html", other=other, thread=thread)
