from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    db.init_app(app) 
    bcrypt.init_app(app)  # <--- ADD THIS LINE HERE
    
    from app.services.facade import HBnBFacade
    from app.api.v1.users import api as users_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.reviews import api as reviews_ns
        
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/"  
    )
    app.config["FACADE"] = HBnBFacade()

    # Register Namespaces
    api.add_namespace(users_ns, path="/api/v1/users") # Recommendation: Add /api/v1/ to match instructions
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(reviews_ns, path="/api/v1/reviews")

    return app
