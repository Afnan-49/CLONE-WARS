from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address')
})

@api.route('/')
class UserList(Resource):
    @jwt_required()
    def post(self):
        """Create a new user (Admin Only)"""
        token_claims = get_jwt()
        if not token_claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        user_data = request.json
        facade = current_app.config['FACADE']
        
        if facade.get_user_by_email(user_data.get('email')):
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        return new_user, 201

@api.route('/<user_id>')
class UserResource(Resource):
    @jwt_required()
    def put(self, user_id):
        """Update user information (Admin or Owner)"""
        token_claims = get_jwt()
        is_admin = token_claims.get('is_admin', False)
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']

        # Permission Check: Must be admin OR the user themselves
        if not is_admin and current_user_id != user_id:
            return {'error': 'Admin privileges required'}, 403

        data = request.json
        
        # Email uniqueness check for Admins changing emails
        if 'email' in data:
            existing_user = facade.get_user_by_email(data['email'])
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        # Field restriction for regular users
        if not is_admin and ('email' in data or 'password' in data):
            return {'error': 'You cannot modify email or password'}, 400

        updated_user = facade.update_user(user_id, data)
        if not updated_user:
            return {'error': 'User not found'}, 404
        return updated_user, 200
