from flask_restx import Namespace, Resource, fields
from flask import request

from app.services.facade import facade

api = Namespace("places", description="Place operations")

place_input = api.model("PlaceInput", {
    "title": fields.String(required=True),
    "description": fields.String(required=False),
    "price": fields.Float(required=True),
    "latitude": fields.Float(required=True),
    "longitude": fields.Float(required=True),
    "owner_id": fields.String(required=True),

})
place_update = api.model("PlaceUpdate", {
    "title": fields.String(required=False),
    "description": fields.String(required=False),
    "price": fields.Float(required=False),
    "latitude": fields.Float(required=False),
    "longitude": fields.Float(required=False),
    "owner_id": fields.String(required=False),
})

review_in_place = api.model("ReviewInPlace", {
    "id": fields.String,
    "text": fields.String,
    "rating": fields.Integer,
    "user_id": fields.String,
})
place_output = api.model("PlaceOutput", {
    "id": fields.String(readOnly=True),
    "title": fields.String(required=True),
    "description": fields.String,
    "price": fields.Float(required=True),
    "latitude": fields.Float(required=True),
    "longitude": fields.Float(required=True),
    "owner_id": fields.String(required=True),
    "created_at": fields.String,
    "updated_at": fields.String,
})

def serialize_place(p):
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "price": p.price,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "owner_id": p.owner_id,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }

@api.route("/")
class PlaceList(Resource):

    @api.marshal_list_with(place_output)
    def get(self):
        places = facade.list_places()
        return [serialize_place(p) for p in places], 200

    @api.expect(place_input, validate=True)
    @api.marshal_with(place_output, code=201)
    def post(self):
        try:
            place = facade.create_place(request.json or {})
            return serialize_place(place), 201
        except ValueError as e:
            api.abort(400, str(e))

@api.route("/<string:place_id>")
class PlaceItem(Resource):

    @api.marshal_with(place_output)
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, "Place not found")
        return serialize_place(place), 200

    @api.expect(place_update, validate=True)
    @api.marshal_with(place_output)
    def put(self, place_id):
        try:
            place = facade.update_place(place_id, request.json or {})
            if not place:
                api.abort(404, "Place not found")
            return serialize_place(place), 200
        except ValueError as e:
            api.abort(400, str(e))
