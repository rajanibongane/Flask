# from flask import Flask
# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

# @app.route("/about")
# def about_world():
#     return "<p>About World!</p>"

# @app.route("/user/<name>")
# def user_world(name):
#       return f"<h1> Welcome {name} <h1>"

# @app.route("/user/<postID>")
# def show_ID(postID):
#       return f"<h1> user ID : {postID} <h1>"


# from flask import Flask
# from flask_restful import Api, Resource

# app = Flask(__name__)
# api = Api(app)

# class HelloWorld(Resource):
#     def get(self):
#         return {'message': 'Hello, World!'}

# api.add_resource(HelloWorld, '/')

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	public_id = db.Column(db.String(2), unique = True)
	name = db.Column(db.String(5))
	email = db.Column(db.String(5), unique = True)
	password = db.Column(db.String(5))

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
		if not token:
			return jsonify({'message' : 'Token is missing !!'}), 401

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
			current_user = User.query\
				.filter_by(public_id = data['public_id'])\
				.first()
		except:
			return jsonify({
				'message' : 'Token is invalid !!'
			}), 401
		return f(current_user, *args, **kwargs)

	return decorated

@app.route('/user', methods =['GET'])
@token_required
def get_all_users(current_user):
	users = User.query.all()
	output = []
	for user in users:
		output.append({
			'public_id': user.public_id,
			'name' : user.name,
			'email' : user.email
		})

	return jsonify({'users': output})

@app.route('/login', methods =['POST'])
def login():
	auth = request.form

	if not auth or not auth.get('email') or not auth.get('password'):
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
		)

	user = User.query\
		.filter_by(email = auth.get('email'))\
		.first()

	if not user:
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
		)

	if check_password_hash(user.password, auth.get('password')):
		token = jwt.encode({
			'public_id': user.public_id,
			'exp' : datetime.utcnow() + timedelta(minutes = 30)
		}, app.config['SECRET_KEY'])
		return make_response(jsonify({'token' : token}), 201)
	return make_response(
		'Could not verify',
		403,
		{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
	)

@app.route('/signup', methods =['POST'])
def signup():
	data = request.form

	name, email = data.get('name'), data.get('email')
	password = data.get('password')

	user = User.query\
		.filter_by(email = email)\
		.first()
	if not user:
		user = User(
			public_id = str(uuid.uuid4()),
			name = name,
			email = email,
			password = generate_password_hash(password)
		)
		db.session.add(user)
		db.session.commit()

		return make_response('Successfully registered.', 201)
	else:
		return make_response('User already exists. Please Log in.', 202)

with app.app_context():
	db.create_all()

if __name__ == "__main__":
	app.run(debug=True)