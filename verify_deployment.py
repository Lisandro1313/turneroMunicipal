"""
Script de verificación pre-deployment
Verifica que todos los componentes estén listos
"""

import sys
import os

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file(filepath, description):
    """Verifica si un archivo existe"""
    exists = os.path.exists(filepath)
    status = f"{Colors.GREEN}✓{Colors.END}" if exists else f"{Colors.RED}✗{Colors.END}"
    print(f"{status} {description}: {filepath}")
    return exists

def check_import(module_name):
    """Verifica si un módulo se puede importar"""
    try:
        __import__(module_name)
        print(f"{Colors.GREEN}✓{Colors.END} Módulo instalado: {module_name}")
        return True
    except ImportError:
        print(f"{Colors.RED}✗{Colors.END} Módulo faltante: {module_name}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}   VERIFICACIÓN PRE-DEPLOYMENT - Sistema de Turnos{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    all_ok = True
    
    # Verificar archivos críticos
    print(f"\n{Colors.YELLOW}📂 Archivos de Configuración:{Colors.END}")
    files = {
        'requirements.txt': 'Dependencias',
        'config.py': 'Configuración',
        '.env.example': 'Template de variables',
        '.gitignore': 'Git ignore',
        'Procfile': 'Procfile para deployment',
        'run.py': 'Archivo de ejecución',
        'init_db.py': 'Script de inicialización'
    }
    
    for file, desc in files.items():
        all_ok &= check_file(file, desc)
    
    # Verificar estructura de carpetas
    print(f"\n{Colors.YELLOW}📁 Estructura de Carpetas:{Colors.END}")
    folders = {
        'app': 'Aplicación principal',
        'app/templates': 'Templates HTML',
        'app/static': 'Archivos estáticos',
        'migrations': 'Migraciones de DB'
    }
    
    for folder, desc in folders.items():
        all_ok &= check_file(folder, desc)
    
    # Verificar módulos Python
    print(f"\n{Colors.YELLOW}🐍 Dependencias Python:{Colors.END}")
    modules = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_migrate',
        'flask_wtf',
        'flask_limiter',
        'werkzeug',
        'gunicorn'
    ]
    
    for module in modules:
        all_ok &= check_import(module)
    
    # Verificar archivos de la app
    print(f"\n{Colors.YELLOW}🔧 Archivos de la Aplicación:{Colors.END}")
    app_files = {
        'app/__init__.py': 'Inicialización de app',
        'app/models.py': 'Modelos de DB',
        'app/routes.py': 'Rutas principales',
        'app/turns.py': 'Blueprint de turnos'
    }
    
    for file, desc in app_files.items():
        all_ok &= check_file(file, desc)
    
    # Verificar templates
    print(f"\n{Colors.YELLOW}📄 Templates HTML:{Colors.END}")
    templates = {
        'app/templates/base.html': 'Template base',
        'app/templates/login.html': 'Login',
        'app/templates/turns/recepcion.html': 'Recepción',
        'app/templates/turns/piso_llamado.html': 'Vista Piso',
        'app/templates/turns/estadisticas.html': 'Estadísticas Admin'
    }
    
    for file, desc in templates.items():
        all_ok &= check_file(file, desc)
    
    # Verificar que .env NO esté en el repo
    print(f"\n{Colors.YELLOW}🔒 Seguridad:{Colors.END}")
    env_exists = os.path.exists('.env')
    if env_exists:
        print(f"{Colors.YELLOW}⚠{Colors.END} Archivo .env existe (asegúrate que esté en .gitignore)")
        
        # Verificar que está en gitignore
        with open('.gitignore', 'r') as f:
            in_gitignore = '.env' in f.read()
        
        if in_gitignore:
            print(f"{Colors.GREEN}✓{Colors.END} .env está en .gitignore")
        else:
            print(f"{Colors.RED}✗{Colors.END} .env NO está en .gitignore - AGREGAR URGENTE")
            all_ok = False
    else:
        print(f"{Colors.GREEN}✓{Colors.END} .env no existe en el proyecto (usar .env.example)")
    
    # Verificar base de datos
    print(f"\n{Colors.YELLOW}💾 Base de Datos:{Colors.END}")
    db_exists = os.path.exists('instance/turnero.db')
    if db_exists:
        print(f"{Colors.GREEN}✓{Colors.END} Base de datos existe en instance/turnero.db")
        
        # Verificar que instance/ está en gitignore
        with open('.gitignore', 'r') as f:
            instance_ignored = 'instance/' in f.read()
        
        if instance_ignored:
            print(f"{Colors.GREEN}✓{Colors.END} instance/ está en .gitignore")
        else:
            print(f"{Colors.RED}✗{Colors.END} instance/ NO está en .gitignore")
            all_ok = False
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Base de datos no existe. Ejecutar: python init_db.py")
    
    # Resumen final
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    if all_ok:
        print(f"{Colors.GREEN}✅ VERIFICACIÓN COMPLETADA - TODO OK{Colors.END}")
        print(f"\n{Colors.YELLOW}⚠️  Recordatorios antes de deployment:{Colors.END}")
        print("  1. Cambiar SECRET_KEY en producción")
        print("  2. Cambiar contraseñas por defecto")
        print("  3. Configurar DATABASE_URL para PostgreSQL")
        print("  4. Configurar FLASK_DEBUG=False")
        print(f"\n{Colors.GREEN}El sistema está listo para deployment!{Colors.END}")
    else:
        print(f"{Colors.RED}❌ HAY PROBLEMAS - REVISAR ARRIBA{Colors.END}")
        print(f"\n{Colors.YELLOW}Soluciona los errores antes de hacer deployment.{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
