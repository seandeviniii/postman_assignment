# from app.api import bp
# from app import db
from app.models import User, Tweet
from app.api.errors import bad_request
from flask import jsonify, url_for, request, g
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
@bp.route('/v1/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if re.match("^[a-zA-Z0-9_.-]+$", data['username']) is None or len(data['username'])>64:
        return bad_request('Characters allowed:[alphabets,numbers,_,.,-]. Max length: 64')
    if re.search(r'\w+@\w+', data['email']) is None or len(data['email'])>120:
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

# Following a user
@bp.route('/v1/follows', methods=['POST'])
@token_auth.login_required
def follow():
    data = request.get_json() or {}
    if 'follower_id' not in data or 'followed_id' not in data:
        return bad_request('must include id of follower and followed user.')
    try:
        follower_id = int(data['follower_id'])
        followed_id = int(data['followed_id'])
        if follower_id == followed_id:
            return bad_request('User cannot follow himself.')
        u1 = User.query.filter_by(id=follower_id).first()
        u2 = User.query.filter_by(id=followed_id).first()
        if u1 is None or u2 is None:
            return bad_request('User does not exist.')
        if u1.is_following(u2):
            return bad_request('{} already follows {}'.format(follower_id, followed_id))
        else:
            u1.follow(u2)
            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()
            return jsonify({
                "status" : 200,
                "response" : '{} now follows {}'.format(follower_id, followed_id)
                })
    except (ValueError):
        return bad_request('Please provide integer ids.')


# Unfollowing a user
@bp.route('/v1/unfollows', methods=['POST'])
@token_auth.login_required
def unfollow():
    data = request.get_json() or {}
    if 'follower_id' not in data or 'followed_id' not in data:
        return bad_request('must include id of follower and followed user.')
    try:
        follower_id = int(data['follower_id'])
        followed_id = int(data['followed_id'])
        if follower_id == followed_id:
            return bad_request('User cannot unfollow himself.')
        u1 = User.query.filter_by(id=follower_id).first()
        u2 = User.query.filter_by(id=followed_id).first()
        if u1 is None or u2 is None:
            return bad_request('User does not exist.')
        if u1.is_following(u2):
            u1.unfollow(u2)
            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()
            return jsonify({
                "status": 200,
                "response": "{} unfollowed {}".format(follower_id, followed_id)
            }) 
        else:
            return bad_request("{} already does not follow {}".format(follower_id, followed_id))
    except (ValueError):
        return bad_request('Please provide integer ids.')

# Creating a tweet
@bp.route('/v1/tweet/<int:id>', methods=['GET'])
@token_auth.login_required
def return_tweet(id):
    t = Tweet.query.filter_by(id=id).first()
    if t is not None:
        return jsonify(t.to_dict())
    return bad_request("No tweet had id:{}".format(id))


# deleting a tweet
@bp.route('/v1/delete_tweet/<int:id>', methods=['POST'])
@token_auth.login_required
def delete_tweet(id):
    t = Tweet.query.filter_by(id=id).first()
    if t is not None:
        db.session.delete(t)
        db.session.commit()
        return jsonify({
            'status_code': 200,
            'response': 'Item with id:{} deleted.'.format(id)
        })
    return bad_request("No tweet had id:{}".format(id))


# Creating a tweet
@bp.route('/v1/create_tweet', methods=['POST'])
@token_auth.login_required
def create_tweet():
    data = request.get_json() or {}
    if 'body' not in data:
        return bad_request('Body of data not supplied')
    t = Tweet(body = data['body'], user_id=g.current_user.id)
    db.session.add(t)
    db.session.commit()
    return jsonify({
        'status_code': 200,
        'response':'Tweet Created.',
        'body': data['body']
    })

# Showing followers of a given username
@bp.route('/v1/followers/<string:username>')
@token_auth.login_required
def show_followers(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        return bad_request('User does not exist.')
    data = []
    all_followers = u.followers.all()
    for f in all_followers:
        data.append(f.username)
    return jsonify({
        "followers": data
    })
