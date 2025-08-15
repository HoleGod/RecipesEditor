from Recipes import create_app
from Recipes.ext import db
from Recipes.models import Category, Tag

def init_db():
	app = create_app()
	with app.app_context():
		db.create_all()

		if not Category.query.first():
			initial_categories = [
				Category(name='Dessert'),
				Category(name='Main Course'),
				Category(name='Salad'),
				Category(name='Appetizer'),
				Category(name='Second')
			]
			initial_tags = [
				Tag(name='Vegan'),
				Tag(name='Gluten-free'),
				Tag(name='Quick'),
				Tag(name='Healthy'),
				Tag(name='ForSport'),
				Tag(name='ForMovies')
			]
			db.session.add_all(initial_categories + initial_tags)
			try:
				db.session.commit()
				print("Initial categories and tags created successfully.")
			except Exception as e:
				db.session.rollback()
				print(f"Error while committing initial data: {e}")
		else:
			print("Categories already exist. Skipping initial data creation.")

if __name__ == '__main__':
	init_db()
