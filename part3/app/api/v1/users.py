from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required  # <--- Essential for Task 2
from flask import current_app

api = Namespace('users', description='User operations')

# Define the user model for input validation and output masking
user_model = api.model('User', {
    'id': fields.String(readOnly=True, description='The user unique identifier'),
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'is_admin': fields.Boolean(default=False, description='Whether the user is an admin'),
    'created_at': fields.String(readOnly=True, description='Creation timestamp'),
    'updated_at': fields.String(readOnly=True, description='Last update timestamp')
})

@api.route('/')
class UserList(Resource):
    @api.doc('list_users')
    @api.marshal_list_with(user_model)
    @jwt_required()  # <--- Only users with a valid token can access this now
    def get(self):
        """Retrieve a list of all users (Protected)"""
        facade = current_app.config['FACADE']
        return facade.list_users()

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model, code=201)
    def post(self):
        """Register a new user"""
        facade = current_app.config['FACADE']
        user_data = api.payload
        try:
            new_user = facade.create_user(user_data)
            return new_user, 201
        except ValueError as e:
            return {'error': str(e)}, 400

@api.route('/<user_id>')
@api.response(404, 'User not found')
class UserResource(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, user_id):
        """Get user details by ID"""
        facade = current_app.config['FACADE']
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "User not found")
        return user

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model)
    @jwt_required()  # <--- Protecting updates as well is good practice!
    def put(self, user_id):
        """Update user information"""
        facade = current_app.config['FACADE']
        user_data = api.payload
        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            api.abort(404, "User not found")
        return updated_user
