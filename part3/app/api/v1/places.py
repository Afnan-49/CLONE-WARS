from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app

api = Namespace('places', description='Place operations')

# Define place model (simplified for this example)
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
    'owner_id': fields.String(readOnly=True, description='ID of the owner') # Set as readOnly
})

@api.route('/')
class PlaceList(Resource):
    @api.marshal_list_with(place_model)
    def get(self):
        """Retrieve all places (Public)"""
        facade = current_app.config['FACADE']
        return facade.get_all_places()

    @api.expect(place_model, validate=True)
    @api.marshal_with(place_model, code=201)
    @jwt_required()
    def post(self):
        """Create a new place (Protected)"""
        current_user_id = get_jwt_identity() # Identify the owner
        facade = current_app.config['FACADE']
        
        place_data = api.payload
        place_data['owner_id'] = current_user_id # Force ownership
        
        new_place = facade.create_place(place_data)
        return new_place, 201
