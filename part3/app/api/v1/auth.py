from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from flask import current_app

api = Namespace('auth', description='Authentication operations')

# Model for documentation and validation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        facade = current_app.config['FACADE']
        credentials = api.payload
        
        # 1. Find the user
        user = facade.get_user_by_email(credentials['email'])
        
        # 2. Verify existence and password
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # 3. Generate Token
        # We store the user ID as 'identity' and 'is_admin' as a claim
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"is_admin": user.is_admin}
        )
        
        return {'access_token': access_token}, 200
