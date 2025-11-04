from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import sqlalchemy as sa
from app import db
from app.models.topic import Topic
from app.models.user import User
from app.utils.schemas import TopicSchema

topics_bp = Blueprint('topics', __name__)

topic_schema = TopicSchema()
topics_schema = TopicSchema(many=True)


# -----------------------
# GET ALL TOPICS
# -----------------------
@topics_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_topics():
    """Get all available topics with optional search"""
    search = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = Topic.query

    # Search by topic name
    if search:
        query = query.filter(Topic.name.ilike(f'%{search}%'))

    # Order by name
    query = query.order_by(Topic.name)

    # Paginate
    topics = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'topics': topics_schema.dump(topics.items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': topics.total,
            'pages': topics.pages,
            'has_next': topics.has_next,
            'has_prev': topics.has_prev
        }
    })


# -----------------------
# GET SINGLE TOPIC
# -----------------------
@topics_bp.route('/<topic_id>', methods=['GET'])
@jwt_required()
def get_topic(topic_id):
    """Get a single topic by ID"""
    topic = Topic.query.get_or_404(topic_id)
    return jsonify({'topic': topic_schema.dump(topic)})


# -----------------------
# GET TOPIC BY NAME
# -----------------------
@topics_bp.route('/name/<topic_name>', methods=['GET'])
@jwt_required()
def get_topic_by_name(topic_name):
    """Get a single topic by name"""
    topic = Topic.query.filter_by(name=topic_name).first_or_404()
    return jsonify({'topic': topic_schema.dump(topic)})


# -----------------------
# FOLLOW TOPIC
# -----------------------
@topics_bp.route('/<topic_id>/follow', methods=['POST'])
@jwt_required()
def follow_topic(topic_id):
    """Follow a topic"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Find the topic
    topic = Topic.query.get_or_404(topic_id)

    # Check if already following
    if topic in user.topics:
        return jsonify({'message': 'Already following this topic'}), 200

    # Add topic to user's followed topics
    user.topics.append(topic)

    try:
        db.session.commit()
        return jsonify({
            'message': f'Successfully followed {topic.name}',
            'topic': topic_schema.dump(topic)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to follow topic', 'details': str(e)}), 500


# -----------------------
# UNFOLLOW TOPIC
# -----------------------
@topics_bp.route('/<topic_id>/unfollow', methods=['DELETE'])
@jwt_required()
def unfollow_topic(topic_id):
    """Unfollow a topic"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Find the topic
    topic = Topic.query.get_or_404(topic_id)

    # Check if user is following
    if topic not in user.topics:
        return jsonify({'error': 'Not following this topic'}), 404

    # Remove topic from user's followed topics
    user.topics.remove(topic)

    try:
        db.session.commit()
        return jsonify({
            'message': f'Successfully unfollowed {topic.name}'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to unfollow topic', 'details': str(e)}), 500


# -----------------------
# GET USER'S FOLLOWED TOPICS
# -----------------------
@topics_bp.route('/following', methods=['GET'])
@jwt_required()
def get_followed_topics():
    """Get all topics the current user is following"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    return jsonify({
        'topics': topics_schema.dump(user.topics),
        'total': len(user.topics)
    })


# -----------------------
# CHECK IF FOLLOWING TOPIC
# -----------------------
@topics_bp.route('/<topic_id>/is-following', methods=['GET'])
@jwt_required()
def is_following_topic(topic_id):
    """Check if the current user is following a specific topic"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    topic = Topic.query.get_or_404(topic_id)

    is_following = topic in user.topics

    return jsonify({
        'topic_id': topic.id,
        'topic_name': topic.name,
        'is_following': is_following
    })


# -----------------------
# GET ARTICLES FOR A TOPIC
# -----------------------
@topics_bp.route('/<topic_id>/articles', methods=['GET'])
@jwt_required()
def get_topic_articles(topic_id):
    """Get all articles for a specific topic"""
    from app.models.article import Article
    from app.utils.schemas import ArticleSchema
    from sqlalchemy import desc

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # Verify topic exists
    topic = Topic.query.get_or_404(topic_id)

    # Get articles for this topic
    articles = Article.query.join(Article.topics) \
        .filter(Topic.id == topic_id) \
        .order_by(desc(Article.timestamp)) \
        .paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    articles_schema = ArticleSchema(many=True)

    return jsonify({
        'topic': topic_schema.dump(topic),
        'articles': articles_schema.dump(articles.items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': articles.total,
            'pages': articles.pages,
            'has_next': articles.has_next,
            'has_prev': articles.has_prev
        }
    })