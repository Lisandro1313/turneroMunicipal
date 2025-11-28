import os
from app import create_app

# Determinar el entorno
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == "__main__":
    # En desarrollo, usar servidor de Flask
    # En producción, usar gunicorn (ver Procfile)
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

