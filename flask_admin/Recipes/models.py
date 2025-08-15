from .ext import db
from datetime import timezone, datetime

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	username = db.Column(db.String(100), unique=True, nullable=False)
	password_hash = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	workplace = db.Column(db.String(150), nullable=False)
	address = db.Column(db.String(200), nullable=False)
	profile_image = db.Column(db.String(255), nullable=False) 
	age = db.Column(db.Integer, nullable=False)
	role = db.Column(db.String(20), default='user') 

	recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan', lazy=True)
	favorites = db.relationship('Favorite', back_populates='user', cascade="all, delete-orphan", lazy=True)
	ratings = db.relationship('Rating', back_populates='user', cascade='all, delete-orphan', lazy=True)
	comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan', lazy=True)


class Recipe(db.Model):
	__tablename__ = 'recipe'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150), nullable=False)
	short_description = db.Column(db.String(300))
	ingredients = db.Column(db.Text, nullable=False)
	instruction = db.Column(db.Text, nullable=False)
	notes = db.Column(db.Text)
	image_filename = db.Column(db.String(255))
	image_alt = db.Column(db.String(150))
	views = db.Column(db.Integer, default=0)

	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

	user = db.relationship('User', back_populates='recipes')
	favorited_by = db.relationship('Favorite', back_populates='recipe', cascade="all, delete-orphan", lazy=True)
	ratings = db.relationship('Rating', back_populates='recipe', cascade='all, delete-orphan', lazy=True)
	comments = db.relationship('Comment', back_populates='recipe', cascade='all, delete-orphan', lazy=True)

	@property
	def average_rating(self):
		if not self.ratings:
			return None
		return sum(r.value for r in self.ratings) / len(self.ratings)

class Favorite(db.Model):
	__tablename__ = 'favorites'
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

	user = db.relationship('User', back_populates='favorites')
	recipe = db.relationship('Recipe', back_populates='favorited_by')


recipe_categories = db.Table(
	'recipe_categories',
	db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
	db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Category(db.Model):
	__tablename__ = 'categories'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)

	recipes = db.relationship('Recipe', secondary=recipe_categories, backref='categories', lazy=True)

recipe_tags = db.Table(
	'recipe_tags',
	db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
	db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Tag(db.Model):
	__tablename__ = 'tags'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True, nullable=False)

	recipes = db.relationship('Recipe', secondary=recipe_tags, backref='tags', lazy=True)


class Rating(db.Model):
	__tablename__ = 'ratings'

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Integer, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

	user = db.relationship('User', back_populates='ratings')
	recipe = db.relationship('Recipe', back_populates='ratings')


class Comment(db.Model):
	__tablename__ = 'comments'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
	author = db.Column(db.String(100))
	text = db.Column(db.Text, nullable=False)
	created_at = db.Column(db.DateTime,  default=lambda: datetime.now(timezone.utc))
 
	user = db.relationship('User', back_populates='comments')
	recipe = db.relationship('Recipe', back_populates='comments')