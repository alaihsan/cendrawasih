from flask import jsonify, request
from flask_login import current_user, login_required
from app.blueprints.api import bp
from app.models.notification import Notification
from app import db

@bp.route('/notifications')
@login_required
def get_notifications():
    """Get unread notifications for current user"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'type': n.type,
        'link': n.link,
        'created_at': n.created_at.isoformat()
    } for n in notifications])

@bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    """Mark a notification as read"""
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})
