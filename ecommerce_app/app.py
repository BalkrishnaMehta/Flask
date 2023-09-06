from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

users = []

class UsersResource(Resource):
    def get(self):
        return users
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('email', type=str, required=True, help='Email is required')
        args = parser.parse_args()
        
        user = {
            'id': len(users) + 1,
            'name': args['name'],
            'email': args['email'],
            'cart': []
        }
        users.append(user)
        
        return user, 201

api.add_resource(UsersResource, '/users')

class UserResource(Resource):
    def get(self, user_id):
        for user in users:
            if user['id'] == user_id:
                return user
        abort(404, message='User not found')
    
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        args = parser.parse_args()
        
        for user in users:
            if user['id'] == user_id:
                if args['name']:
                    user['name'] = args['name']
                if args['email']:
                    user['email'] = args['email']
                return user
        
        abort(404, message='User not found')

    def patch(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        args = parser.parse_args()

        for user in users:
            if user['id'] == user_id:
                if args['name']:
                    user['name'] = args['name']
                if args['email']:
                    user['email'] = args['email']
                return user

        abort(404, message='User not found')

    
    def delete(self, user_id):
        for user in users:
            if user['id'] == user_id:
                users.remove(user)
                return {'message': 'User deleted'}
        abort(404, message='User not found')

api.add_resource(UserResource, '/users/<int:user_id>')

class CartResource(Resource):
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('product', type=str, required=True, help='product is required')
        parser.add_argument('quantity', type=str, required=True, help='quantity is required')
        args = parser.parse_args()
        for user in users:
            if user['id'] == user_id:
                cart = user.get('cart', [])
                cart.append(args)
                user['cart'] = cart
                return cart, 201
        abort(404, message='User not found')

    
    def get(self, user_id):
        for user in users:
            if user['id'] == user_id:
                cart = user.get('cart', [])
                return cart
        abort(404, message='User not found')

api.add_resource(CartResource, '/users/<int:user_id>/cart')

class OrdersResource(Resource):
    def get(self, user_id):
        for user in users:
            if user['id'] == user_id:
                orders = user.get('orders', [])
                return orders
        abort(404, message='User not found')

api.add_resource(OrdersResource, '/users/<int:user_id>/orders')

class CheckoutResource(Resource):
    def post(self, user_id):
        for user in users:
            if user['id'] == user_id:
                cart_items = user.get('cart', [])
                if len(cart_items) > 0:
                    orders = user.get('orders', [])
                    orders.append({
                        'orderNo': len(orders) + 1,
                        'items': cart_items
                    })
                    user['orders'] = orders

                    user['cart'] = []
                    return {'message': 'Checkout process completed'}
                else:
                    abort(400, message='Cart is empty')
        abort(404, message='User not found')

api.add_resource(CheckoutResource, '/users/<int:user_id>/cart/checkout')

@app.errorhandler
def default_error_handler(error):
    message = getattr(error, 'message', 'An error occurred')
    status_code = getattr(error, 'status_code', 500)
    return {'message': message}, status_code

if __name__ == '__main__':
    app.run(debug=True)
