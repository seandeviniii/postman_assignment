# from app.api import bp
# from app import db
from app.models import User
from app.api.errors import bad_request
from flask import jsonify, url_for, request
from app.api import bp
from app import db
from app.api.auth import token_auth
import re

# Get a specific user by id
@bp.route('/v1/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


# Registration of a user.
# Check for CSRF attacks and regex on username,email,pass.
@bp.route('/v1/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if re.match("^[a-zA-Z0-9_.-]+$", data['username']) is None or data['username'].len()>64:
        return bad_request('Characters allowed:[alphabets,numbers,_,.,-]. Max length: 64')
    if re.match("^.+@([?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", data['email']) is None or data['email'].len()>120:
        return bad_request('Valid email required and Max length: 120')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response