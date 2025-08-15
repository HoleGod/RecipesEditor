from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, session, g
from Recipes import db
from Recipes.models import User, Recipe, Favorite
from werkzeug.security import generate_password_hash
from utils import save_avatar

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/<string:username>/")
def home(username):
	user = User.query.filter_by(username=username).first()
	if not user:
		flash("You are not logged in! Please log in or register and try again later!", "error")
		return redirect(url_for("auth.login"))

	return render_template("user/profile.html", user=user)

@bp.route("/<string:username>/favorites")
def show_fav(username):
    user = User.query.filter_by(username=username).first_or_404()

    favorites = (
        Recipe.query
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .filter(Favorite.user_id == user.id)
        .all()
    )

    return render_template("user/favorites.html", user=user, favorites=favorites)


@bp.route("/<string:username>/edit", methods=["GET", "POST"])
def edit(username):
    user = User.query.filter_by(username=username).first_or_404()

    if request.method == "POST":
        name = request.form.get("name")
        new_username = request.form.get("username")
        email = request.form.get("email")
        age = request.form.get("age")
        workplace = request.form.get("workplace")
        address = request.form.get("street")
        password = request.form.get("password")
        password_rpt = request.form.get("password-rpt")
        profile_image = request.files.get("profile_image")

        if password != password_rpt:
            flash("Passwords do not match!", "error")
            return redirect(url_for("user.edit", username=username))
        
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != user.id:
            flash("Username already taken!", "error")
            return redirect(url_for("user.edit", username=username))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user.id:
            flash("Email already taken!", "error")
            return redirect(url_for("user.edit", username=username))
        
        user.name = name
        user.username = new_username
        user.email = email
        user.age = int(age) if age else None
        user.workplace = workplace
        user.address = address

        if profile_image and profile_image.filename != "":
            image_filename = save_avatar(profile_image)
            user.profile_image = image_filename

        if password:
            user.password_hash = generate_password_hash(password)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("user.home", username=user.username))

    return render_template("user/edit.html", user=user)

@bp.route("/<string:username>/delete", methods=["POST"])
def delete(username):
    user = User.query.filter_by(username=username).first_or_404()
    db.session.delete(user)
    db.session.commit()

    flash("Account deleted successfully!")
    return redirect(url_for('recipe.home'))
