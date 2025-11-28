"""
Blueprint para gestión de turnos de visitantes
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import VisitorTurn
from .utils import normalize_area, normalize_motive, editor_required, admin_required, log_action
from datetime import datetime
from sqlalchemy import func, and_, or_

turns_bp = Blueprint('turns', __name__, url_prefix='/turns')

# ============================================
# VISTAS HTML
# ============================================

@turns_bp.route('/recepcion')
@login_required
def recepcion():
    """Vista de recepción (planta baja) - registrar visitantes"""
    from flask import current_app
    areas = current_app.config.get('AREAS_MUNICIPALES_NORMALIZADAS', [])
    return render_template('turns/recepcion.html', areas=areas)

@turns_bp.route('/area/<area_key>')
@login_required
def area_dashboard(area_key):
    """Dashboard para cada área/piso - ver turnos y gestionar"""
    from flask import current_app
    areas = current_app.config.get('AREAS_MUNICIPALES_NORMALIZADAS', [])
    area = next((a for a in areas if a['key'] == area_key), None)
    
    if not area:
        flash('Área no encontrada', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('turns/area_dashboard.html', area=area, areas=areas)

# ============================================
# API ENDPOINTS
# ============================================

@turns_bp.route('/api/turnos', methods=['GET'])
@login_required
def api_list_turns():
    """Listar turnos con filtros opcionales"""
    # Filtros
    estado = request.args.get('estado')
    area_key = request.args.get('area_key')
    piso = request.args.get('piso')
    dni = request.args.get('dni')
    limit = int(request.args.get('limit', 50))
    
    query = VisitorTurn.query
    
    if estado:
        query = query.filter_by(estado=estado)
    if area_key:
        query = query.filter_by(area_key=area_key)
    if piso:
        query = query.filter_by(piso=piso)
    if dni:
        query = query.filter(VisitorTurn.dni.like(f'%{dni}%'))
    
    # Ordenar por más recientes primero
    turnos = query.order_by(VisitorTurn.hora_llegada.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'data': [t.to_dict() for t in turnos],
        'count': len(turnos)
    })

@turns_bp.route('/api/turnos/en-espera', methods=['GET'])
@login_required
def api_turnos_en_espera():
    """Turnos en espera (para cola de recepción y áreas)"""
    area_key = request.args.get('area_key')
    
    query = VisitorTurn.query.filter(
        or_(
            VisitorTurn.estado == 'ESPERA',
            VisitorTurn.estado == 'AUTORIZADO_SUBIR'
        )
    )
    
    if area_key:
        query = query.filter_by(area_key=area_key)
    
    turnos = query.order_by(VisitorTurn.hora_llegada).all()
    
    return jsonify({
        'success': True,
        'data': [t.to_dict() for t in turnos],
        'count': len(turnos)
    })

@turns_bp.route('/api/turnos', methods=['POST'])
@login_required
def api_create_turn():
    """Crear nuevo turno desde recepción"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('nombre'):
            return jsonify({'success': False, 'message': 'Nombre es requerido'}), 400
        if not data.get('area_key'):
            return jsonify({'success': False, 'message': 'Área es requerida'}), 400
        
        # Normalizar área
        area_key, area_nombre, piso = normalize_area(data.get('area_nombre', ''))
        if data.get('area_key'):  # Si viene area_key directamente, usar ese
            from flask import current_app
            areas = current_app.config.get('AREAS_MUNICIPALES_NORMALIZADAS', [])
            area = next((a for a in areas if a['key'] == data['area_key']), None)
            if area:
                area_key = area['key']
                area_nombre = area['nombre']
                piso = area['piso']
        
        # Normalizar motivo
        motivo_key, motivo_texto = normalize_motive(data.get('motivo_texto'))
        
        # Crear turno
        turno = VisitorTurn(
            nombre=data['nombre'].strip(),
            dni=data.get('dni', '').strip() if data.get('dni') else None,
            area_key=area_key,
            area_nombre=area_nombre,
            piso=piso,
            motivo_key=motivo_key,
            motivo_texto=motivo_texto,
            estado='ESPERA'
        )
        
        db.session.add(turno)
        db.session.commit()
        
        log_action('create', 'visitor_turn', turno.id, f'Turno creado: {turno.nombre} -> {area_nombre}')
        
        return jsonify({
            'success': True,
            'message': 'Turno registrado correctamente',
            'data': turno.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@turns_bp.route('/api/turnos/<int:turno_id>/autorizar', methods=['POST'])
@login_required
def api_autorizar_turno(turno_id):
    """Autorizar subida de visitante"""
    turno = VisitorTurn.query.get_or_404(turno_id)
    
    if turno.estado != 'ESPERA':
        return jsonify({'success': False, 'message': 'El turno no está en espera'}), 400
    
    turno.autorizar_subida()
    log_action('update', 'visitor_turn', turno.id, f'Turno autorizado: {turno.nombre}')
    
    return jsonify({
        'success': True,
        'message': 'Visitante autorizado a subir',
        'data': turno.to_dict()
    })

@turns_bp.route('/api/turnos/<int:turno_id>/atender', methods=['POST'])
@login_required
def api_atender_turno(turno_id):
    """Marcar turno como atendido"""
    turno = VisitorTurn.query.get_or_404(turno_id)
    data = request.get_json() or {}
    
    agente = data.get('atendido_por', current_user.username)
    turno.marcar_atendido(agente)
    
    log_action('update', 'visitor_turn', turno.id, f'Turno atendido por {agente}: {turno.nombre}')
    
    return jsonify({
        'success': True,
        'message': 'Turno marcado como atendido',
        'data': turno.to_dict()
    })

@turns_bp.route('/api/turnos/<int:turno_id>/rechazar', methods=['POST'])
@login_required
def api_rechazar_turno(turno_id):
    """Rechazar turno"""
    turno = VisitorTurn.query.get_or_404(turno_id)
    data = request.get_json() or {}
    
    motivo = data.get('motivo', 'Sin especificar')
    turno.rechazar(motivo)
    
    log_action('update', 'visitor_turn', turno.id, f'Turno rechazado: {turno.nombre} - {motivo}')
    
    return jsonify({
        'success': True,
        'message': 'Turno rechazado',
        'data': turno.to_dict()
    })

@turns_bp.route('/api/dni/<dni>/historial', methods=['GET'])
@login_required
def api_historial_dni(dni):
    """Buscar historial de visitante por DNI (para autocompletar)"""
    turnos = VisitorTurn.query.filter_by(dni=dni).order_by(VisitorTurn.hora_llegada.desc()).limit(5).all()
    
    if not turnos:
        return jsonify({'success': True, 'data': None})
    
    # Retornar último visitante con ese DNI
    ultimo = turnos[0]
    return jsonify({
        'success': True,
        'data': {
            'nombre': ultimo.nombre,
            'dni': ultimo.dni,
            'visitas_previas': len(turnos)
        }
    })

@turns_bp.route('/api/estadisticas/resumen', methods=['GET'])
@login_required
def api_estadisticas_resumen():
    """Resumen de estadísticas de turnos"""
    from datetime import date, timedelta
    
    hoy = date.today()
    
    # Totales
    total_hoy = VisitorTurn.query.filter(
        func.date(VisitorTurn.hora_llegada) == hoy
    ).count()
    
    en_espera = VisitorTurn.query.filter_by(estado='ESPERA').count()
    autorizados = VisitorTurn.query.filter_by(estado='AUTORIZADO_SUBIR').count()
    
    atendidos_hoy = VisitorTurn.query.filter(
        and_(
            func.date(VisitorTurn.hora_llegada) == hoy,
            VisitorTurn.estado == 'ATENDIDO'
        )
    ).count()
    
    # Por área (top 5)
    por_area = db.session.query(
        VisitorTurn.area_nombre,
        func.count(VisitorTurn.id).label('count')
    ).filter(
        func.date(VisitorTurn.hora_llegada) == hoy
    ).group_by(VisitorTurn.area_nombre).order_by(func.count(VisitorTurn.id).desc()).limit(5).all()
    
    return jsonify({
        'success': True,
        'data': {
            'total_hoy': total_hoy,
            'en_espera': en_espera,
            'autorizados': autorizados,
            'atendidos_hoy': atendidos_hoy,
            'por_area': [{'area': a[0], 'count': a[1]} for a in por_area]
        }
    })
