# Guía de Desarrollo Local - Turnero Municipal

## ✅ Cambios Implementados

### 1. Base de Datos Configurada ✅
- ✅ Base de datos SQLite local funcionando
- ✅ **Los datos se guardan PERMANENTEMENTE** - No se borran automáticamente
- ✅ Archivo `.env` configurado para desarrollo local
- 📁 Ubicación de la base de datos: `instance/turnero.db`

### 2. Usuarios Separados por Pisos ✅
Se actualizó el sistema de roles para que los usuarios estén separados por pisos:

**Roles disponibles:**
- `admin` - Acceso completo a todo el sistema
- `recepcion` - Solo puede acceder a la vista de recepción
- `piso1` - Solo puede acceder al piso 1
- `piso2` - Solo puede acceder al piso 2
- `piso3` - Solo puede acceder al piso 3

**Usuarios creados:**
- **Admin:** usuario: `admin`, contraseña: `admin123`
- **Recepción:** usuario: `recepcion`, contraseña: `recepcion123`
- **Piso 1:** usuario: `piso1`, contraseña: `piso1123`
- **Piso 2:** usuario: `piso2`, contraseña: `piso2123`
- **Piso 3:** usuario: `piso3`, contraseña: `piso3123`

### 3. Seguridad por Piso ✅
- Los usuarios de piso solo pueden acceder a su piso específico
- Si intentan acceder a otro piso, son redirigidos automáticamente
- El admin puede acceder a todos los pisos

### 4. Estadísticas Mejoradas ✅
Ahora la sección de estadísticas incluye:

#### 🔍 Búsqueda de Visitantes:
- **Buscar por DNI:** Ver el historial completo de una persona
  - Total de visitas
  - Primera y última visita
  - Áreas visitadas
  - Motivos de consulta
- **Buscar por Nombre:** Buscar todas las personas con un nombre similar

#### 📊 Estadísticas Detalladas:
- **Motivos de Consulta:** Top de motivos más frecuentes del día
- **Por Área:** Top 10 áreas más visitadas
- **Por Piso:** Distribución de turnos por piso
- **Últimos Turnos:** Historial de los últimos 20 turnos

### 5. Historial Permanente ✅
- **IMPORTANTE:** Todos los turnos quedan guardados para siempre en la base de datos
- Puedes buscar cualquier visita histórica por DNI o nombre
- Los datos NO se borran automáticamente
- Para limpiar datos antiguos, tendrías que hacerlo manualmente

## 🚀 Cómo Usar

### Iniciar el Servidor Local
```bash
cd C:\Users\Usuario\OneDrive\Escritorio\turneromunicipal
python run.py
```

El servidor estará disponible en: http://127.0.0.1:5000

### Reinicializar la Base de Datos
Si necesitas limpiar la base de datos y crear usuarios nuevos:
```bash
python init_db.py
```

### Crear Usuarios Adicionales
```bash
python create_user.py
```

## 📱 Próximos Pasos para la App Mobile

Para la app mobile con notificaciones, necesitarás:

### 1. Backend - API REST
- ✅ Ya tienes endpoints API en `/api/turnos`
- 🔲 Agregar autenticación JWT para mobile
- 🔲 Implementar WebSocket o Server-Sent Events para notificaciones en tiempo real
- 🔲 Endpoint para registrar tokens de notificaciones push (FCM/APNS)

### 2. Frontend Mobile
Opciones recomendadas:
- **React Native** (multiplataforma: iOS + Android)
- **Flutter** (multiplataforma: iOS + Android)
- **Ionic + Capacitor** (usa el código web existente)

### 3. Notificaciones Push
- **Firebase Cloud Messaging (FCM)** para Android
- **Apple Push Notification Service (APNS)** para iOS
- Implementar servicio en el backend que envíe notificaciones cuando:
  - Se crea un nuevo turno para un piso específico
  - Se autoriza a un visitante a subir
  - Se marca un turno como atendido

## 🔧 Estructura del Proyecto

```
turneromunicipal/
├── app/
│   ├── __init__.py          # Configuración de la app
│   ├── models.py            # Modelos de datos (User, VisitorTurn, ChatMessage)
│   ├── routes.py            # Rutas de autenticación
│   ├── turns.py             # Rutas y API de turnos
│   ├── utils.py             # Utilidades
│   ├── static/              # CSS y JS
│   └── templates/           # Templates HTML
├── migrations/              # Migraciones de base de datos
├── instance/                # Archivos de instancia (DB SQLite)
├── config.py                # Configuraciones
├── .env                     # Variables de entorno LOCAL
├── requirements.txt         # Dependencias Python
└── run.py                   # Punto de entrada
```

## 🧪 Testing Local

1. **Login con diferentes usuarios:**
   - http://127.0.0.1:5000/login
   - Prueba con cada usuario (admin, recepcion, piso1, piso2, piso3)

2. **Crear turnos desde recepción:**
   - Login como `recepcion`
   - Crear turnos para diferentes áreas/pisos

3. **Ver turnos desde cada piso:**
   - Login como `piso1`, `piso2`, o `piso3`
   - Verificar que solo ves turnos de tu piso
   - Probar autorizar visitantes a subir

## 📝 Notas Importantes

- La base de datos local está en `instance/turnero.db`
- Los logs se guardan en `logs/turnero.log`
- Para producción, deberás actualizar las contraseñas y usar PostgreSQL en lugar de SQLite
- El archivo `.env` NO debe subirse a Git (ya está en `.gitignore`)

## 🔄 Actualizar el Deploy en Render

Cuando estés listo para subir los cambios:

```bash
# 1. Commit los cambios
git add .
git commit -m "Actualización: usuarios por pisos y base de datos funcionando"

# 2. Push al repositorio
git push origin main

# 3. Render detectará los cambios y hará redeploy automáticamente
```

**IMPORTANTE:** Antes de hacer push, asegúrate de:
- Que el archivo `.env` NO esté incluido (usar `.env.example` como referencia)
- Actualizar `render.yaml` si hay cambios en las variables de entorno
- Ejecutar migraciones en producción si hay cambios en los modelos

## 🔐 Seguridad en Producción

Para producción en Render, necesitas configurar estas variables de entorno:
- `DATABASE_URL` - PostgreSQL URL (Render lo configura automáticamente)
- `SECRET_KEY` - Una clave secreta fuerte
- `JWT_SECRET_KEY` - Otra clave secreta para JWT
- `FLASK_ENV` - production
- `FLASK_DEBUG` - False

---

## 📞 Contacto y Soporte

Si tienes dudas o problemas, revisa:
- `README.md` - Documentación general
- `DEPLOY.md` - Guía de deployment
- `QUICKSTART.md` - Inicio rápido
