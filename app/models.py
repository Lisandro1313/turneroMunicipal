from . import db
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Timezone de Argentina (UTC-3)
ARGENTINA_TZ = timezone(timedelta(hours=-3))

def now_argentina():
    """Obtener fecha/hora actual de Argentina"""
    return datetime.now(ARGENTINA_TZ)

class User(UserMixin, db.Model):
    """Modelo de usuario para el sistema de turnos"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='pisos')  # admin, recepcion, pisos
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=now_argentina)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hashear la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Actualizar último login"""
        self.last_login = now_argentina()
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
    hora_llegada = db.Column(db.DateTime, default=now_argentina, index=True)
    hora_autorizado = db.Column(db.DateTime, nullable=True)
    hora_atendido = db.Column(db.DateTime, nullable=True)

    # Responsable
    llamado_por = db.Column(db.String(150), nullable=True)  # quién llamó al visitante desde el piso
    atendido_por = db.Column(db.String(150), nullable=True)  # alias/nombre del agente que atendió
    notas = db.Column(db.Text, nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=now_argentina)
    updated_at = db.Column(db.DateTime, default=now_argentina, onupdate=now_argentina)

    def autorizar_subida(self, llamado_por: str | None = None):
        self.estado = 'AUTORIZADO_SUBIR'
        self.hora_autorizado = now_argentina()
        if llamado_por:
            self.llamado_por = llamado_por
        db.session.commit()

    def marcar_atendido(self, agente_nombre: str | None = None):
        self.estado = 'ATENDIDO'
        self.hora_atendido = now_argentina()
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
            'llamado_por': self.llamado_por,
            'atendido_por': self.atendido_por,
            'notas': self.notas,
            'tiempo_espera_segundos': self.tiempo_espera_segundos(),
        }

class ChatMessage(db.Model):
    """Mensajes del chat interno entre recepción y pisos"""
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(150), nullable=False)  # quién envía
    origen = db.Column(db.String(50), nullable=False)  # 'recepcion', 'piso_1', 'piso_2', 'piso_3'
    mensaje = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=now_argentina, index=True)
    leido = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario': self.usuario,
            'origen': self.origen,
            'mensaje': self.mensaje,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'leido': self.leido
        }
