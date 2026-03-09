from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import current_app, request

api = Namespace('reviews', description='Review operations')

# Review model for input/output validation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating (1-5)'),
    'user_id': fields.String(readOnly=True, description='ID of the reviewer'),
    'place_id': fields.String(required=True, description='ID of the place being reviewed')
})

@api.route('/')
class ReviewList(Resource):
    @api.marshal_list_with(review_model)
    def get(self):
        """Retrieve all reviews (Public)"""
        facade = current_app.config['FACADE']
        return facade.get_all_reviews(), 200

    @api.expect(review_model, validate=True)
    @api.marshal_with(review_model, code=201)
    @jwt_required()
    def post(self):
        """Create a new review (Protected)"""
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        review_data = request.json

        # 1. Check if the place exists
        place = facade.get_place(review_data['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404

        # 2. Rule: You cannot review your own place
        if place.owner_id == current_user_id:
            return {'error': 'You cannot review your own place'}, 400

        # 3. Rule: One review per place per user
        existing_reviews = facade.get_reviews_by_place(review_data['place_id'])
        for r in existing_reviews:
            if r.user_id == current_user_id:
                return {'error': 'You have already reviewed this place'}, 400

        review_data['user_id'] = current_user_id
        new_review = facade.create_review(review_data)
        return new_review, 201

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.marshal_with(review_model)
    def get(self, review_id):
        """Get review details (Public)"""
        facade = current_app.config['FACADE']
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review, 200

    @api.expect(review_model, validate=True)
    @jwt_required()
    def put(self, review_id):
        """Update a review (Creator or Admin)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        # Admin bypass logic: If not admin AND not creator -> 403
        if not is_admin and review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        updated_review = facade.update_review(review_id, request.json)
        return updated_review, 200

    @jwt_required()
    def delete(self, review_id):
        """Delete a review (Creator or Admin)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        current_user_id = get_jwt_identity()
        facade = current_app.config['FACADE']
        
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200
