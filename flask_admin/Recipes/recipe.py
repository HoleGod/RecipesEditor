from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, g, jsonify
from .ext import db
from .models import User, Recipe, Favorite, Category, Tag, Rating, Comment
from utils import save_image
from sqlalchemy import or_, func

bp = Blueprint('recipe', __name__)

@bp.route("/")
def home():
    featured = Recipe.query.first()
    if not featured:
        flash("No recipes available yet.")
        return render_template('recipe/index.html', featured=None, other_recipes=[])
    
    other_recipes = Recipe.query.filter(Recipe.id != featured.id).all()
    return render_template("recipe/index.html", featured=featured, other_recipes=other_recipes)

@bp.route("/add", methods=["GET", "POST"])
def add_recipe():

    if g.user is None:
        flash("Please log in", "danger")
        return redirect(url_for('auth.login'))
    
    if request.method == "POST":
        title = request.form.get('title')
        short_description = request.form.get('short_description')
        ingredients = request.form.get('ingredients')
        instruction = request.form.get('instruction')
        notes = request.form.get('notes')
        image_file = request.files.get('image_filename')
        image_alt = request.form.get('image_alt')
        categories = request.form.getlist('categories')
        tags = request.form.getlist('tags')

        image_url = save_image(image_file)

        recipe = Recipe(
            title=title,
            short_description=short_description,
            ingredients=ingredients,
            instruction=instruction,
            notes=notes,
            image_filename=image_url,
            image_alt=image_alt,
            user_id=g.user.id  
        )

        if categories:
            recipe.categories = Category.query.filter(Category.id.in_(categories)).all()
        if tags:
            recipe.tags = Tag.query.filter(Tag.id.in_(tags)).all()

        db.session.add(recipe)
        db.session.commit()

        flash("Recipe created successfully!")
        return redirect(url_for('recipe.home'))

    return render_template('recipe/form.html', categories=Category.query.all(), tags=Tag.query.all())

@bp.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    comments = Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.desc()).all()
    user_rating = None
    recipe.views += 1
    db.session.commit()
    
    if g.user:
        rating_obj = Rating.query.filter_by(user_id=g.user.id, recipe_id=recipe_id).first()
        if rating_obj:
            user_rating = rating_obj.value
    if recipe.average_rating:
        average_rating = recipe.average_rating
    else:
        average_rating = 0
    return render_template('recipe/detail.html', recipe=recipe, user_rating=user_rating, average_rating=average_rating, comments=comments)

