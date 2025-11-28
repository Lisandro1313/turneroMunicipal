from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

# Inicializamos las instancias
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configuración de LoginManager
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app(config_name=None):
    """Factory pattern para crear la aplicación"""
    app = Flask(__name__)
    
    # Configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Rate limiting
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter.init_app(app)
    
    # CORS para APIs
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/turnero.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Turnero Municipal startup')
    
    # Registrar blueprints
    from app.routes import main
    from app.api import api_bp
    from app.stats import stats_bp
    
    app.register_blueprint(main)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/stats')
    
    # Context processors
    @app.context_processor
    def inject_config():
        """Inyectar configuración en los templates"""
        return {
            'app_name': app.config.get('APP_NAME', 'Turnero Municipal'),
            'direcciones': app.config.get('DIRECCIONES_MUNICIPALES', []),
            'frecuencias': app.config.get('FRECUENCIAS_ENTREGA', []),
            'dias_semana': app.config.get('DIAS_SEMANA', [])
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        from flask import render_template
        return render_template('errors/429.html'), 429
    
    # Crear tablas
    with app.app_context():
        from app.models import User, Organization, Schedule, AuditLog
        db.create_all()
        
        # Crear usuario admin por defecto si no existe
        if User.query.filter_by(username='admin').first() is None:
            admin = User(username='admin', email='admin@municipio.gob.ar', role='admin')
            admin.set_password('admin123')  # Cambiar en producción
            db.session.add(admin)
            db.session.commit()
            app.logger.info('Usuario admin creado')
    
    return app

