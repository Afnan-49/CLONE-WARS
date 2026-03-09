from flask import current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    def get(self):
        """Retrieve all amenities (Public)"""
        return current_app.config['FACADE'].get_all_amenities(), 200

    @jwt_required()
    @api.expect(amenity_model)
    def post(self):
        """Add a new amenity (Admin Only)"""
        token_claims = get_jwt()
        if not token_claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        new_amenity = current_app.config['FACADE'].create_amenity(api.payload)
        return new_amenity, 201

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    def get(self, amenity_id):
        """Get amenity details (Public)"""
        amenity = current_app.config['FACADE'].get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity, 200

    @jwt_required()
    @api.expect(amenity_model)
    def put(self, amenity_id):
        """Update an amenity (Admin Only)"""
        token_claims = get_jwt()
        if not token_claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        updated_amenity = current_app.config['FACADE'].update_amenity(amenity_id, api.payload)
        if not updated_amenity:
            return {'error': 'Amenity not found'}, 404
        return updated_amenity, 200