@bp.route("/recipe/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    if request.method == "POST": 
            if g.user.id != recipe.user_id and g.user.role not in ['admin', 'moderator']:
                abort(403)

            title = request.form.get('title')
            short_description = request.form.get('short_description')
            ingredients = request.form.get('ingredients')
            instruction = request.form.get('instruction')
            notes = request.form.get('notes')
            image_file = request.files.get('image_filename') 
            image_alt = request.form.get('image_alt')
            categories = request.form.getlist('categories')
            tags = request.form.getlist('tags')

            recipe.title = title
            recipe.short_description = short_description
            recipe.ingredients = ingredients
            recipe.instruction = instruction
            recipe.notes = notes
            recipe.image_alt = image_alt

            if image_file and image_file.filename != '':
                image_url = save_image(image_file)
                recipe.image_filename = image_url

            if categories:
                recipe.categories = Category.query.filter(Category.id.in_(categories)).all()
            else:
                recipe.categories = []

            if tags:
                recipe.tags = Tag.query.filter(Tag.id.in_(tags)).all()
            else:
                recipe.tags = []

            db.session.commit()

            flash("Recipe updated successfully!")
            return redirect(url_for('recipe.show_recipe', recipe_id=recipe.id))

    return render_template('recipe/edit.html', recipe=recipe, categories=Category.query.all(), tags=Tag.query.all())

@bp.route("/recipe/<int:recipe_id>/delete", methods=["GET", "POST"])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    if g.user.id != recipe.user_id:
        abort(403) 

    db.session.delete(recipe)
    db.session.commit() 

    flash("Recipe deleted successfully!")
    return redirect(url_for('recipe.home'))

@bp.route("/recipe/<int:recipe_id>/fav", methods=["GET", "POST"])
def fav(recipe_id):
    if g.user is None:
        flash("Please log in to manage favorites.", "error")
        return redirect(url_for("auth.login"))
    
    favorite = Favorite.query.filter_by(user_id=g.user.id, recipe_id=recipe_id).first()

    if favorite:
        db.session.delete(favorite)
        flash("Removed from favorites.", "success")
    else:
        new_fav=Favorite(user_id=g.user.id, recipe_id=recipe_id)
        db.session.add(new_fav)
        flash("Added to favorites.", "success")
    
    db.session.commit()
    return redirect(request.referrer or url_for('recipe.detail'))

@bp.route("/search")
def search():
    query = request.args.get("q", "").lower()
    
    if not query:
        return jsonify([])
    
    recipes = (
        db.session.query(Recipe)
        .join(Recipe.categories, isouter=True)
        .join(Recipe.tags, isouter=True)
        .join(Recipe.user, isouter=True)
        .filter(
            or_(
                func.lower(Recipe.title).like(f"%{query}%"),
                func.lower(Category.name).like(f"%{query}%"),
                func.lower(Tag.name).like(f"%{query}%"),
                func.lower(User.name).like(f"%{query}%")
            )
        )
        .distinct()
        .all()
    )
    return render_template("recipe/search.html", recipes=recipes, query=query)

@bp.route("/search_api")
def search_api():
    query = request.args.get("q", "").lower()
    
    if not query:
        return jsonify([])
    
    query_lower = query.lower()

    recipes = (
	Recipe.query
	.join(Recipe.categories, isouter=True)
	.join(Recipe.tags, isouter=True)
	.join(Recipe.user, isouter=True)
	.filter(
		or_(
			Recipe.title.ilike(f"%{query_lower}%"),
			Category.name.ilike(f"%{query_lower}%"),
			Tag.name.ilike(f"%{query_lower}%"),
			User.name.ilike(f"%{query_lower}%")
		)
	)
	.distinct()
	.all()
)


    data = []
    for r in recipes:
        data.append({
            'id': r.id,
            'title': r.title,
            'short_description': r.short_description,
            'author_name': r.user.name,
            'categories': [c.name for c in r.categories],
            'tags': [t.name for t in r.tags],
            'image': r.image_filename or ""
        })

    return jsonify(data)

@bp.route("/recipe/<int:recipe_id>/rate", methods=["POST"])
def get_rate(recipe_id):
    if not g.user:
        flash("Please log in to rate recipes.", "danger")
        return redirect(url_for('auth.login'))
    
    rating_value = request.form.get('rating')
    
    if not rating_value or not rating_value.isdigit():
        flash('Invaild rating value', 'danger')
        return redirect('recipe.show_recipe', recipe_id=recipe_id)
    
    rating_value = int(rating_value)
    if rating_value < 1 or rating_value > 5:
        flash('Rating must be between 1 and 5', 'danger')
        return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))
    
    rating = Rating.query.filter_by(recipe_id=recipe_id, user_id=g.user.id).first()
    if rating:
        rating.value = rating_value
    else:
        rating = Rating(user_id=g.user.id, recipe_id=recipe_id, value=rating_value)
        db.session.add(rating)

    db.session.commit()
    flash("Rating has been saved", "success")

    return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))

@bp.route("/recipe/<int:recipe_id>/add_comment", methods=["GET", "POST"])
def add_comment(recipe_id):
    if request.method == "POST":
        if not g.user:
            flash("Please log in to add comment!", "dander")
            return redirect(url_for('auth.login'))

        text = request.form.get('text', "").strip()
        if not text:
            flash("Comment can't be empty!", "danger")
            return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))
        
        comment = Comment(
            user_id = g.user.id,
            recipe_id = recipe_id,
            author = g.user.name,
            text=text
        )

        db.session.add(comment)
        db.session.commit()

        flash("Your comment has been added!", "success")
        return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id)) 
    return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))

@bp.route("/recipe/<int:recipe_id>/<int:comment_id>/edit_comment", methods=["POST"])
def edit_comment(recipe_id, comment_id):
    if not g.user:
        flash("Please log in to edit comment!", "danger")
        return redirect(url_for('auth.login'))

    text = request.form.get('text', "").strip()
    if not text:
        flash("Comment can't be empty!", "danger")
        return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))

    comment = Comment.query.filter_by(user_id=g.user.id, recipe_id=recipe_id, id=comment_id).first()
    if not comment:
        flash("Comment not found!", "danger")
        return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))
    if g.user.id == comment.user_id:
        comment.text = text
        db.session.commit()

    flash("Your comment has been updated!", "success")
    return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))

@bp.route("/recipe/<int:recipe_id>/<int:comment_id>/delete_comment", methods=["POST"])
def delete_comment(recipe_id, comment_id):
    if not g.user:
        flash("Please log in to delete comment!", "danger")
        return redirect(url_for('auth.login'))
    
    comment = Comment.query.get_or_404(comment_id)

    role = g.user.role
    if g.user.id == comment.user_id or role in ['moderator', 'admin']:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment has been deleted", "success")
    else:
        flash("You don't have permission to delete this comment!", "danger")

    return redirect(url_for('recipe.show_recipe', recipe_id=recipe_id))
