from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt

api = Namespace('auth', description='Authentication operations')
bcrypt = Bcrypt()

# Model for Swagger documentation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class LoginResource(Resource):
    @api.expect(login_model, validate=True)
    def post(self):
        """Authenticate user and return a JWT"""
        auth_data = request.json
        facade = current_app.config['FACADE']
        
        # 1. Fetch user by email
        user = facade.get_user_by_email(auth_data.get('email'))
        
        # 2. Validate password using Bcrypt
        if user and bcrypt.check_password_hash(user.password, auth_data.get('password')):
            # 3. Add 'is_admin' to the JWT claims
            # This allows other endpoints to check role-based access
            additional_claims = {"is_admin": user.is_admin}
            
            # 4. Create the token with the User ID as identity
            access_token = create_access_token(
                identity=user.id, 
                additional_claims=additional_claims
            )
            return {'access_token': access_token}, 200
        
        # Unauthorized if credentials fail
        return {'error': 'Invalid email or password'}, 401
