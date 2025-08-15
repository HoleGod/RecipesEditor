import os
import time
from flask import current_app
from werkzeug.utils import secure_filename
from sqlalchemy import func
from Recipes.ext import db
from Recipes.models import Favorite, Recipe, Comment
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image_file):
	if image_file and allowed_file(image_file.filename):
		filename = secure_filename(image_file.filename)
		name, ext = os.path.splitext(filename)
		unique_name = f"{name}_{int(time.time())}{ext}"

		upload_folder = current_app.config['UPLOAD_FOLDER']

		image_path = os.path.join(upload_folder, unique_name)
		image_file.save(image_path)

		image_url = f"uploads/{unique_name}"
		return image_url
	
def save_avatar(avatar_file):
    if avatar_file and allowed_file(avatar_file.filename):
        filename = secure_filename(avatar_file.filename)
        name, ext = os.path.splitext(filename)
        unique_name = f"{name}_{int(time.time())}{ext}"

        avatar_folder = os.path.join(current_app.config['AVATAR_FOLDER'])

        image_path = os.path.join(avatar_folder, unique_name)
        avatar_file.save(image_path)

        image_url = f"avatar/{unique_name}"
        return image_url 
	