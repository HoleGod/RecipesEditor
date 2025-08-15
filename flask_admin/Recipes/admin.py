from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, session, g, jsonify
from .ext import db
from .models import User, Recipe, Favorite, Comment
from functools import wraps
from sqlalchemy import func
from utils import save_avatar

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user or g.user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@admin_bp.route("/")
def home():
    return render_template("admin/ixd.html")

@admin_bp.route('/dashboard')
def dashboard():
    total_views = db.session.query(func.coalesce(func.sum(Recipe.views), 0)).scalar()
    total_favorites = db.session.query(func.count(Favorite.id)).scalar()
    total_comments = db.session.query(func.count(Comment.id)).scalar()
    total_recipes = db.session.query(func.count(Recipe.id)).scalar()

    recipes = Recipe.query.all()
    return render_template('admin/dashboard.html', total_views=total_views, total_favs=total_favorites, total_comments=total_comments, total_recipes=total_recipes, recipes=recipes)

@admin_bp.route("/users")
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route("/comments")
def comments():
    comments = Comment.query.all()
    return render_template('admin/comments.html', comments=comments)

@admin_bp.route("/recipes")
def recipes():
    recipes = Recipe.query.all()
    return render_template('admin/recipes.html', recipes=recipes)

@admin_bp.route("/admin_info")
def admin():
    return render_template('admin/admin.html')

@admin_bp.route("/HelpAndFaQ")
def haf():
    return render_template('admin/haf.html')

@admin_bp.route("/admin_info/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if request.method == "POST":
        user_id = g.user.id
        current_user = User.query.get_or_404(user_id)

        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email') 
        workplace = request.form.get('workplace') 
        address = request.form.get('address') 
        age = request.form.get('age') 
        profile_image = request.files.get('profile_image')

        current_user.name = name
        current_user.username = username
        current_user.email = email
        current_user.workplace = workplace
        current_user.address = address
        current_user.age = age
        if profile_image and profile_image.filename != "":
            image_filename = save_avatar(profile_image)
            
            current_user.profile_image = image_filename

        db.session.commit()
        flash("Information has been changed!", "success")
        return redirect(url_for('admin.admin'))
    return render_template("admin/edit.html")

@admin_bp.route("/delete_comment", methods=["POST"])
def delete_comment():
    comment_id = request.form.get('comment_id')
    comment = Comment.query.get(comment_id)

    if comment:
        db.session.delete(comment)
        db.session.commit()
    
    return redirect(url_for('admin.comments'))

@admin_bp.route("/delete_user", methods=["POST"])
@role_required('admin')
def delete_user():
    user_id = request.form.get('user_id')

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('admin.users'))

@admin_bp.route("/delete_recipe", methods=["POST"])
def delete_recipe():
    recipe_id = request.form.get('recipe_id')

    recipe = Recipe.query.get(recipe_id)
    if recipe:
        db.session.delete(recipe) 
        db.session.commit()

    return redirect(url_for('admin.recipes'))

@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("recipe.home"))