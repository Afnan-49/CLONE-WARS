from flask_restx import Namespace, Resource, fields
from flask import request

from app.services.facade import facade

api = Namespace("reviews", description="Review operations")

review_input = api.model("ReviewInput", {
    "text": fields.String(required=True),
    "rating": fields.Integer(required=True, description="1..5"),
    "user_id": fields.String(required=True),
    "place_id": fields.String(required=True),
})

review_update = api.model("ReviewUpdate", {
    "text": fields.String(required=False),
    "rating": fields.Integer(required=False, description="1..5"),
})

review_output = api.model("Review", {
    "id": fields.String(readOnly=True),
    "text": fields.String,
    "rating": fields.Integer,
    "user": fields.Nested(api.model("ReviewUserOut", {
        "id": fields.String,
        "first_name": fields.String,
        "last_name": fields.String,
        "email": fields.String,
    })),
    "place_id": fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
})

def serialize_review(r):
    u = r.user
    return {
        "id": r.id,
        "text": r.text,
        "rating": r.rating,
        "user": {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
        } if u else None,
        "place_id": r.place.id if r.place else None,
        "created_at": r.created_at.isoformat(),
        "updated_at": r.updated_at.isoformat(),
    }

@api.route("/")
class ReviewList(Resource):

    @api.marshal_list_with(review_output)
    def get(self):
        reviews = facade.list_reviews()
        return [serialize_review(r) for r in reviews], 200

    @api.expect(review_input, validate=True)
    @api.marshal_with(review_output, code=201)
    def post(self):
        try:
            review = facade.create_review(request.json or {})
            return serialize_review(review), 201
        except ValueError as e:
            api.abort(400, str(e))

@api.route("/<string:review_id>")
class ReviewItem(Resource):

    @api.marshal_with(review_output)
    def get(self, review_id):
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")
        return serialize_review(review), 200

    @api.expect(review_update, validate=True)
    @api.marshal_with(review_output)
    def put(self, review_id):
        try:
            review = facade.update_review(review_id, request.json or {})
            if not review:
                api.abort(404, "Review not found")
            return serialize_review(review), 200
        except ValueError as e:
            api.abort(400, str(e))

    def delete(self, review_id):
        deleted = facade.delete_review(review_id)
        if not deleted:
            api.abort(404, "Review not found")
        return {"message": "Review deleted"}, 200


#  list reviews for a specific place
@api.route("/places/<string:place_id>/reviews")
class PlaceReviews(Resource):

    @api.marshal_list_with(review_output)
    def get(self, place_id):
        try:
            reviews = facade.list_reviews_by_place(place_id)
            return [serialize_review(r) for r in reviews], 200
        except ValueError as e:
            api.abort(404, str(e))
