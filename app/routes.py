import os
import redis
from flask import Blueprint, render_template, jsonify, request

bp = Blueprint('routes', __name__)

# Get Redis URL from environment variable
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
r = redis.from_url(REDIS_URL)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/run', methods=['POST'])
def run():
    """Triggers the automattuner process by pushing a job to the Redis queue."""
    try:
        # Push a job to the 'automattuner' queue
        r.lpush('automattuner', '{"action": "run"}')
        return jsonify({'status': 'Job started'})
    except redis.exceptions.ConnectionError as e:
        return jsonify({'status': 'Error connecting to Redis', 'error': str(e)}), 500
