# 🚀 Inicio Rápido - Turnero Municipal

## Instalación Local (5 minutos)

### 1. Instalar Dependencias

```powershell
# Navegar a la carpeta del proyecto
cd "c:\Users\Public\Desktop\Algo de lisu\turnero_app"

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

El archivo `.env` ya está creado con valores por defecto para desarrollo.

### 3. Inicializar Base de Datos

```powershell
# Inicializar migraciones (solo primera vez)
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade

# Poblar con datos de ejemplo (OPCIONAL)
python init_db.py
```

### 4. Ejecutar Aplicación

```powershell
python run.py
```

La aplicación estará disponible en: **http://localhost:5000**

### 5. Acceder

**Credenciales por defecto:**
- **Admin**: usuario `admin`, contraseña `admin123`
- **Editor**: usuario `editor`, contraseña `editor123`

---

## 📋 Verificación Rápida

### Checklist de Funcionalidades

✅ **Login**
1. Ve a http://localhost:5000/login
2. Ingresa: usuario `admin`, contraseña `admin123`
3. Deberías ver el Dashboard

✅ **Ver Organizaciones**
1. Click en "Organizaciones" en el menú
2. Deberías ver 5 organizaciones de ejemplo (si ejecutaste init_db.py)

✅ **Agregar Organización**
1. Click en "Nueva Organización"
2. Completa el formulario usando solo **selects y dropdowns** (sin escribir fechas manualmente)
3. Guarda

✅ **Generar Cronograma**
1. Click en "Generar Cronograma"
2. Selecciona fechas con el date picker
3. Click en "Generar"
4. Verifica que se crearon las entregas

✅ **Ver Estadísticas**
1. Click en "Estadísticas"
2. Deberías ver gráficos y métricas

✅ **API REST**
- Organizaciones: http://localhost:5000/api/organizations
- Cronogramas: http://localhost:5000/api/schedules
- Stats Overview: http://localhost:5000/stats/api/overview

---

## 🔧 Comandos Útiles

### Desarrollo

```powershell
# Ejecutar en modo debug
python run.py

# Ver logs de base de datos
$env:SQLALCHEMY_ECHO="True"
python run.py

# Crear nueva migración después de cambios en models.py
flask db migrate -m "Descripción del cambio"
flask db upgrade
```

### Base de Datos

```powershell
# Resetear base de datos (CUIDADO: elimina todos los datos)
Remove-Item instance\turnero.db
flask db upgrade
python init_db.py

# Backup de base de datos
Copy-Item instance\turnero.db instance\turnero_backup_$(Get-Date -Format 'yyyyMMdd').db
```

### Testing

```powershell
# Instalar pytest
pip install pytest pytest-flask

# Ejecutar tests (cuando los crees)
pytest
```

---

## 🎨 Personalización

### Cambiar Nombre de la App

Edita `config.py`:
```python
APP_NAME = 'Tu Nombre Personalizado'
```

### Agregar Direcciones Municipales

Edita `config.py` en la sección `DIRECCIONES_MUNICIPALES`:
```python
{
    'id': 'nueva_direccion',
    'nombre': 'Dirección de ...',
    'descripcion': 'Descripción',
    'icon': '🏛️'
}
```

### Cambiar Colores

Edita `app/static/css/style.css`:
```css
:root {
    --primary-color: #TU-COLOR;
}
```

---

## 🐛 Troubleshooting

### Error: "No module named flask"
```powershell
# Asegúrate de tener el venv activado
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Unable to locate migration script"
```powershell
# Elimina la carpeta migrations y reinicializa
Remove-Item -Recurse migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Error: "Working outside of application context"
```powershell
# Usa flask shell para interactuar con la app
flask shell
>>> from app.models import User, Organization
>>> User.query.all()
```

### La app está muy lenta
- En desarrollo es normal la primera carga
- Verifica que no tengas muchos procesos de Python corriendo
- Reinicia la aplicación

### Los cambios en templates no se ven
```powershell
# Limpia caché del navegador (Ctrl+Shift+R en Chrome)
# O desactiva caché en modo desarrollador (F12 > Network > Disable cache)
```

---

## 📚 Próximos Pasos

1. **Personalizar** la configuración en `config.py`
2. **Agregar** tus organizaciones reales
3. **Generar** el cronograma del año
4. **Capacitar** al personal en el uso del sistema
5. **Desplegar** en Render siguiendo `DEPLOY.md`

---

## 🆘 Soporte

Si tienes problemas:

1. Verifica los logs en la terminal
2. Revisa `logs/turnero.log` (si existe)
3. Consulta `README.md` para más detalles
4. Abre un issue en GitHub

---

## ✨ Mejoras Implementadas vs Versión Original

| Característica | Antes | Ahora |
|---------------|-------|-------|
| **Seguridad** | Contraseñas en texto plano | Hash con Werkzeug + CSRF + Rate limiting |
| **UI** | HTML básico | Bootstrap 5 + responsive + dropdowns |
| **Datos** | Dispersos en formularios | Centralizados en config.py |
| **Estadísticas** | No existían | Dashboard completo con gráficos |
| **API** | No existía | REST API completa |
| **Roles** | Un solo usuario | Admin, Editor, Viewer |
| **Logging** | No | Sistema completo de auditoría |
| **Deployment** | Local solamente | Listo para Render |
| **Arquitectura** | Un solo archivo | Blueprints separados |
| **Validaciones** | Básicas | Completas con mensajes |

---

¡Disfruta de tu nuevo sistema de turnero municipal mejorado! 🎉
