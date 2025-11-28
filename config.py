import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///turnero.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # App
    APP_NAME = os.environ.get('APP_NAME', 'Turnero Municipal')
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Áreas/Pisos del edificio (normalizadas)
    AREAS_MUNICIPALES_NORMALIZADAS = [
        {'key': 'TRABAJO_SOCIAL', 'nombre': 'Área de Trabajo Social', 'piso': '1', 'icon': '🧩'},
        {'key': 'POLITICAS_ALIMENTARIAS', 'nombre': 'Dirección de Políticas Alimentarias', 'piso': '1', 'icon': '🍎'},
        {'key': 'SITUACION_DE_CALLE', 'nombre': 'Situación de Calle', 'piso': '1', 'icon': '🚶'},
        {'key': 'EMERGENCIA_ASISTENCIA_CRITICA', 'nombre': 'Dirección de Emergencia y Asistencia Crítica', 'piso': '1', 'icon': '🚨'},
        {'key': 'NINEZ_Y_ADOLESCENCIA', 'nombre': 'Dirección de Niñez y Adolescencia', 'piso': '2', 'icon': '👶'},
        {'key': 'SECRETARIA', 'nombre': 'Secretaría de Desarrollo Social', 'piso': '3', 'icon': '🏢'},
        {'key': 'INTEGRACION_SOCIAL', 'nombre': 'Dirección de Integración Social', 'piso': '3', 'icon': '🤝'},
        {'key': 'ARTICULACION_OPERATIVA', 'nombre': 'Dirección de Articulación Operativa', 'piso': '3', 'icon': '🧭'},
        {'key': 'INCLUSION_SOCIAL', 'nombre': 'Subsecretaría de Inclusión Social', 'piso': '3', 'icon': '🧑‍🤝‍🧑'},
    ]

    # Mapeos de variantes a claves normalizadas (incompleto, ampliable)
    AREA_VARIANTS_MAP = {
        'DIRECCION GENERAL DE EMERGENCIA Y ASISTENCIA CRITICA': 'EMERGENCIA_ASISTENCIA_CRITICA',
        'ASISTENCIA CRITICA': 'EMERGENCIA_ASISTENCIA_CRITICA',
        'AC': 'EMERGENCIA_ASISTENCIA_CRITICA',
        'DIRECCIO GENERAL DE ARTICULACION OPERATIVA': 'ARTICULACION_OPERATIVA',
        'DIRECCION GENERAL DE ARTICULACION OPERATIVA': 'ARTICULACION_OPERATIVA',
        'DIRECCION DE ARTICULACION': 'ARTICULACION_OPERATIVA',
        'POLITICAS ALIMENTARIAS': 'POLITICAS_ALIMENTARIAS',
        'Politicias Alimentarias': 'POLITICAS_ALIMENTARIAS',
        'DIRECCION GENERAL DE POLITICA ALIMENTARIA': 'POLITICAS_ALIMENTARIAS',
        'DIRECCION GENERAL DE POLITICAS ALIMENTARIAS': 'POLITICAS_ALIMENTARIAS',
        'DIRECCIONGENERALDEPOLITICASALIMENTARIAS': 'POLITICAS_ALIMENTARIAS',
        'direccion general de politica alimentarias': 'POLITICAS_ALIMENTARIAS',
        'SUBSECRETARIA DE INCLUSION SOCIAL': 'INCLUSION_SOCIAL',
        'SUBSECRETARIADEINCLUSIONSOCIAL': 'INCLUSION_SOCIAL',
        'INCLUSION': 'INCLUSION_SOCIAL',
        'SITUACION DE CALLE': 'SITUACION_DE_CALLE',
        'situacion de calle': 'SITUACION_DE_CALLE',
        'DIRECCION GENERAL DE POLITICAS DE NIÑEZ Y ADOLESCENCIA': 'NINEZ_Y_ADOLESCENCIA',
        'TRABAJO SOCIAL': 'TRABAJO_SOCIAL',
        'AREA TRABAJO SOCIAL': 'TRABAJO_SOCIAL',
        'DIRECCION DE INTEGRACION SOCIAL': 'INTEGRACION_SOCIAL',
        'DIRECION GENERAL DE INTEGRACION SOCIAL': 'INTEGRACION_SOCIAL',
        'SECRETARIA DE DESARROLLO SOCIAL': 'SECRETARIA',
        'SECRETARIA DESARROLLO SOCIAL': 'SECRETARIA',
        '3er piso': 'SECRETARIA',
    }

    MOTIVO_VARIANTS_MAP = {
        'CONSULTA': 'CONSULTA_GENERAL',
        'RECLAMO': 'RECLAMO',
        'SOLICITUD DE MATERIALES': 'MATERIALES',
        'MATERIALES': 'MATERIALES',
        'ENTREGA DE DOCUMENTACION': 'DOCUMENTACION',
        'ENTREGA DOCUMENTACION': 'DOCUMENTACION',
        'DOCUMENTACION': 'DOCUMENTACION',
        'INCENDIO': 'INCENDIO',
        'PLAN MAS VIDA': 'PLAN_MAS_VIDA',
        'TARJETA': 'TARJETA',
        'CONSULTA TARJETA': 'TARJETA',
        'CONSULTA POR TARJETA': 'TARJETA',
        'COMEDOR': 'COMEDOR',
        'HABITACIONAL': 'HABITACIONAL',
        'REUNION': 'REUNION',
    }
    
    # Tipos de frecuencia de entrega
    FRECUENCIAS_ENTREGA = [
        {'value': 'semanal', 'label': 'Semanal'},
        {'value': 'quincenal', 'label': 'Quincenal'},
        {'value': 'mensual', 'label': 'Mensual'}
    ]
    
    # Días de la semana
    DIAS_SEMANA = [
        {'value': 0, 'label': 'Lunes'},
        {'value': 1, 'label': 'Martes'},
        {'value': 2, 'label': 'Miércoles'},
        {'value': 3, 'label': 'Jueves'},
        {'value': 4, 'label': 'Viernes'},
        {'value': 5, 'label': 'Sábado'},
        {'value': 6, 'label': 'Domingo'}
    ]

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # En producción, las variables de entorno son obligatorias
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Verificar que las variables críticas estén configuradas
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY must be set in production'
        assert os.environ.get('DATABASE_URL'), 'DATABASE_URL must be set in production'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
