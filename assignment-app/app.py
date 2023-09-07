from flask import Flask, redirect
from flask_restful import Api, Resource, reqparse, abort
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo

app = Flask(__name__)
api = Api(app)

# client = pymongo.MongoClient("mongodb://localhost:27017/data")
client = pymongo.MongoClient("mongodb://mongodb:27017/data")
db = client.data
users = db.users

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>') 
def catch_all(path):
    return redirect('/users')

class UsersResource(Resource):
    def get(self):
        users_list = list(db.users.find({}, {'_id': 0}))
        return users_list
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()
        
        name = args['name']
        email = args['email']
        password_hash = generate_password_hash(args['password'])
        # We can use "check_password_hash" function to get again same password
        
        user = {
            'id': len(users.distinct('id')) + 1,
            'name': name,
            'email': email,
            'password': password_hash,  
        }
        db.users.insert_one(user)

        user['_id'] = None
        return user, 201

api.add_resource(UsersResource, '/users')

class UserResource(Resource):
    def get(self, user_id):
        user = db.users.find_one({'id': user_id}, {'_id': 0})
        if not user:
            abort(404, message='User not found')

        return user
    
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()

        user = db.users.find_one({'id': user_id}, {'_id': 0})
        if not user:
            user = {
                'id': len(users.distinct('id')) + 1,
                'name': args['name'],
                'email': args['email'],
                'password': generate_password_hash(args['password']),  
            }
            db.users.insert_one(user)
        else:
            db.users.update_one({'id': user_id}, {'$set': {'name': args['name'], 'email': args['email'], 'password': generate_password_hash(args['password'])}})  # Update and hash the password

        return db.users.find_one({'id': user_id}, {'_id': 0})
    
    def delete(self, user_id):
        user = db.users.find_one({'id': user_id}, {'_id': 0})
        if not user: 
            abort(404, message='User not found')
        db.users.delete_one({'id': user_id})

        return {'message': 'User deleted'}

api.add_resource(UserResource, '/users/<int:user_id>')

@app.errorhandler
def default_error_handler(error):
    message = getattr(error, 'message', 'An error occurred')
    status_code = getattr(error, 'status_code', 500)
    return {'message': message}, status_code

if __name__ == '__main__':
    app.run(debug=True)
