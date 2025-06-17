from flask import Blueprint, request, jsonify
from schemas import UserSchema
from app.services.auth_service import signup_user,login_user
from marshmallow import ValidationError

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = user_schema.load(request.get_json())
        result = signup_user(data['phone'],data['email'], data['password'])
        return jsonify(result), result.get("status", 400)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = user_schema.load(request.get_json())
        result = login_user(data['email'], data['password'])
        return jsonify(result), result.get("status", 400)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
