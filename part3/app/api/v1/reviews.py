from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app

api = Namespace('reviews', description='Review operations')

# Review model for input/output
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating (1-5)'),
    'user_id': fields.String(readOnly=True, description='ID of the reviewer'),
    'place_id': fields.String(required=True, description='ID of the place being reviewed')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model, validate=True)
    @api.marshal_with(review_model, code=201)
    @jwt_required()
    def post(self):
        """Create a new review (Protected)"""
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        review_data = api.payload

        # 1. Fetch the place to check ownership
        place = facade.get_place(review_data['place_id'])
        if not place:
            api.abort(404, "Place not found")

        # 2. Rule: You cannot review your own place
        if place.owner_id == current_user_id:
            return {'error': 'You cannot review your own place'}, 400

        # 3. Rule: No duplicate reviews from the same user
        existing_reviews = facade.get_reviews_by_place(review_data['place_id'])
        for r in existing_reviews:
            if r.user_id == current_user_id:
                return {'error': 'You have already reviewed this place'}, 400

        # Create the review
        review_data['user_id'] = current_user_id
        new_review = facade.create_review(review_data)
        return new_review, 201

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.marshal_with(review_model)
    def get(self, review_id):
        """Get review details by ID (Public)"""
        facade = current_app.config['FACADE']
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")
        return review

    @api.expect(review_model, validate=True)
    @jwt_required()
    def put(self, review_id):
        """Update a review (Protected - Owner only)"""
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        review = facade.get_review(review_id)

        if not review:
            api.abort(404, "Review not found")

        # 4. Authorization Check: Only the creator can edit
        if review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        updated_review = facade.update_review(review_id, api.payload)
        return updated_review, 200

    @jwt_required()
    def delete(self, review_id):
        """Delete a review (Protected - Owner only)"""
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        review = facade.get_review(review_id)

        if not review:
            api.abort(404, "Review not found")

        # 5. Authorization Check: Only the creator can delete
        if review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200
