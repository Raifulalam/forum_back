# app/routes.py

from flask import Blueprint
from .ranking import get_users, get_activities, update_points

ranking_bp = Blueprint('ranking', __name__)

ranking_bp.route('/api/users', methods=['GET'])(get_users)
ranking_bp.route('/api/activities', methods=['GET'])(get_activities)
ranking_bp.route('/api/update', methods=['POST'])(update_points)
