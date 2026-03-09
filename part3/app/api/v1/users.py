from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import current_app, request

api = Namespace('users', description='User operations')

@api.route('/<user_id>')
class UserResource(Resource):
    @jwt_required()
    def put(self, user_id):
        """Update user information (Admin or Self)"""
        token_claims = get_jwt()
        is_admin = token_claims.get('is_admin', False)
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']

        # 1. Permission Check
        if not is_admin and current_user_id != user_id:
            return {'error': 'Admin privileges required'}, 403

        data = request.json
        email = data.get('email')

        # 2. Email Uniqueness Check (Only if email is being changed)
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        # 3. Admins can change everything; Regular users still blocked from email/pass
        if not is_admin and ('email' in data or 'password' in data):
            return {'error': 'You cannot modify email or password'}, 400

        updated_user = facade.update_user(user_id, data)
        return updated_user, 200
