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
    "amenity_ids": fields.List(fields.String, required=False, description="List of amenity IDs"),
})

review_in_place = api.model("ReviewInPlace", {
    "id": fields.String,
    "text": fields.String,
    "rating": fields.Integer,
    "user_id": fields.String,
})
place_output = api.model("Place", {
    "id": fields.String(readOnly=True),
    "title": fields.String,
    "description": fields.String,
    "price": fields.Float,
    "latitude": fields.Float,
    "longitude": fields.Float,

    # owner details returned
    "owner": fields.Nested(api.model("OwnerOut", {
        "id": fields.String,
        "first_name": fields.String,
        "last_name": fields.String,
        "email": fields.String,
    })),

    # amenities returned as list of objects
    "amenities": fields.List(fields.Nested(api.model("AmenityOut", {
        "id": fields.String,
        "name": fields.String,
    }))),

    "created_at": fields.String,
    "updated_at": fields.String,

    "reviews": fields.List(fields.Nested(review_in_place)),
})

def serialize_place(p):
    owner = p.owner
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "price": p.price,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "owner": {
            "id": owner.id,
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "email": owner.email,
        } if owner else None,
        "amenities": [{"id": a.id, "name": a.name} for a in (p.amenities or [])],
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),

        "reviews": [
    {
        "id": r.id,
        "text": r.text,
        "rating": r.rating,
        "user_id": r.user.id if r.user else None,
    }
    for r in (getattr(p, "reviews", []) or [])
],
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

    @api.expect(place_input, validate=True)
    @api.marshal_with(place_output)
    def put(self, place_id):
        try:
            place = facade.update_place(place_id, request.json or {})
            if not place:
                api.abort(404, "Place not found")
            return serialize_place(place), 200
        except ValueError as e:
            api.abort(400, str(e))
