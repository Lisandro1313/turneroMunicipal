# Sistema de Turnos Municipal - Gestión de Visitantes

## 🎯 Descripción

Sistema de gestión de turnos para visitantes en edificio municipal de 3 pisos. Permite a recepción registrar visitantes, a los pisos llamarlos cuando estén listos para atenderlos, y a administradores ver estadísticas completas.

## ✨ Características Principales

### 🔐 Sistema de Roles
- **Admin**: Acceso completo + vista de estadísticas
- **Recepción**: Registro de visitantes y gestión de cola
- **Pisos (1, 2, 3)**: Llamado y atención de visitantes

### 📋 Gestión de Turnos
- ✅ Registro rápido de visitantes (DNI, nombre, área, motivo)
- ✅ Autocompletado desde historial al buscar por DNI
- ✅ Cola de espera en tiempo real
- ✅ Llamado de visitantes con seguimiento de quién llama
- ✅ Registro de quién atiende al visitante
- ✅ Estados: Espera → Autorizado/Subiendo → Atendido

### 💬 Chat Interno
- ✅ Mensajes entre recepción y pisos
- ✅ Notificaciones en tiempo real
- ✅ Formato con fecha/hora completa (DD/MM/YYYY HH:MM)

### 📊 Estadísticas (Admin)
- ✅ Resumen diario: Total, En Espera, Subiendo, Atendidos
- ✅ Distribución por piso (1, 2, 3)
- ✅ Top 10 áreas más visitadas
- ✅ Últimos 20 turnos con detalles completos
- ✅ Auto-actualización cada 30 segundos

### 🔔 Notificaciones
- ✅ Sonido al registrar nuevo turno
- ✅ Alertas visuales (toast messages)
- ✅ Notificaciones del navegador
- ✅ Control de activación/desactivación de sonido

### 🌍 Configuración Regional
- ✅ Timezone: Argentina (UTC-3)
- ✅ Formato de fechas: DD/MM/YYYY HH:MM
- ✅ Idioma: Español
- ✔ Filtros y búsqueda avanzada
- ✔ Paginación
- ✔ Log de auditoría

### ✅ Arquitectura
- ✔ Blueprints separados (main, api, stats)
- ✔ Modelos mejorados con relaciones
- ✔ Utilidades y decoradores
- ✔ Manejo de errores centralizado
- ✔ Logging profesional

## 📦 Instalación

### Desarrollo Local

1. **Clonar el repositorio**
```bash
git clone <tu-repo>
cd turnero_app
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
copy .env.example .env
# Editar .env con tus valores
```

5. **Inicializar la base de datos**
```bash
flask db init  # Solo la primera vez
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Ejecutar la aplicación**
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

**Usuario por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: Cambiar la contraseña del admin en producción!

## 🌐 Deployment en Render

### Opción 1: Usando el Dashboard de Render

1. **Crear cuenta en Render**: https://render.com
2. **New > Web Service**
3. **Conectar tu repositorio de GitHub**
4. Configurar:
   - **Name**: turnero-municipal
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn run:app`
   - **Environment Variables**:
     - `FLASK_ENV=production`
     - `SECRET_KEY=<generar-random>`
     - `JWT_SECRET_KEY=<generar-random>`
     - `DATABASE_URL` (se auto-configura con la BD)

5. **Crear PostgreSQL Database**:
   - New > PostgreSQL
   - Name: turnero-db
   - Copiar el Internal Database URL
   - Agregar como variable `DATABASE_URL` en el Web Service

### Opción 2: Usando render.yaml (Infrastructure as Code)

El archivo `render.yaml` ya está configurado. Solo necesitas:

1. Push del código a GitHub
2. En Render Dashboard: New > Blueprint
3. Conectar el repositorio
4. Render automáticamente detectará `render.yaml` y creará todo

### Variables de Entorno en Producción

En Render, configurar estas variables:

```
FLASK_ENV=production
SECRET_KEY=<tu-secret-key-super-segura>
JWT_SECRET_KEY=<tu-jwt-secret-key-super-segura>
DATABASE_URL=<se-autoconfigura-desde-postgresql>
```

Para generar keys seguras en Python:
```python
import secrets
secrets.token_urlsafe(32)
```

## 🗂️ Estructura del Proyecto

```
turnero_app/
├── app/
│   ├── __init__.py          # Factory pattern, extensiones
│   ├── models.py            # Modelos de datos mejorados
│   ├── routes.py            # Rutas principales
│   ├── api.py               # API REST
│   ├── stats.py             # Estadísticas
│   ├── utils.py             # Utilidades y decoradores
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       ├── base.html        # Template base con Bootstrap 5
│       ├── login.html       # Login moderno
│       ├── dashboard.html   # Dashboard con métricas
│       ├── organizations.html
│       ├── add_organization.html
│       ├── edit_organization.html
│       └── ...
├── migrations/              # Migraciones de BD
├── config.py               # Configuración centralizada
├── run.py                  # Entry point
├── requirements.txt        # Dependencias
├── Procfile               # Para Render
├── render.yaml            # Configuración IaC
├── .env.example           # Template de variables
└── .gitignore
```

## 🔑 Credenciales por Defecto

**Admin:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ Cambiar inmediatamente en producción!

## 📊 API Endpoints

### Organizaciones
- `GET /api/organizations` - Listar todas
- `GET /api/organizations/<id>` - Ver una
- `POST /api/organizations` - Crear
- `PUT /api/organizations/<id>` - Actualizar
- `DELETE /api/organizations/<id>` - Eliminar (desactivar)

### Cronogramas
- `GET /api/schedules` - Listar con filtros
- `POST /api/schedules/<id>/deliver` - Marcar como entregado
- `POST /api/schedules/<id>/undeliver` - Desmarcar

### Estadísticas
- `GET /stats/api/overview` - Resumen general
- `GET /stats/api/by-month` - Por mes
- `GET /stats/api/by-organization` - Por organización
- `GET /stats/api/by-direccion` - Por dirección municipal
- `GET /stats/api/upcoming-deliveries` - Próximas entregas

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask 3.0
- **Base de Datos**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **Auth**: Flask-Login
- **Security**: Flask-WTF (CSRF), Flask-Limiter, Werkzeug
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Charts**: Chart.js
- **Server**: Gunicorn
- **Hosting**: Render

## 📝 Próximas Mejoras

- [ ] Exportación de reportes a PDF/Excel
- [ ] Sistema de notificaciones por email
- [ ] Búsqueda avanzada con filtros múltiples
- [ ] Calendario interactivo para visualizar entregas
- [ ] Panel de métricas en tiempo real
- [ ] Integración con WhatsApp para notificaciones
- [ ] Multi-tenancy para múltiples municipios

## 📄 Licencia

MIT License - Uso libre para municipalidades

## 👨‍💻 Autor

Desarrollado para la modernización de la gestión de entregas alimentarias municipales.

---

**¿Necesitas ayuda?** Abre un issue en GitHub
