from app.blueprints import user, web
from app.extensions import db
from flask import Flask
# from flask_pymongo import PyMongo

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
# mongo = PyMongo(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)
app.register_blueprint(web.bp)
app.register_blueprint(user.bp)

with app.app_context():
    db.create_all()