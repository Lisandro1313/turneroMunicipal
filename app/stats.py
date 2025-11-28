"""
Stats Blueprint - Estadísticas y reportes
"""
from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required
from app.models import Organization, Schedule, AuditLog, db
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from calendar import monthrange

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/')
@login_required
def stats_dashboard():
    """Dashboard de estadísticas"""
    return render_template('stats/dashboard.html')

@stats_bp.route('/api/overview')
@login_required
def stats_overview():
    """Estadísticas generales"""
    
    # Total de organizaciones activas
    total_orgs = Organization.query.filter_by(is_active=True).count()
    
    # Total de entregas programadas
    total_schedules = Schedule.query.count()
    
    # Entregas completadas
    delivered_count = Schedule.query.filter_by(delivered=True).count()
    
    # Entregas pendientes
    pending_count = Schedule.query.filter_by(delivered=False).count()
    
    # Kilos totales entregados
    total_kilos_delivered = db.session.query(func.sum(Schedule.kilos))\
        .filter_by(delivered=True).scalar() or 0
    
    # Kilos pendientes
    total_kilos_pending = db.session.query(func.sum(Schedule.kilos))\
        .filter_by(delivered=False).scalar() or 0
    
    # Entregas del mes actual
    today = datetime.now()
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    
    month_delivered = Schedule.query.filter(
        Schedule.delivered == True,
        Schedule.date >= first_day,
        Schedule.date <= last_day
    ).count()
    
    month_kilos = db.session.query(func.sum(Schedule.kilos))\
        .filter(
            Schedule.delivered == True,
            Schedule.date >= first_day,
            Schedule.date <= last_day
        ).scalar() or 0
    
    return jsonify({
        'success': True,
        'data': {
            'organizations': {
                'total': total_orgs
            },
            'schedules': {
                'total': total_schedules,
                'delivered': delivered_count,
                'pending': pending_count,
                'completion_rate': round((delivered_count / total_schedules * 100) if total_schedules > 0 else 0, 2)
            },
            'kilos': {
                'total_delivered': total_kilos_delivered,
                'total_pending': total_kilos_pending,
                'month_delivered': month_kilos
            },
            'current_month': {
                'deliveries': month_delivered,
                'kilos': month_kilos
            }
        }
    })

@stats_bp.route('/api/by-month')
@login_required
def stats_by_month():
    """Estadísticas por mes"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Entregas por mes
    monthly_stats = db.session.query(
        extract('month', Schedule.date).label('month'),
        func.count(Schedule.id).label('total'),
        func.sum(func.cast(Schedule.delivered, db.Integer)).label('delivered'),
        func.sum(Schedule.kilos).label('kilos')
    ).filter(
        extract('year', Schedule.date) == year
    ).group_by(extract('month', Schedule.date)).all()
    
    data = []
    for stat in monthly_stats:
        data.append({
            'month': int(stat.month),
            'month_name': datetime(year, int(stat.month), 1).strftime('%B'),
            'total': stat.total,
            'delivered': stat.delivered or 0,
            'pending': stat.total - (stat.delivered or 0),
            'kilos': stat.kilos or 0
        })
    
    return jsonify({
        'success': True,
        'year': year,
        'data': data
    })

@stats_bp.route('/api/by-organization')
@login_required
def stats_by_organization():
    """Estadísticas por organización"""
    
    stats = db.session.query(
        Organization.id,
        Organization.name,
        Organization.direccion_municipal,
        func.count(Schedule.id).label('total_schedules'),
        func.sum(func.cast(Schedule.delivered, db.Integer)).label('delivered'),
        func.sum(Schedule.kilos).label('total_kilos')
    ).join(Schedule).filter(
        Organization.is_active == True
    ).group_by(Organization.id).all()
    
    data = []
    for stat in stats:
        data.append({
            'id': stat.id,
            'name': stat.name,
            'direccion_municipal': stat.direccion_municipal,
            'total_schedules': stat.total_schedules,
            'delivered': stat.delivered or 0,
            'pending': stat.total_schedules - (stat.delivered or 0),
            'total_kilos': stat.total_kilos or 0,
            'completion_rate': round((stat.delivered or 0) / stat.total_schedules * 100, 2) if stat.total_schedules > 0 else 0
        })
    
    return jsonify({
        'success': True,
        'data': data
    })

@stats_bp.route('/api/by-direccion')
@login_required
def stats_by_direccion():
    """Estadísticas por dirección municipal"""
    
    stats = db.session.query(
        Organization.direccion_municipal,
        func.count(func.distinct(Organization.id)).label('organizations'),
        func.count(Schedule.id).label('total_schedules'),
        func.sum(func.cast(Schedule.delivered, db.Integer)).label('delivered'),
        func.sum(Schedule.kilos).label('total_kilos')
    ).join(Schedule).filter(
        Organization.is_active == True,
        Organization.direccion_municipal.isnot(None)
    ).group_by(Organization.direccion_municipal).all()
    
    data = []
    for stat in stats:
        data.append({
            'direccion': stat.direccion_municipal,
            'organizations': stat.organizations,
            'total_schedules': stat.total_schedules,
            'delivered': stat.delivered or 0,
            'pending': stat.total_schedules - (stat.delivered or 0),
            'total_kilos': stat.total_kilos or 0
        })
    
    return jsonify({
        'success': True,
        'data': data
    })

@stats_bp.route('/api/recent-activity')
@login_required
def recent_activity():
    """Actividad reciente"""
    limit = request.args.get('limit', 20, type=int)
    
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'data': [log.to_dict() for log in logs]
    })

@stats_bp.route('/api/upcoming-deliveries')
@login_required
def upcoming_deliveries():
    """Próximas entregas"""
    days = request.args.get('days', 7, type=int)
    
    end_date = datetime.now().date() + timedelta(days=days)
    
    schedules = Schedule.query.filter(
        Schedule.date >= datetime.now().date(),
        Schedule.date <= end_date,
        Schedule.delivered == False
    ).order_by(Schedule.date).all()
    
    return jsonify({
        'success': True,
        'data': [schedule.to_dict() for schedule in schedules]
    })
