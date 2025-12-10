# ✅ Checklist de Deployment - Sistema de Turnos Municipal

## 📋 Verificaciones Pre-Deployment

### 🔒 Seguridad
- [x] Archivo `.gitignore` configurado correctamente
- [x] Archivo `.env.example` incluido (sin datos sensibles)
- [x] `.env` en gitignore (no se sube al repo)
- [ ] ⚠️ **CAMBIAR `SECRET_KEY` en producción**
- [ ] ⚠️ **CAMBIAR contraseñas por defecto (admin/recepcion/pisos)**
- [x] CSRF protection activado
- [x] Rate limiting configurado
- [x] Hash de contraseñas con Werkzeug

### 📦 Archivos de Configuración
- [x] `requirements.txt` - Dependencias correctas
- [x] `Procfile` - Para Heroku/Render
- [x] `config.py` - Configuración por entornos
- [x] `.env.example` - Template de variables
- [x] `README.md` - Documentación actualizada

### 🗄️ Base de Datos
- [x] Modelos definidos (User, VisitorTurn, ChatMessage)
- [x] Migraciones configuradas (Alembic/Flask-Migrate)
- [x] Script `init_db.py` funcional
- [x] Timezone Argentina (UTC-3) configurado
- [ ] ⚠️ **Configurar PostgreSQL para producción** (actualmente SQLite)

### 🔧 Código
- [x] No hay errores críticos de Python
- [x] Endpoints API funcionando (12 rutas)
- [x] Templates renderizando correctamente
- [x] JavaScript sin errores de consola
- [x] CSS/Bootstrap cargando correctamente
- [x] Auto-refresh configurado (turnos, chat, stats)

### 🧪 Funcionalidades Testeadas
- [x] Login/Logout funcional
- [x] Registro de visitantes (Recepción)
- [x] Búsqueda por DNI con historial
- [x] Llamado de visitantes (Pisos)
- [x] Marcado como atendido (Pisos)
- [x] Chat interno entre roles
- [x] Estadísticas completas (Admin)
- [x] Navegación entre vistas
- [x] Control de acceso por rol

### 📱 UI/UX
- [x] Responsive design (Bootstrap 5)
- [x] Navegación con dropdown scrollable
- [x] Modals funcionando (Llamar, Atender, Chat)
- [x] Notificaciones visuales (toasts)
- [x] Notificaciones de sonido
- [x] Badges de contador (chat, turnos)
- [x] Formularios con validación

### 🌐 Deployment

#### Opción 1: Heroku
```bash
# 1. Instalar Heroku CLI
# 2. Login
heroku login

# 3. Crear app
heroku create nombre-app

# 4. Agregar PostgreSQL
heroku addons:create heroku-postgresql:mini

# 5. Configurar variables
heroku config:set SECRET_KEY="tu-secret-key-segura"
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

# 6. Deploy
git push heroku main

# 7. Inicializar DB
heroku run python init_db.py
```

#### Opción 2: Render
1. Crear cuenta en [render.com](https://render.com)
2. Conectar repositorio GitHub
3. Configurar Web Service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
4. Agregar PostgreSQL Database
5. Configurar Environment Variables:
   - `SECRET_KEY`
   - `DATABASE_URL` (auto desde Render)
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=False`
6. Deploy automático desde GitHub

#### Opción 3: PythonAnywhere
```bash
# 1. Subir archivos via Git o interface web
# 2. Crear virtualenv
mkvirtualenv --python=/usr/bin/python3.10 turnero

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar WSGI
# Editar /var/www/tudominio_pythonanywhere_com_wsgi.py

# 5. Configurar .env
# Crear archivo .env con variables

# 6. Inicializar DB
python init_db.py

# 7. Reload web app
```

### 🚨 CRÍTICO - Antes de Subir a Producción

1. **Cambiar SECRET_KEY**:
```python
# Generar una nueva:
python -c "import secrets; print(secrets.token_hex(32))"
```

2. **Cambiar Contraseñas**:
```bash
# Ejecutar después del init_db.py
python create_user.py
# Y cambiar las contraseñas de admin, recepcion, pisos
```

3. **Configurar Base de Datos**:
```bash
# En .env para producción:
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

4. **Desactivar Debug**:
```bash
# En .env:
FLASK_ENV=production
FLASK_DEBUG=False
```

5. **Configurar CORS** (si usas API externa):
```python
# En app/__init__.py
CORS(app, resources={r"/api/*": {"origins": "tu-dominio.com"}})
```

### 📊 Post-Deployment

- [ ] Verificar que la app carga correctamente
- [ ] Probar login con usuarios creados
- [ ] Registrar un turno de prueba
- [ ] Verificar que persiste en la base de datos
- [ ] Probar chat entre roles
- [ ] Verificar estadísticas en vista admin
- [ ] Revisar logs de errores
- [ ] Configurar monitoreo (opcional: Sentry, Datadog)
- [ ] Configurar backups automáticos de DB

### 📝 Mantenimiento

#### Comandos Útiles
```bash
# Ver logs en Heroku
heroku logs --tail

# Ver logs en Render
# Desde la dashboard > Logs

# Backup DB en Heroku
heroku pg:backups:capture
heroku pg:backups:download

# Resetear DB (¡CUIDADO!)
heroku pg:reset DATABASE_URL
heroku run python init_db.py
```

### 🎯 Estado Actual

**✅ LISTO PARA DEPLOYMENT LOCAL**

**⚠️ PENDIENTE PARA PRODUCCIÓN:**
- Cambiar SECRET_KEY
- Cambiar contraseñas por defecto
- Configurar PostgreSQL
- Configurar variables de entorno en plataforma

**🐛 Errores Conocidos:**
- ⚠️ JavaScript warning en `piso_llamado.html` línea 199 (no afecta funcionalidad, es un warning del linter por la sintaxis de Jinja2)

**📌 Áreas de Mejora Futuras:**
- Sistema de backup automático
- Exportación de reportes a Excel/PDF
- Panel de métricas históricas (últimos 30 días)
- Notificaciones por email
- Integración con impresora térmica para tickets
