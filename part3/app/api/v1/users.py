from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity # <--- Added get_jwt_identity
from flask import current_app

api = Namespace('users', description='User operations')

# ... (keep your existing user_model) ...

@api.route('/<user_id>')
@api.response(404, 'User not found')
class UserResource(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, user_id):
        """Get user details by ID (Public)"""
        facade = current_app.config['FACADE']
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "User not found")
        return user

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model)
    @jwt_required() # <--- Required for security
    def put(self, user_id):
        """Update user information (Protected)"""
        current_user_id = get_jwt_identity() # Get ID from the token
        facade = current_app.config['FACADE']
        
        # 1. Authorization Check: Is the user editing themselves?
        if current_user_id != user_id:
            return {'error': 'Unauthorized action'}, 403

        user_data = api.payload
        
        # 2. Field Restriction: Block email/password updates here
        if 'email' in user_data or 'password' in user_data:
            return {'error': 'You cannot modify email or password'}, 400

        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            api.abort(404, "User not found")
        return updated_user
