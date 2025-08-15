from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from Recipes.models import User
from Recipes import db
from utils import save_avatar
bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			flash("Please log in to access this page.", "warning")
			return redirect(url_for("auth.login"))
		return view(**kwargs)
	return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    print("load_logged_in_user called") 
    user_id = session.get("user_id")

    if not user_id:
        g.user = None
        return

    user = User.query.get(user_id) 

    if not user:
        print("User not found in DB, clearing session")
        session.clear()
        g.user = None
    else:
        g.user = user

@bp.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		name = request.form.get("name")
		username = request.form.get("username")
		email = request.form.get("email")
		age = request.form.get("age")
		workplace = request.form.get("workplace")
		address = request.form.get("street")
		password = request.form.get("password")
		password_rpt = request.form.get("password-rpt")
		profile_image = request.files.get("profile_image")

		if password != password_rpt:
			flash("Passwords do not match!", "error")
			return redirect(url_for("auth.register"))

		role = request.form.get('role')

		allowed_domain = "@company.com"

		if role in ["admin", "moderator"] and not email.endswith(allowed_domain):
			flash(f"{role.capitalize()} must register with email ending '{allowed_domain}'", "error")
			return redirect(url_for("auth.register"))
		
		if role == 'user' and email.endswith(allowed_domain):
			flash(f"{role.capitalize()} cant use this email ending '{allowed_domain}'", "error")
			return redirect(url_for("auth.register"))

		if User.query.filter_by(username=username).first():
			flash("Username already exists. Try another.", "error")
			return redirect(url_for("auth.register"))
        
		image_filename = save_avatar(profile_image) if profile_image else None

		password_hash = generate_password_hash(password)

		user = User(
			name=name,
			username=username,
			email=email,
			password_hash=password_hash,
			workplace=workplace,
			address=address,
			profile_image=image_filename,
			age=int(age) if age else None,
            role=role
		)

		try:
			db.session.add(user)
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			flash("Error creating user: " + str(e), "error")
			return redirect(url_for("auth.register"))

		flash("Registration successful! Please log in.", "success")
		return redirect(url_for("auth.login"))

	return render_template("auth/register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		user = User.query.filter_by(username=username).first()

		if user is None:
			flash("User not found. Please register.", "error")
			return redirect(url_for("auth.register"))

		if not check_password_hash(user.password_hash, password):
			flash("Wrong password.", "error")
			return redirect(url_for("auth.login"))

		session.clear()
		session["user_id"] = user.id
		flash("Logged in successfully!", "success")
		return redirect(url_for("recipe.home"))

	return render_template("auth/login.html")

@bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("recipe.home"))
