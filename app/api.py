"""
API Blueprint - Endpoints REST para la aplicación
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Organization, Schedule, AuditLog, db
from app.utils import log_action, admin_required
from datetime import datetime, date
from sqlalchemy import func

api_bp = Blueprint('api', __name__)

@api_bp.route('/organizations', methods=['GET'])
@login_required
def get_organizations():
    """Obtener todas las organizaciones"""
    organizations = Organization.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'data': [org.to_dict() for org in organizations]
    })

@api_bp.route('/organizations/<int:org_id>', methods=['GET'])
@login_required
def get_organization(org_id):
    """Obtener una organización específica"""
    org = Organization.query.get_or_404(org_id)
    return jsonify({
        'success': True,
        'data': org.to_dict()
    })

@api_bp.route('/organizations', methods=['POST'])
@login_required
def create_organization():
    """Crear nueva organización"""
    data = request.get_json()
    
    try:
        org = Organization(
            name=data.get('name'),
            representative=data.get('representative'),
            address=data.get('address'),
            phone=data.get('phone'),
            email=data.get('email'),
            direccion_municipal=data.get('direccion_municipal'),
            tipo_organizacion=data.get('tipo_organizacion'),
            kilos=data.get('kilos'),
            frequency=data.get('frequency', 'mensual'),
            day_of_week=data.get('day_of_week'),
            day_of_month=data.get('day_of_month'),
            notes=data.get('notes')
        )
        
        db.session.add(org)
        db.session.commit()
        
        log_action(current_user.id, 'create', 'organization', org.id, f"Creada organización: {org.name}")
        
        return jsonify({
            'success': True,
            'message': 'Organización creada exitosamente',
            'data': org.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear organización: {str(e)}'
        }), 400

@api_bp.route('/organizations/<int:org_id>', methods=['PUT'])
@login_required
def update_organization(org_id):
    """Actualizar organización"""
    org = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    try:
        for field in ['name', 'representative', 'address', 'phone', 'email', 
                      'direccion_municipal', 'tipo_organizacion', 'kilos', 
                      'frequency', 'day_of_week', 'day_of_month', 'notes']:
            if field in data:
                setattr(org, field, data[field])
        
        db.session.commit()
        
        log_action(current_user.id, 'update', 'organization', org.id, f"Actualizada organización: {org.name}")
        
        return jsonify({
            'success': True,
            'message': 'Organización actualizada exitosamente',
            'data': org.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar organización: {str(e)}'
        }), 400

@api_bp.route('/organizations/<int:org_id>', methods=['DELETE'])
@login_required
def delete_organization(org_id):
    """Eliminar (desactivar) organización"""
    org = Organization.query.get_or_404(org_id)
    
    try:
        org.is_active = False
        db.session.commit()
        
        log_action(current_user.id, 'delete', 'organization', org.id, f"Desactivada organización: {org.name}")
        
        return jsonify({
            'success': True,
            'message': 'Organización eliminada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar organización: {str(e)}'
        }), 400

@api_bp.route('/schedules', methods=['GET'])
@login_required
def get_schedules():
    """Obtener cronogramas con filtros opcionales"""
    # Parámetros de filtro
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    org_id = request.args.get('organization_id', type=int)
    delivered = request.args.get('delivered')
    
    query = Schedule.query
    
    if start_date:
        query = query.filter(Schedule.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Schedule.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if org_id:
        query = query.filter_by(organization_id=org_id)
    if delivered is not None:
        query = query.filter_by(delivered=delivered.lower() == 'true')
    
    schedules = query.order_by(Schedule.date).all()
    
    return jsonify({
        'success': True,
        'data': [schedule.to_dict() for schedule in schedules]
    })

@api_bp.route('/schedules/<int:schedule_id>/deliver', methods=['POST'])
@login_required
def mark_delivered(schedule_id):
    """Marcar entrega como realizada"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    try:
        schedule.mark_delivered(current_user.id)
        
        log_action(current_user.id, 'deliver', 'schedule', schedule.id, 
                  f"Entrega marcada para {schedule.organization.name} - {schedule.date}")
        
        return jsonify({
            'success': True,
            'message': 'Entrega marcada exitosamente',
            'data': schedule.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al marcar entrega: {str(e)}'
        }), 400

@api_bp.route('/schedules/<int:schedule_id>/undeliver', methods=['POST'])
@login_required
def mark_undelivered(schedule_id):
    """Desmarcar entrega"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    try:
        schedule.delivered = False
        schedule.delivered_at = None
        schedule.delivered_by = None
        db.session.commit()
        
        log_action(current_user.id, 'undeliver', 'schedule', schedule.id, 
                  f"Entrega desmarcada para {schedule.organization.name} - {schedule.date}")
        
        return jsonify({
            'success': True,
            'message': 'Entrega desmarcada exitosamente',
            'data': schedule.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al desmarcar entrega: {str(e)}'
        }), 400
