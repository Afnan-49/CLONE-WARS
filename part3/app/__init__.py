from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# Define the security scheme for Swagger UI
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type 'Bearer <your_token>' to authenticate"
    }
}

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    db.init_app(app) 
    bcrypt.init_app(app) 
    jwt.init_app(app) 
    
    from app.services.facade import HBnBFacade
    from app.api.v1.users import api as users_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns
        
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/",
        authorizations=authorizations, # Enables the Authorize button
        security='apikey'              # Sets the default security to the apikey scheme
    )
    
    app.config["FACADE"] = HBnBFacade()

    # Register Namespaces
    api.add_namespace(auth_ns, path="/api/v1/auth")
    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(reviews_ns, path="/api/v1/reviews")

    return app
