# Guía de Deployment en Render

## Pasos para Desplegar en Render.com

### 1. Preparar el Repositorio

1. **Inicializar Git** (si no lo has hecho):
```bash
cd turnero_app
git init
git add .
git commit -m "Initial commit - Turnero Municipal App"
```

2. **Crear repositorio en GitHub**:
   - Ve a https://github.com/new
   - Crea un repositorio llamado `turnero-municipal`
   - Sigue las instrucciones para hacer push:

```bash
git remote add origin https://github.com/TU-USUARIO/turnero-municipal.git
git branch -M main
git push -u origin main
```

### 2. Configurar Render

1. **Crear cuenta en Render**:
   - Ve a https://render.com
   - Regístrate con GitHub

2. **Crear PostgreSQL Database**:
   - Click en "New +"
   - Selecciona "PostgreSQL"
   - Configuración:
     - **Name**: turnero-db
     - **Database**: turnero
     - **User**: turnero
     - **Region**: Elegir el más cercano (US East si estás en Argentina)
     - **Plan**: Free
   - Click "Create Database"
   - **IMPORTANTE**: Copia el "Internal Database URL" que aparece

3. **Crear Web Service**:
   - Click en "New +"
   - Selecciona "Web Service"
   - Conecta tu repositorio de GitHub
   - Configuración:
     - **Name**: turnero-municipal
     - **Region**: Mismo que la database
     - **Branch**: main
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
     - **Start Command**: `gunicorn run:app`
     - **Plan**: Free

4. **Variables de Entorno**:
   Agregar en la sección "Environment":

   ```
   FLASK_ENV=production
   SECRET_KEY=<generar-una-key-segura>
   JWT_SECRET_KEY=<generar-otra-key-segura>
   DATABASE_URL=<pegar-el-Internal-Database-URL>
   PYTHON_VERSION=3.11.0
   ```

   Para generar keys seguras, ejecuta en Python:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Render automáticamente:
     - Clonará tu repo
     - Instalará dependencias
     - Ejecutará migraciones
     - Iniciará la aplicación

### 3. Verificar el Deployment

1. Una vez completado, verás una URL como:
   ```
   https://turnero-municipal.onrender.com
   ```

2. Accede a la aplicación y verifica:
   - Login funciona
   - Se puede crear organizaciones
   - Generar cronogramas
   - Ver estadísticas

### 4. Inicializar Datos

Render ejecuta comandos en el build. Para inicializar la BD con datos de ejemplo:

1. Ve a la consola de Render (pestaña "Shell")
2. Ejecuta:
```bash
python init_db.py
```

Alternativamente, agrega al Build Command:
```bash
pip install -r requirements.txt && flask db upgrade && python init_db.py
```

### 5. Configuración Avanzada (Opcional)

#### Dominio Personalizado
1. En Render Dashboard > tu servicio
2. Settings > Custom Domain
3. Agregar tu dominio (ej: turnero.municipio.gob.ar)
4. Configurar DNS según instrucciones

#### Health Checks
Render automáticamente hace health checks a `/`. Si quieres personalizar:
1. Settings > Health Check Path
2. Cambiar a `/api/health` (necesitarías crear ese endpoint)

#### Logging
Los logs están disponibles en la pestaña "Logs" del dashboard.

### 6. Mantenimiento

#### Actualizar la Aplicación
```bash
git add .
git commit -m "Descripción del cambio"
git push origin main
```

Render automáticamente detectará los cambios y redesplegará.

#### Backups de Base de Datos
En el plan gratuito, los backups no están incluidos. Considera:
1. Upgrading al plan Starter ($7/mes) para backups automáticos
2. O crear un script de backup manual

#### Monitoreo
- Render proporciona métricas básicas (CPU, memoria, requests)
- Para monitoreo avanzado, considera integrar:
  - Sentry (errores)
  - Google Analytics (uso)

### 7. Costos

**Plan Gratuito:**
- Web Service: 750 horas/mes (suficiente para 1 app)
- PostgreSQL: 90 días gratis, luego $7/mes
- La app se "duerme" después de 15 minutos sin uso
- Primer request después de dormir toma ~30 segundos

**Para Producción Real:**
Considera el plan Starter:
- Web Service: $7/mes
- PostgreSQL: $7/mes
- **Total: $14/mes**
- Sin sleep, mejor performance, backups incluidos

### Troubleshooting

**Error en Build:**
- Verifica requirements.txt
- Revisa logs de build en Render

**Error en Runtime:**
- Verifica variables de entorno
- Revisa logs en pestaña "Logs"
- Asegúrate que DATABASE_URL esté configurada

**App muy lenta:**
- Es normal en plan gratuito tras inactividad
- Upgrade a plan Starter para mejor performance

**Database Connection Error:**
- Verifica que DATABASE_URL sea el "Internal" URL
- No usar "External" URL entre servicios de Render

---

## Alternativas a Render

Si prefieres otras opciones:

### Railway.app
- Similar a Render
- $5/mes incluye todo
- Más fácil de usar

### Heroku
- Clásico PaaS
- Ya no tiene plan gratuito
- $7/mes por app

### Fly.io
- Más técnico (requiere Docker)
- Buen plan gratuito
- Mejor para apps globales

### PythonAnywhere
- Especializado en Python
- Plan gratuito limitado
- Bueno para prototipos

---

## Recomendación Final

Para esta app municipal, recomiendo:

1. **Desarrollo/Testing**: Render Free tier
2. **Producción**: Render Starter ($14/mes) o Railway ($5/mes)
3. **Si hay presupuesto**: DigitalOcean App Platform ($12/mes) con mejor soporte

La inversión de $15/mes es mínima comparada con el valor que aporta la aplicación a la gestión municipal.
