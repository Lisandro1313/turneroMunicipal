"""
Blueprint para gestión de turnos de visitantes
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import VisitorTurn
from .utils import normalize_area, normalize_motive
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
    # Solo admin y recepcion pueden acceder
    if current_user.role not in ['admin', 'recepcion']:
        flash('No tienes acceso a esta sección', 'error')
        return redirect(url_for('turns.piso_llamado', numero=1))
    
    from flask import current_app
    areas = current_app.config.get('AREAS_MUNICIPALES_NORMALIZADAS', [])
    return render_template('turns/recepcion.html', areas=areas)

@turns_bp.route('/area/<area_key>')
@login_required
def area_dashboard(area_key):
    """Dashboard para cada área/piso - ver turnos y gestionar"""
    # Solo admin puede acceder a gestión por área
    if current_user.role != 'admin':
        flash('No tienes acceso a esta sección', 'error')
        if current_user.role == 'recepcion':
            return redirect(url_for('turns.recepcion'))
        else:  # pisos
            return redirect(url_for('turns.piso_llamado', numero=1))
    
    from flask import current_app
    areas = current_app.config.get('AREAS_MUNICIPALES_NORMALIZADAS', [])
    area = next((a for a in areas if a['key'] == area_key), None)
    
    if not area:
        flash('Área no encontrada', 'error')
        return redirect(url_for('turns.recepcion'))
    
    return render_template('turns/area_dashboard.html', area=area, areas=areas)

@turns_bp.route('/piso/<int:numero>')
@login_required
def piso_llamado(numero):
    """Vista de llamado para cada piso - ver turnos en ESPERA y llamarlos"""
    # Solo admin y pisos pueden acceder
    if current_user.role not in ['admin', 'pisos']:
        flash('No tienes acceso a esta sección', 'error')
        return redirect(url_for('turns.recepcion'))
    
    from flask import current_app
    areas = current_app.config.get('AREAS_MUNICIPALES_NORMALIZADAS', [])
    areas_piso = [a for a in areas if a.get('piso') == str(numero)]
    
    if not areas_piso:
        flash(f'Piso {numero} no encontrado', 'error')
        return redirect(url_for('turns.recepcion'))
    
    return render_template('turns/piso_llamado.html', numero_piso=numero, areas_piso=areas_piso)

@turns_bp.route('/estadisticas')
@login_required
def estadisticas():
    """Vista de estadísticas - solo para admin"""
    if current_user.role != 'admin':
        flash('No tienes acceso a esta sección', 'error')
        return redirect(url_for('turns.recepcion'))
    
    return render_template('turns/estadisticas.html')

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
        print(f"DEBUG - Datos recibidos: {data}")  # DEBUG
        
        # Validar campos requeridos
        if not data or not data.get('nombre'):
            print("DEBUG - Error: Nombre faltante")  # DEBUG
            return jsonify({'success': False, 'message': 'Nombre es requerido'}), 400
        if not data.get('area_key'):
            print("DEBUG - Error: Area_key faltante")  # DEBUG
            return jsonify({'success': False, 'message': 'Área es requerida'}), 400
        
        # Obtener información del área desde la configuración
        from flask import current_app
        areas = current_app.config.get('AREAS_MUNICIPALES_NORMALIZADAS', [])
        print(f"DEBUG - Total áreas disponibles: {len(areas)}")  # DEBUG
        area = next((a for a in areas if a['key'] == data['area_key']), None)
        
        if not area:
            print(f"DEBUG - Error: Área no encontrada para key={data['area_key']}")  # DEBUG
            return jsonify({'success': False, 'message': f'Área no válida: {data["area_key"]}'}), 400
        
        area_key = area['key']
        area_nombre = area['nombre']
        piso = area['piso']
        
        print(f"DEBUG - Área encontrada: {area_nombre} (Piso {piso})")  # DEBUG
        
        # Normalizar motivo
        motivo_texto = (data.get('motivo_texto') or '').strip()
        motivo_key, _ = normalize_motive(motivo_texto) if motivo_texto else ('SIN_ESPECIFICAR', 'SIN ESPECIFICAR')
        
        # Crear turno
        turno = VisitorTurn(
            nombre=data['nombre'].strip(),
            dni=data.get('dni', '').strip() if data.get('dni') else None,
            area_key=area_key,
            area_nombre=area_nombre,
            piso=piso,
            motivo_key=motivo_key,
            motivo_texto=motivo_texto or 'SIN ESPECIFICAR',
            estado='ESPERA'
        )
        
        db.session.add(turno)
        db.session.commit()
        
        print(f"DEBUG - Turno creado exitosamente ID={turno.id}")  # DEBUG
        
        return jsonify({
            'success': True,
            'message': 'Turno registrado correctamente',
            'data': turno.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG - ERROR: {error_trace}")  # DEBUG
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@turns_bp.route('/api/turnos/<int:turno_id>/autorizar', methods=['POST'])
@login_required
def api_autorizar_turno(turno_id):
    """Autorizar subida de visitante (LLAMAR desde piso)"""
    turno = VisitorTurn.query.get_or_404(turno_id)
    
    if turno.estado != 'ESPERA':
        return jsonify({'success': False, 'message': 'El turno no está en espera'}), 400
    
    data = request.get_json() or {}
    llamado_por = data.get('llamado_por', current_user.username)
    atendido_por = data.get('atendido_por')
    
    turno.autorizar_subida(llamado_por)
    
    # Guardar quién va a atender
    if atendido_por:
        turno.atendido_por = atendido_por
        db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Visitante llamado por {llamado_por}',
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

@turns_bp.route('/api/estadisticas/por-piso', methods=['GET'])
@login_required
def api_estadisticas_por_piso():
    """Estadísticas de turnos por piso"""
    from datetime import date
    
    hoy = date.today()
    
    por_piso = db.session.query(
        VisitorTurn.piso,
        func.count(VisitorTurn.id).label('total')
    ).filter(
        func.date(VisitorTurn.hora_llegada) == hoy
    ).group_by(VisitorTurn.piso).all()
    
    resultado = {p.piso: p.total for p in por_piso}
    
    return jsonify({
        'success': True,
        'data': resultado
    })

@turns_bp.route('/api/estadisticas/por-area', methods=['GET'])
@login_required
def api_estadisticas_por_area():
    """Estadísticas de turnos por área"""
    from datetime import date
    
    hoy = date.today()
    
    por_area = db.session.query(
        VisitorTurn.area_nombre,
        VisitorTurn.piso,
        func.count(VisitorTurn.id).label('total'),
        func.sum(func.case((VisitorTurn.estado == 'ATENDIDO', 1), else_=0)).label('atendidos'),
        func.sum(func.case((VisitorTurn.estado == 'ESPERA', 1), else_=0)).label('en_espera')
    ).filter(
        func.date(VisitorTurn.hora_llegada) == hoy
    ).group_by(
        VisitorTurn.area_nombre, VisitorTurn.piso
    ).order_by(func.count(VisitorTurn.id).desc()).all()
    
    resultado = [{
        'area_nombre': area.area_nombre,
        'piso': area.piso,
        'total': area.total,
        'atendidos': area.atendidos or 0,
        'en_espera': area.en_espera or 0
    } for area in por_area]
    
    return jsonify({
        'success': True,
        'data': resultado
    })

# ============================================
# API CHAT
# ============================================

@turns_bp.route('/api/chat/mensajes', methods=['GET'])
@login_required
def api_chat_mensajes():
    """Obtener mensajes del chat (últimos 50)"""
    from .models import ChatMessage
    
    limite = request.args.get('limite', 50, type=int)
    
    mensajes = ChatMessage.query.order_by(
        ChatMessage.timestamp.desc()
    ).limit(limite).all()
    
    return jsonify({
        'success': True,
        'mensajes': [m.to_dict() for m in reversed(mensajes)]
    })

@turns_bp.route('/api/chat/enviar', methods=['POST'])
@login_required
def api_chat_enviar():
    """Enviar mensaje al chat"""
    from .models import ChatMessage
    
    data = request.get_json() or {}
    mensaje_texto = data.get('mensaje', '').strip()
    origen = data.get('origen', 'recepcion')  # recepcion, piso_1, piso_2, piso_3
    usuario = data.get('usuario', current_user.username).strip()  # Nombre personalizado o username
    
    if not mensaje_texto:
        return jsonify({'success': False, 'message': 'Mensaje vacío'}), 400
    
    mensaje = ChatMessage(
        usuario=usuario,
        origen=origen,
        mensaje=mensaje_texto
    )
    
    db.session.add(mensaje)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Mensaje enviado',
        'data': mensaje.to_dict()
    }), 201
