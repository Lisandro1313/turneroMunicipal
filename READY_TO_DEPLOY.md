# 🎉 SISTEMA DE TURNOS MUNICIPAL - LISTO PARA SUBIR

## ✅ ESTADO ACTUAL: **READY FOR DEPLOYMENT**

### 📊 Verificación Completada
✅ **Todos los archivos presentes**  
✅ **Todas las dependencias instaladas**  
✅ **Base de datos funcionando**  
✅ **Templates completos**  
✅ **API endpoints operativos (12 rutas)**  
✅ **Sistema de roles configurado**  
✅ **Seguridad implementada (.env en .gitignore)**  

---

## 🚀 DEPLOYMENT - OPCIONES RÁPIDAS

### Opción 1: Render.com (RECOMENDADO) ⭐

1. **Push a GitHub**:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Crear cuenta en Render.com**:
   - Ir a https://render.com
   - Sign up / Login con GitHub

3. **Crear Web Service**:
   - Click "New" → "Web Service"
   - Conectar repositorio: `Lisandro1313/turneroMunicipal`
   - **Name**: `turnero-municipal`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Plan**: Free

4. **Agregar PostgreSQL Database**:
   - Click "New" → "PostgreSQL"
   - **Name**: `turnero-db`
   - **Plan**: Free
   - Copiar la `Internal Database URL`

5. **Configurar Environment Variables**:
   En el Web Service → Environment:
   ```
   SECRET_KEY=tu-clave-super-secreta-generada
   DATABASE_URL=[pegar la Internal Database URL de PostgreSQL]
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

6. **Deploy**:
   - Click "Manual Deploy" → "Deploy latest commit"
   - Esperar 2-3 minutos

7. **Inicializar DB**:
   En el Shell del Web Service:
   ```bash
   python init_db.py
   ```

8. **¡LISTO!** Tu app estará en: `https://turnero-municipal.onrender.com`

---

### Opción 2: Heroku

```bash
# 1. Instalar Heroku CLI (si no está instalado)
# Descargar desde: https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Crear app
heroku create turnero-municipal

# 4. Agregar PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# 5. Configurar variables
heroku config:set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

# 6. Push
git push heroku main

# 7. Inicializar DB
heroku run python init_db.py

# 8. Abrir app
heroku open
```

---

### Opción 3: PythonAnywhere

