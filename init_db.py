"""
Script para inicializar la base de datos con datos de ejemplo
"""
from app import create_app, db
from app.models import User, Organization, VisitorTurn
from datetime import datetime

def init_database():
    """Inicializar base de datos con datos de ejemplo"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✓ Tablas creadas")
        
        # Verificar si ya existe el usuario admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@municipio.gob.ar',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Usuario admin creado (usuario: admin, contraseña: admin123)")
        
        # Crear usuario editor de ejemplo
        editor = User.query.filter_by(username='editor').first()
        if not editor:
            editor = User(
                username='editor',
                email='editor@municipio.gob.ar',
                role='editor'
            )
            editor.set_password('editor123')
            db.session.add(editor)
            print("✓ Usuario editor creado (usuario: editor, contraseña: editor123)")
        
        # Crear organizaciones de ejemplo (para módulo previo)
        if Organization.query.count() == 0:
            organizaciones = [
                {
                    'name': 'Comedor Barrio Norte',
                    'representative': 'María González',
                    'address': 'Calle Principal 123',
                    'phone': '555-1234',
                    'email': 'comedor.norte@email.com',
                    'direccion_municipal': 'desarrollo_social',
                    'tipo_organizacion': 'comedor',
                    'kilos': 50,
                    'frequency': 'semanal',
                    'day_of_week': 1  # Martes
                },
                {
                    'name': 'Escuela Primaria N°5',
                    'representative': 'Juan Pérez',
                    'address': 'Av. Educación 456',
                    'phone': '555-5678',
                    'email': 'escuela5@educacion.gob.ar',
                    'direccion_municipal': 'educacion',
                    'tipo_organizacion': 'escuela',
                    'kilos': 100,
                    'frequency': 'mensual',
                    'day_of_month': 15
                },
                {
                    'name': 'Club Deportivo Central',
                    'representative': 'Carlos Rodríguez',
                    'address': 'Av. Deportes 789',
                    'phone': '555-9012',
                    'email': 'club.central@deportes.com',
                    'direccion_municipal': 'deportes',
                    'tipo_organizacion': 'club',
                    'kilos': 75,
                    'frequency': 'quincenal',
                    'day_of_week': 4  # Viernes
                },
                {
                    'name': 'Centro de Salud Comunitario',
                    'representative': 'Dra. Ana Martínez',
                    'address': 'Calle Salud 321',
                    'phone': '555-3456',
                    'email': 'centro.salud@salud.gob.ar',
                    'direccion_municipal': 'salud',
                    'tipo_organizacion': 'centro_salud',
                    'kilos': 60,
                    'frequency': 'semanal',
                    'day_of_week': 3  # Jueves
                },
                {
                    'name': 'Biblioteca Popular',
                    'representative': 'Laura Fernández',
                    'address': 'Plaza Cultural s/n',
                    'phone': '555-7890',
                    'email': 'biblioteca@cultura.gob.ar',
                    'direccion_municipal': 'cultura',
                    'tipo_organizacion': 'biblioteca',
                    'kilos': 30,
                    'frequency': 'mensual',
                    'day_of_month': 1
                }
            ]
            
            for org_data in organizaciones:
                org = Organization(**org_data)
                db.session.add(org)
            
            print(f"✓ {len(organizaciones)} organizaciones de ejemplo creadas")
        
        db.session.commit()

        # Turnos de visitantes de muestra (recepción/planta baja)
        vt_samples = [
                {
                    'nombre': 'Juan Pérez', 'dni': '30111222',
                    'area_key': 'EMERGENCIA_ASISTENCIA_CRITICA', 'area_nombre': 'Dirección de Emergencia y Asistencia Crítica', 'piso': '1',
                    'motivo_key': 'MATERIALES', 'motivo_texto': 'SOLICITUD DE MATERIALES',
                    'estado': 'ESPERA'
                },
                {
                    'nombre': 'María Gómez', 'dni': '27999888',
                    'area_key': 'POLITICAS_ALIMENTARIAS', 'area_nombre': 'Dirección de Políticas Alimentarias', 'piso': '1',
                    'motivo_key': 'CONSULTA_GENERAL', 'motivo_texto': 'CONSULTA',
                    'estado': 'AUTORIZADO_SUBIR'
                },
                {
                    'nombre': 'Carlos Díaz', 'dni': '32444555',
                    'area_key': 'SITUACION_DE_CALLE', 'area_nombre': 'Situación de Calle', 'piso': '1',
                    'motivo_key': 'RECLAMO', 'motivo_texto': 'RECLAMO',
                    'estado': 'ATENDIDO', 'atendido_por': 'ANGIE'
                },
                {
                    'nombre': 'Lucía Fernández', 'dni': '33888777',
                    'area_key': 'NINEZ_Y_ADOLESCENCIA', 'area_nombre': 'Dirección de Niñez y Adolescencia', 'piso': '2',
                    'motivo_key': 'DOCUMENTACION', 'motivo_texto': 'ENTREGA DE DOCUMENTACION',
                    'estado': 'ESPERA'
                },
            ]
        for vt in vt_samples:
            turn = VisitorTurn(**vt)
            db.session.add(turn)
        db.session.commit()
        print("\n✓ Base de datos inicializada correctamente!")
        print("\nCredenciales de acceso:")
        print("  Admin  -> usuario: admin, contraseña: admin123")
        print("  Editor -> usuario: editor, contraseña: editor123")

if __name__ == '__main__':
    init_database()
