from typing import Optional
from flask import current_app

def normalize_area(nombre: str) -> tuple[str, str, Optional[str]]:
    """Normaliza un nombre de área a (key, nombre_amigable, piso)
    Usa Config.AREA_VARIANTS_MAP y Config.AREAS_MUNICIPALES_NORMALIZADAS.
    """
    if not nombre:
        return ('DESCONOCIDO', 'Área desconocida', None)

    n = nombre.strip()
    # Intentar mapear variantes
    variants = getattr(current_app.config, 'AREA_VARIANTS_MAP', {})
    key = variants.get(n)
    if not key:
        # Intentar case-insensitive
        for k, v in variants.items():
            if k.lower() == n.lower():
                key = v
                break

    # Si no se encontró, intentar por coincidencia parcial
    if not key:
        lowered = n.lower()
        for k, v in variants.items():
            if lowered in k.lower() or k.lower() in lowered:
                key = v
                break

    # Buscar detalles en catálogo
    catalog = getattr(current_app.config, 'AREAS_MUNICIPALES_NORMALIZADAS', [])
    area = None
    if key:
        area = next((a for a in catalog if a['key'] == key), None)

    # Fallback si no se encuentra
    if not area:
        # Heurísticas simples
        if 'politi' in lowered and 'aliment' in lowered:
            key = 'POLITICAS_ALIMENTARIAS'
        elif 'emerg' in lowered or 'critica' in lowered:
            key = 'EMERGENCIA_ASISTENCIA_CRITICA'
        elif 'calle' in lowered:
            key = 'SITUACION_DE_CALLE'
        elif 'niñez' in lowered or 'adolesc' in lowered:
            key = 'NINEZ_Y_ADOLESCENCIA'
        elif 'integracion' in lowered:
            key = 'INTEGRACION_SOCIAL'
        elif 'articulacion' in lowered:
            key = 'ARTICULACION_OPERATIVA'
        elif 'inclusion' in lowered:
            key = 'INCLUSION_SOCIAL'
        elif 'trabajo social' in lowered:
            key = 'TRABAJO_SOCIAL'
        area = next((a for a in catalog if a['key'] == key), None)

    if area:
        return (area['key'], area['nombre'], area.get('piso'))
    return ('DESCONOCIDO', n, None)

def normalize_motive(texto: str | None) -> tuple[Optional[str], str]:
    """Normaliza motivo libre a (motivo_key, motivo_texto) usando Config.MOTIVO_VARIANTS_MAP"""
    if not texto:
        return (None, '')
    t = texto.strip()
    variants = getattr(current_app.config, 'MOTIVO_VARIANTS_MAP', {})
    key = variants.get(t)
    if not key:
        for k, v in variants.items():
            if k.lower() == t.lower():
                key = v
                break
    if not key:
        l = t.lower()
        if 'materia' in l:
            key = 'MATERIALES'
        elif 'documen' in l or 'planilla' in l:
            key = 'DOCUMENTACION'
        elif 'incend' in l:
            key = 'INCENDIO'
        elif 'tarjeta' in l:
            key = 'TARJETA'
        elif 'comedor' in l:
            key = 'COMEDOR'
        elif 'reun' in l:
            key = 'REUNION'
        elif 'vida' in l and 'mas' in l:
            key = 'PLAN_MAS_VIDA'
        elif 'habitac' in l:
            key = 'HABITACIONAL'
        elif 'recla' in l:
            key = 'RECLAMO'
        elif 'consult' in l:
            key = 'CONSULTA_GENERAL'
    return (key, t)
"""
Utilidades y helpers para la aplicación
"""
from functools import wraps
from flask import abort, request
from flask_login import current_user
from app.models import AuditLog, db
from datetime import datetime, timedelta
import calendar

def admin_required(f):
    """Decorador para requerir rol de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    """Decorador para requerir rol de editor o admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'editor']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def log_action(user_id, action, entity_type=None, entity_id=None, details=None):
    """Registrar acción en el log de auditoría"""
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging action: {e}")
        db.session.rollback()

def get_week_dates(year, week_number):
    """Obtener fechas de inicio y fin de una semana"""
    first_day_of_year = datetime(year, 1, 1)
    days_to_monday = (week_number - 1) * 7
    monday = first_day_of_year + timedelta(days=days_to_monday - first_day_of_year.weekday())
    sunday = monday + timedelta(days=6)
    return monday.date(), sunday.date()

def generate_schedule_dates(frequency, start_date, end_date, day_of_week=None, day_of_month=None):
    """
    Generar lista de fechas para el cronograma según la frecuencia
    
    Args:
        frequency: 'semanal', 'quincenal', 'mensual'
        start_date: fecha de inicio
        end_date: fecha de fin
        day_of_week: día de la semana (0-6) para frecuencias semanales/quincenales
        day_of_month: día del mes (1-31) para frecuencia mensual
    
    Returns:
        Lista de fechas
    """
    dates = []
    current = start_date
    
    if frequency == 'semanal':
        # Ajustar al día de la semana especificado
        if day_of_week is not None:
            days_ahead = day_of_week - current.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            current = current + timedelta(days=days_ahead)
        
        while current <= end_date:
            dates.append(current)
            current += timedelta(weeks=1)
    
    elif frequency == 'quincenal':
        # Similar a semanal pero cada 2 semanas
        if day_of_week is not None:
            days_ahead = day_of_week - current.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            current = current + timedelta(days=days_ahead)
        
        while current <= end_date:
            dates.append(current)
            current += timedelta(weeks=2)
    
    elif frequency == 'mensual':
        # Cada mes en el día especificado
        if day_of_month is None:
            day_of_month = 1
        
        year = current.year
        month = current.month
        
        while True:
            # Ajustar si el día no existe en el mes
            last_day = calendar.monthrange(year, month)[1]
            day = min(day_of_month, last_day)
            
            date = datetime(year, month, day).date()
            if date > end_date:
                break
            if date >= start_date:
                dates.append(date)
            
            # Siguiente mes
            month += 1
            if month > 12:
                month = 1
                year += 1
    
    return dates

def validate_organization_data(data):
    """Validar datos de organización"""
    errors = []
    
    if not data.get('name'):
        errors.append('El nombre es obligatorio')
    
    if data.get('frequency') not in ['semanal', 'quincenal', 'mensual']:
        errors.append('La frecuencia debe ser semanal, quincenal o mensual')
    
    if data.get('kilos'):
        try:
            kilos = int(data['kilos'])
            if kilos <= 0:
                errors.append('Los kilos deben ser un número positivo')
        except ValueError:
            errors.append('Los kilos deben ser un número válido')
    
    if data.get('frequency') in ['semanal', 'quincenal']:
        if data.get('day_of_week') is None:
            errors.append('Debe especificar el día de la semana para entregas semanales/quincenales')
    
    if data.get('frequency') == 'mensual':
        if data.get('day_of_month') is None:
            errors.append('Debe especificar el día del mes para entregas mensuales')
        elif data.get('day_of_month'):
            try:
                day = int(data['day_of_month'])
                if day < 1 or day > 31:
                    errors.append('El día del mes debe estar entre 1 and 31')
            except ValueError:
                errors.append('El día del mes debe ser un número válido')
    
    return errors

def format_date_spanish(date):
    """Formatear fecha en español"""
    months = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    
    days = {
        0: 'lunes', 1: 'martes', 2: 'miércoles', 3: 'jueves',
        4: 'viernes', 5: 'sábado', 6: 'domingo'
    }
    
    day_name = days[date.weekday()]
    month_name = months[date.month]
    
    return f"{day_name.capitalize()}, {date.day} de {month_name} de {date.year}"