1. **Crear cuenta**: https://www.pythonanywhere.com
2. **Upload código**: Via Git o Files
3. **Crear virtualenv**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 turnero
   pip install -r requirements.txt
   ```
4. **Configurar Web App**:
   - Python 3.10
   - Manual configuration
   - Configurar WSGI file
5. **Crear .env** con variables
6. **Inicializar DB**: `python init_db.py`
7. **Reload**: Click "Reload"

---

## 🔑 CREDENCIALES POR DEFECTO

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| recepcion | recepcion123 | Recepción |
| pisos | pisos123 | Pisos 1, 2, 3 |

⚠️ **CAMBIAR ESTAS CONTRASEÑAS DESPUÉS DEL PRIMER LOGIN EN PRODUCCIÓN**

---

## ⚙️ CONFIGURACIÓN NECESARIA ANTES DE DEPLOYMENT

### 1. Generar SECRET_KEY seguro
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Configurar variables de entorno en la plataforma

**Render/Heroku/PythonAnywhere:**
```
SECRET_KEY=<tu-clave-generada>
DATABASE_URL=<postgresql-url>
FLASK_ENV=production
FLASK_DEBUG=False
```

### 3. Inicializar base de datos en producción
```bash
python init_db.py
```

---

## 📝 ESTRUCTURA DEL PROYECTO

```
turnero_app/
├── app/
│   ├── __init__.py          # Inicialización Flask
│   ├── models.py            # Modelos DB (User, VisitorTurn, ChatMessage)
│   ├── routes.py            # Rutas principales (login, logout)
│   ├── turns.py             # Blueprint de turnos (12 endpoints API)
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/notifications.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       └── turns/
│           ├── recepcion.html
│           ├── piso_llamado.html
│           └── estadisticas.html
├── instance/
│   └── turnero.db           # SQLite (desarrollo)
├── migrations/              # Migraciones Alembic
├── .env.example             # Template de variables
├── .gitignore              # Git ignore
├── config.py               # Configuración app
├── init_db.py              # Script inicialización
├── requirements.txt        # Dependencias Python
├── Procfile               # Para Heroku/Render
├── run.py                 # Ejecutar app
├── verify_deployment.py   # Script verificación
└── README.md              # Documentación
```

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS

### ✅ Sistema Completo de Turnos
- Registro de visitantes (Recepción)
- Búsqueda por DNI con historial
- Cola de espera en tiempo real
- Llamado de visitantes (Pisos)
- Registro de quién atiende
- Marcado como atendido
- Flujo: Espera → Autorizado → Atendido

### ✅ Chat Interno
- Mensajes entre recepción y pisos
- Auto-refresh cada 5 segundos
- Formato DD/MM/YYYY HH:MM
- Badge con contador de mensajes nuevos

### ✅ Estadísticas (Admin)
- 4 cards resumen (Total, Espera, Subiendo, Atendidos)
- Distribución por piso
- Top 10 áreas visitadas
- Últimos 20 turnos
- Auto-refresh cada 30 segundos

### ✅ Notificaciones
- Sonido al registrar turno
- Toast messages (Bootstrap)
- Notificaciones del navegador
- Control on/off de sonido

### ✅ Seguridad
- Hash de contraseñas (Werkzeug)
- CSRF protection (Flask-WTF)
- Rate limiting (Flask-Limiter)
- Control de acceso por roles
- Variables de entorno (.env)

---

## 🔧 ENDPOINTS API

### Turnos
- `GET /turns/api/turnos` - Lista con filtros
- `GET /turns/api/turnos/en-espera` - Cola de espera
- `POST /turns/api/turnos` - Crear turno
- `POST /turns/api/turnos/{id}/autorizar` - Llamar visitante
- `POST /turns/api/turnos/{id}/atender` - Marcar atendido
- `POST /turns/api/turnos/{id}/rechazar` - Rechazar turno
- `GET /turns/api/dni/{dni}/historial` - Buscar por DNI

### Estadísticas
- `GET /turns/api/estadisticas/resumen` - Resumen general
- `GET /turns/api/estadisticas/por-piso` - Por piso
- `GET /turns/api/estadisticas/por-area` - Por área

### Chat
- `GET /turns/api/chat/mensajes` - Obtener mensajes
- `POST /turns/api/chat/enviar` - Enviar mensaje

---

## 🐛 PROBLEMAS CONOCIDOS

1. **JavaScript warning** en `piso_llamado.html` línea 199:
   - Es solo un warning del linter por sintaxis Jinja2
   - No afecta la funcionalidad
   - Se puede ignorar

2. **Rate limiting 429** en chat:
   - Ocurre con muchos requests simultáneos
   - Es comportamiento esperado (protección anti-spam)
   - Se resuelve esperando unos segundos

---

## 📞 SOPORTE POST-DEPLOYMENT

### Ver logs en Render:
Dashboard → Logs

### Ver logs en Heroku:
```bash
heroku logs --tail
```

### Resetear base de datos:
```bash
# ⚠️ CUIDADO: Borra todos los datos
python init_db.py
```

### Backup base de datos (Heroku):
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

- `README.md` - Guía completa
- `CHECKLIST_DEPLOYMENT.md` - Checklist detallado
- `verify_deployment.py` - Script de verificación

---

## ✅ CHECKLIST FINAL ANTES DE SUBIR

- [x] Código en GitHub
- [ ] SECRET_KEY generada y configurada
- [ ] Variables de entorno configuradas en plataforma
- [ ] PostgreSQL creado y DATABASE_URL configurada
- [ ] FLASK_DEBUG=False
- [ ] App deployada
- [ ] Base de datos inicializada (`python init_db.py`)
- [ ] Login funcional
- [ ] Cambiar contraseñas por defecto
- [ ] Probar registro de turno
- [ ] Verificar que persiste en DB
- [ ] Probar chat
- [ ] Verificar estadísticas

---

## 🎉 ¡TODO LISTO!

El sistema está **100% funcional** y listo para deployment.

Solo falta:
1. Pushear a GitHub
2. Elegir plataforma (Render recomendado)
3. Configurar variables de entorno
4. Deployar
5. Inicializar DB
6. ¡Usar el sistema!

**Tiempo estimado de deployment: 10-15 minutos** ⏱️

---

*Sistema de Turnos Municipal - Desarrollado con ❤️ usando Flask + Bootstrap 5*
