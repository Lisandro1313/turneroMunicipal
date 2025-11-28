from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """Modelo de usuario con roles y seguridad mejorada"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer')  # admin, editor, viewer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relaciones
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hashear la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Actualizar último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Organization(db.Model):
    """Modelo de organización/institución beneficiaria"""
    __tablename__ = 'organization'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    representative = db.Column(db.String(150), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    
    # Clasificación
    direccion_municipal = db.Column(db.String(50), nullable=True)  # desarrollo_social, educacion, etc.
    tipo_organizacion = db.Column(db.String(50), nullable=True)  # comedor, escuela, club, etc.
    
    # Datos de entrega
    kilos = db.Column(db.Integer, nullable=True)
    frequency = db.Column(db.String(50), nullable=False, default='mensual')  # semanal, quincenal, mensual
    day_of_week = db.Column(db.Integer, nullable=True)  # 0-6 (Lunes-Domingo)
    day_of_month = db.Column(db.Integer, nullable=True)  # 1-31
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    schedules = db.relationship('Schedule', backref='organization', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'representative': self.representative,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'direccion_municipal': self.direccion_municipal,
            'tipo_organizacion': self.tipo_organizacion,
            'kilos': self.kilos,
            'frequency': self.frequency,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'is_active': self.is_active,
            'notes': self.notes
        }

class Schedule(db.Model):
    """Modelo de cronograma de entregas"""
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    kilos = db.Column(db.Integer, nullable=True)
    delivered = db.Column(db.Boolean, default=False)
    
    # Información adicional
    delivered_at = db.Column(db.DateTime, nullable=True)
    delivered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def mark_delivered(self, user_id):
        """Marcar como entregado"""
        self.delivered = True
        self.delivered_at = datetime.utcnow()
        self.delivered_by = user_id
        db.session.commit()
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'organization_name': self.organization.name if self.organization else None,
            'date': self.date.isoformat() if self.date else None,
            'kilos': self.kilos,
            'delivered': self.delivered,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'notes': self.notes
        }

class AuditLog(db.Model):
    """Modelo para auditoría de acciones"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # login, create, update, delete
    entity_type = db.Column(db.String(50), nullable=True)  # organization, schedule, user
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Sistema',
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class VisitorTurn(db.Model):
    """Turno de visitante para edificio municipal"""
    __tablename__ = 'visitor_turn'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    dni = db.Column(db.String(20), nullable=True, index=True)

    # Área/Piso normalizados
    area_key = db.Column(db.String(100), nullable=False, index=True)  # clave normalizada (e.g., POLITICAS_ALIMENTARIAS)
    area_nombre = db.Column(db.String(200), nullable=False)  # nombre amigable
    piso = db.Column(db.String(20), nullable=True)  # "PB", "1", "2", "3"

    # Motivo
    motivo_key = db.Column(db.String(100), nullable=True, index=True)  # categoría normalizada
    motivo_texto = db.Column(db.String(300), nullable=True)  # texto libre ingresado

    # Estados del flujo
    estado = db.Column(db.String(30), nullable=False, default='ESPERA')  # ESPERA | AUTORIZADO_SUBIR | ATENDIDO | RECHAZADO
    hora_llegada = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    hora_autorizado = db.Column(db.DateTime, nullable=True)
    hora_atendido = db.Column(db.DateTime, nullable=True)

    # Responsable
    atendido_por = db.Column(db.String(150), nullable=True)  # alias/nombre del agente que atendió
    notas = db.Column(db.Text, nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def autorizar_subida(self):
        self.estado = 'AUTORIZADO_SUBIR'
        self.hora_autorizado = datetime.utcnow()
        db.session.commit()

    def marcar_atendido(self, agente_nombre: str | None = None):
        self.estado = 'ATENDIDO'
        self.hora_atendido = datetime.utcnow()
        if agente_nombre:
            self.atendido_por = agente_nombre
        db.session.commit()

    def rechazar(self, motivo: str | None = None):
        self.estado = 'RECHAZADO'
        if motivo:
            self.notas = (self.notas + "\n" if self.notas else "") + f"Rechazado: {motivo}"
        db.session.commit()

    def tiempo_espera_segundos(self):
        if not self.hora_autorizado:
            return None
        return int((self.hora_autorizado - self.hora_llegada).total_seconds())

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'dni': self.dni,
            'area_key': self.area_key,
            'area_nombre': self.area_nombre,
            'piso': self.piso,
            'motivo_key': self.motivo_key,
            'motivo_texto': self.motivo_texto,
            'estado': self.estado,
            'hora_llegada': self.hora_llegada.isoformat() if self.hora_llegada else None,
            'hora_autorizado': self.hora_autorizado.isoformat() if self.hora_autorizado else None,
            'hora_atendido': self.hora_atendido.isoformat() if self.hora_atendido else None,
            'atendido_por': self.atendido_por,
            'notas': self.notas,
            'tiempo_espera_segundos': self.tiempo_espera_segundos(),
        }
