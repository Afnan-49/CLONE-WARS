from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from app.services.facade import HBnBFacade

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['JWT_SECRET_KEY'] = 'your_super_secret_key'  # Change in production!
    
    # Initialize Extensions
    jwt = JWTManager(app)
    facade = HBnBFacade()
    app.config['FACADE'] = facade

    # Register Namespaces
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')
    
    from app.api.v1.users import api as users_ns
    from app.api.v1.auth import api as auth_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.amenities import api as amenities_ns

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')

    # --- SEEDING THE ADMIN USER ---
    # This ensures that when the app starts, an Admin exists for testing.
    # Note: Ensure your facade.create_user handles the 'is_admin' key!
    try:
        facade.create_user({
            "first_name": "Admin",
            "last_name": "HBnB",
            "email": "admin@hbnb.com",
            "password": "adminpassword123",
            "is_admin": True
        })
    except Exception as e:
        print(f"Admin already exists or error seeding: {e}")

    return app
