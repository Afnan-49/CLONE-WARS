from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import current_app, request

api = Namespace('places', description='Place operations')

# Place model for input/output
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
    'owner_id': fields.String(readOnly=True, description='ID of the owner')
})

@api.route('/')
class PlaceList(Resource):
    @api.marshal_list_with(place_model)
    def get(self):
        """Retrieve all places (Public)"""
        return current_app.config['FACADE'].get_all_places(), 200

    @api.expect(place_model, validate=True)
    @api.marshal_with(place_model, code=201)
    @jwt_required()
    def post(self):
        """Create a new place (Protected)"""
        current_user_id = get_jwt_identity()
        place_data = request.json
        place_data['owner_id'] = current_user_id # Automatically set owner
        
        new_place = current_app.config['FACADE'].create_place(place_data)
        return new_place, 201

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.marshal_with(place_model)
    def get(self, place_id):
        """Get place details (Public)"""
        place = current_app.config['FACADE'].get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place, 200

    @api.expect(place_model, validate=True)
    @jwt_required()
    def put(self, place_id):
        """Update a place (Owner or Admin)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False) #
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        # Admin bypass logic: If not admin AND not the owner -> 403
        if not is_admin and place.owner_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        updated_place = facade.update_place(place_id, request.json)
        return updated_place, 200

    @jwt_required()
    def delete(self, place_id):
        """Delete a place (Owner or Admin)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False) #
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        if not is_admin and place.owner_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_place(place_id)
        return {'message': 'Place deleted successfully'}, 200
