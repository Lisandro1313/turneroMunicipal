"""
Sistema de notificaciones push para la app mobile
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from . import db
from datetime import datetime
import requests

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

class DeviceToken(db.Model):
    """Tokens de dispositivos para notificaciones push"""
    __tablename__ = 'device_token'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(500), nullable=False, unique=True)
    platform = db.Column(db.String(20), nullable=False)  # 'ios' o 'android'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@notifications_bp.route('/register-token', methods=['POST'])
@login_required
def register_token():
    """Registrar token de notificaciones push del dispositivo"""
    data = request.get_json()
    token = data.get('token')
    platform = data.get('platform')  # 'ios' o 'android'
    
    if not token or not platform:
        return jsonify({'success': False, 'message': 'Token y platform son requeridos'}), 400
    
    # Buscar o crear token
    device = DeviceToken.query.filter_by(token=token).first()
    if device:
        device.user_id = current_user.id
        device.updated_at = datetime.utcnow()
        device.is_active = True
    else:
        device = DeviceToken(
            user_id=current_user.id,
            token=token,
            platform=platform
        )
        db.session.add(device)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Token registrado correctamente',
        'data': device.to_dict()
    })

@notifications_bp.route('/unregister-token', methods=['POST'])
@login_required
def unregister_token():
    """Desregistrar token cuando el usuario cierra sesión"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'success': False, 'message': 'Token es requerido'}), 400
    
    device = DeviceToken.query.filter_by(token=token, user_id=current_user.id).first()
    if device:
        device.is_active = False
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Token desregistrado'})

@notifications_bp.route('/test', methods=['POST'])
@login_required
def test_notification():
    """Endpoint para probar notificaciones"""
    data = request.get_json()
    title = data.get('title', 'Test Notification')
    body = data.get('body', 'Esta es una notificación de prueba')
    
    from .push_service import send_push_notification
    result = send_push_notification(current_user.id, title, body)
    
    return jsonify({
        'success': True,
        'message': 'Notificación enviada',
        'result': result
    })


def send_push_notification(user_id, title, body, data=None):
    """
    Enviar notificación push a un usuario específico
    Usa Expo Push Notifications (gratuito y fácil)
    """
    tokens = DeviceToken.query.filter_by(user_id=user_id, is_active=True).all()
    
    if not tokens:
        return {'success': False, 'message': 'No hay tokens registrados para este usuario'}
    
    expo_tokens = [t.token for t in tokens if t.token.startswith('ExponentPushToken')]
    
    if not expo_tokens:
        return {'success': False, 'message': 'No hay tokens de Expo válidos'}
    
    # Preparar mensajes para Expo
    messages = []
    for token in expo_tokens:
        messages.append({
            'to': token,
            'sound': 'default',
            'title': title,
            'body': body,
            'data': data or {},
            'priority': 'high',
            'channelId': 'default',
        })
    
    try:
        # Enviar a Expo Push API
        response = requests.post(
            'https://exp.host/--/api/v2/push/send',
            json=messages,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.text}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def notify_new_turn(turn):
    """Notificar a usuarios del piso cuando hay un nuevo turno"""
    from .models import User
    
    # Buscar usuarios del piso correspondiente
    piso_role = f'piso{turn.piso}'
    users = User.query.filter_by(role=piso_role, is_active=True).all()
    
    results = []
    for user in users:
        result = send_push_notification(
            user.id,
            f'🔔 Nuevo turno - {turn.area_nombre}',
            f'{turn.nombre} está esperando en recepción',
            data={
                'type': 'new_turn',
                'turn_id': turn.id,
                'piso': turn.piso,
                'area': turn.area_nombre,
                'screen': 'PisoScreen'
            }
        )
        results.append(result)
    
    return results


def notify_turn_authorized(turn):
    """Notificar cuando un turno es autorizado a subir"""
    from .models import User
    
    piso_role = f'piso{turn.piso}'
    users = User.query.filter_by(role=piso_role, is_active=True).all()
    
    results = []
    for user in users:
        result = send_push_notification(
            user.id,
            f'✅ Visitante autorizado',
            f'{turn.nombre} está subiendo al piso {turn.piso}',
            data={
                'type': 'turn_authorized',
                'turn_id': turn.id,
                'piso': turn.piso,
                'screen': 'PisoScreen'
            }
        )
        results.append(result)
    
    return results


def notify_chat_message(mensaje):
    """Notificar cuando hay un nuevo mensaje en el chat"""
    from .models import User
    
    # Notificar a todos los usuarios activos excepto al que envió el mensaje
    users = User.query.filter(User.is_active == True, User.username != mensaje.usuario).all()
    
    results = []
    for user in users:
        result = send_push_notification(
            user.id,
            f'💬 Mensaje de {mensaje.usuario}',
            mensaje.mensaje[:100],  # Limitar a 100 caracteres
            data={
                'type': 'chat_message',
                'message_id': mensaje.id,
                'origen': mensaje.origen,
                'screen': 'ChatScreen'
            }
        )
        results.append(result)
    
    return results
