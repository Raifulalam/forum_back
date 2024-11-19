from flask import Blueprint
from .report import get_reports, add_reports, delete_report, approve_report

report_bp = Blueprint('report', __name__)

report_bp.route('/reports', methods=['GET'])(get_reports)
report_bp.route('/reports', methods=['POST'])(add_reports)
report_bp.route('/reports/<report_id>', methods=['DELETE'])(delete_report)
report_bp.route('/reports/approve/<report_id>', methods=['POST'])(approve_report)  # Register the approve function
