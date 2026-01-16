"""
Script para inicializar la base de datos con datos de ejemplo
"""
from app import create_app, db
from app.models import User, VisitorTurn
from datetime import datetime

def init_database():
    """Inicializar base de datos con datos de ejemplo"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✓ Tablas creadas")
        
        # Crear usuarios del sistema si no existen
        usuarios = [
            {
                'username': 'admin',
                'email': 'admin@municipio.gob.ar',
                'role': 'admin',
                'piso': None,
                'password': 'admin123'
            },
            {
                'username': 'recepcion',
                'email': 'recepcion@municipio.gob.ar',
                'role': 'recepcion',
                'piso': None,
                'password': 'recepcion123'
            },
            {
                'username': 'piso1',
                'email': 'piso1@municipio.gob.ar',
                'role': 'piso1',
                'piso': '1',
                'password': 'piso1123'
            },
            {
                'username': 'piso2',
                'email': 'piso2@municipio.gob.ar',
                'role': 'piso2',
                'piso': '2',
                'password': 'piso2123'
            },
            {
                'username': 'piso3',
                'email': 'piso3@municipio.gob.ar',
                'role': 'piso3',
                'piso': '3',
                'password': 'piso3123'
            }
        ]
        
        for user_data in usuarios:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    piso=user_data.get('piso')
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"✓ Usuario {user_data['username']} creado")
        
        db.session.commit()

        # NO crear turnos de ejemplo - base de datos limpia
        print("✓ Base de datos limpia, sin turnos de ejemplo")

        print("\n✓ Base de datos inicializada correctamente!")
        print("\nCredenciales de acceso:")
        print("  Admin      -> usuario: admin, contraseña: admin123")
        print("  Recepción  -> usuario: recepcion, contraseña: recepcion123")
        print("  Pisos      -> usuario: pisos, contraseña: pisos123")

if __name__ == '__main__':
    init_database()
