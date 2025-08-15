from flask import Flask
from config import Config
import os
from .ext import db 
from Recipes import auth, recipe, user, admin


def create_app():
	app = Flask(__name__, static_folder='../app/static')
	app.config.from_object(Config)

	if not os.path.exists(app.config['UPLOAD_FOLDER']):
		os.makedirs(app.config['UPLOAD_FOLDER'])
	
	if not os.path.exists(app.config['AVATAR_FOLDER']):
		os.makedirs(app.config['AVATAR_FOLDER'])
		
	db.init_app(app)

	with app.app_context():
		db.create_all()

	app.register_blueprint(auth.bp)
	app.register_blueprint(recipe.bp)
	app.register_blueprint(user.bp)
	app.register_blueprint(admin.admin_bp)
	
	return app