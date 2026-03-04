from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import facade

api = Namespace("users", description="User operations")

# This model defines what the API expects when creating a user
user_input = api.model("UserInput", {
    "first_name": fields.String(required=True, description="User first name"),
    "last_name": fields.String(required=True, description="User last name"),
    "email": fields.String(required=True, description="User email"),
    "password": fields.String(required=True, description="User password"),
})

# This model defines what the API expects when updating a user
user_update = api.model("UserUpdate", {
    "first_name": fields.String(required=False),
    "last_name": fields.String(required=False),
    "email": fields.String(required=False),
    "password": fields.String(required=False),
    "is_admin": fields.Boolean(required=False),
})

# IMPORTANT: This model defines what is sent BACK to the user.
# Note that "password" is NOT included here for security.
user_output = api.model("User", {
    "id": fields.String(readOnly=True),
    "first_name": fields.String,
    "last_name": fields.String,
    "email": fields.String,
    "is_admin": fields.Boolean,
    "created_at": fields.String,
    "updated_at": fields.String,
})

def serialize_user(u):
    """Converts a User object into a dictionary for JSON responses, excluding sensitive data."""
    return {
        "id": u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "is_admin": u.is_admin,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "updated_at": u.updated_at.isoformat() if u.updated_at else None,
    }

@api.route("/")
class UserList(Resource):

    @api.marshal_list_with(user_output)
    def get(self):
        """Fetch all users (Passwords are automatically excluded by user_output)"""
        users = facade.user_repo.get_all()
        return [serialize_user(u) for u in users], 200

    @api.expect(user_input, validate=True)
    @api.marshal_with(user_output, code=201)
    def post(self):
        """Create a new user with a hashed password"""
        try:
            # The facade.create_user method should handle the hashing
            user = facade.create_user(request.json or {})
            return serialize_user(user), 201
        except ValueError as e:
            api.abort(400, str(e))

@api.route("/<string:user_id>")
class UserItem(Resource):

    @api.marshal_with(user_output)
    def get(self, user_id):
        """Fetch a single user by ID"""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "User not found")
        return serialize_user(user), 200

    @api.expect(user_update, validate=True)
    @api.marshal_with(user_output)
    def put(self, user_id):
        """Update user details"""
        try:
            user = facade.update_user(user_id, request.json or {})
            if not user:
                api.abort(404, "User not found")
            return serialize_user(user), 200
        except ValueError as e:
            api.abort(400, str(e))
