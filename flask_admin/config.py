import os

class Config:
	SECRET_KEY = 'youwillneverguess'

	SQLALCHEMY_DATABASE_URI = 'sqlite:///datebase.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'uploads')

	AVATAR_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'avatar')

	DEBUG = True
