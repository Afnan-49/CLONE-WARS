from flask_restx import Namespace, Resource, fields
from flask import request

from app.services.facade import facade  # facade instance (Singleton)

api = Namespace("amenities", description="Amenity operations")

amenity_input = api.model("AmenityInput", {
    "name": fields.String(required=True),
})

amenity_output = api.model("Amenity", {
    "id": fields.String(readOnly=True),
    "name": fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,

})

def serialize_amenity(a):
    return {
        "id": a.id,
        "name": a.name,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),        
    }

@api.route("/")
class AmenityList(Resource):

    @api.marshal_list_with(amenity_output)
    def get(self):
        amenities = facade.list_amenities()
        return [serialize_amenity(a) for a in amenities], 200

    @api.expect(amenity_input, validate=True)
    @api.marshal_with(amenity_output, code=201)
    def post(self):
        try:
            amenity = facade.create_amenity(request.json or {})
            return serialize_amenity(amenity), 201
        except ValueError as e:
            api.abort(400, str(e))

@api.route("/<string:amenity_id>")
class AmenityItem(Resource):

    @api.marshal_with(amenity_output)
    def get(self, amenity_id):
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, "Amenity not found")
        return serialize_amenity(amenity), 200

    @api.expect(amenity_input, validate=True)
    @api.marshal_with(amenity_output)
    def put(self, amenity_id):
        try:
            amenity = facade.update_amenity(amenity_id, request.json or {})
            if not amenity:
                api.abort(404, "Amenity not found")
            return serialize_amenity(amenity), 200
        except ValueError as e:
            api.abort(400, str(e))
