# 🗄️ Guía: Configurar Base de Datos Permanente con Supabase

## ❌ Problema con Render Free

En el plan gratuito de Render:
- Usa **almacenamiento efímero** (se borra cada 30 días o al reiniciar)
- Tu SQLite se pierde con cada deploy
- **NO GUARDES DATOS IMPORTANTES EN RENDER FREE**

## ✅ Solución: PostgreSQL en Supabase

Supabase ofrece:
- ✅ PostgreSQL **permanente** y gratuito
- ✅ 500 MB de base de datos gratis
- ✅ Backups automáticos
- ✅ Dashboard visual para ver tus datos
- ✅ API REST automática
- ✅ Hosting global (rápido desde Argentina)

---

## 🚀 PASO A PASO

### 1️⃣ Crear Proyecto en Supabase

1. Ve a **https://supabase.com**
2. Click en **"Start your project"** o **"Sign Up"**
3. Regístrate con GitHub/Google/Email
4. Click en **"New Project"**

5. Completa el formulario:
   - **Name**: `turnero-municipal`
   - **Database Password**: Genera una contraseña fuerte y **GUÁRDALA**
     - Ejemplo: `Tu5eNpCw9Xm#K2Lq`
     - ⚠️ **MUY IMPORTANTE**: No la pierdas, la necesitarás después
   - **Region**: Selecciona **South America (São Paulo)** (más cercano a Argentina)
   - **Pricing Plan**: Free (gratis)

6. Click **"Create new project"**
   - ⏱️ Tarda 1-2 minutos en crear la base de datos

---

### 2️⃣ Obtener Connection String

Una vez creado el proyecto:

1. En el panel izquierdo, ve a **Settings** (⚙️)
2. Click en **"Database"**
3. Baja hasta la sección **"Connection string"**
4. Selecciona la pestaña **"URI"**
5. Copia la URL que se ve así:

```
postgresql://postgres.xxxxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

6. **Reemplaza** `[YOUR-PASSWORD]` con tu contraseña real:

```
postgresql://postgres.xxxxxxxxxxxxxxx:Tu5eNpCw9Xm#K2Lq@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

⚠️ **IMPORTANTE**: Si tu contraseña tiene caracteres especiales como `#`, `@`, `$`, etc., necesitas codificarlos:
- `#` → `%23`
- `@` → `%40`
- `$` → `%24`
- ` ` (espacio) → `%20`

Ejemplo: `Tu5eN#pw@2024` → `Tu5eN%23pw%402024`

---

### 3️⃣ Configurar en Render

1. Ve a **https://dashboard.render.com**
2. Entra a tu servicio web (turnero-municipal o como lo hayas llamado)
3. En el menú izquierdo, click en **"Environment"**

4. Busca la variable `DATABASE_URL`:
   - Si existe, click en **"Edit"**
   - Si no existe, click en **"Add Environment Variable"**

5. Configura:
   - **Key**: `DATABASE_URL`
   - **Value**: (pega tu connection string de Supabase completa)
   
   ```
   postgresql://postgres.xxxxxxxx:Tu5eN%23pw%402024@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   ```

6. Click **"Save Changes"**

7. ⏱️ Render redesplegará automáticamente (tarda 1-2 minutos)

---

### 4️⃣ Inicializar la Base de Datos

Una vez que Render termine de redesplegar:

1. En tu servicio en Render, arriba a la derecha click en **"Shell"**
   (Si no ves Shell, puede estar en el menú "⋮ More" → "Shell")

2. Esto abre una terminal en tu servidor. Ejecuta:

```bash
python init_db.py
```

3. Deberías ver algo como:
```
Database initialized successfully!
Admin user created: admin / admin
Recepcion user created: recepcion / recepcion
...
```

✅ **¡LISTO!** Tu base de datos ya está funcionando en Supabase.

---

### 5️⃣ Verificar que Funciona

#### Opción A: Desde tu App Web

1. Ve a la URL de tu app en Render
2. Logueate como admin
3. Registra un turno de prueba
4. Refresca la página → **El turno debe seguir ahí**

#### Opción B: Desde Supabase Dashboard

1. En Supabase, ve a **"Table Editor"** (📊)
2. Deberías ver tus tablas:
   - `user` → Usuarios del sistema
   - `visitor_turn` → Turnos registrados
   - `chat_message` → Mensajes del chat

3. Click en cualquier tabla para ver los datos

---

## 📊 Ver y Gestionar Datos

### Desde Supabase Dashboard

**Ver datos:**
- Table Editor → Selecciona tabla → Ver registros
- Puedes editar, borrar o agregar datos manualmente

**Backups:**
- Database → Backups → Descargar backup
- Gratis: 7 días de backups

**Queries SQL:**
- SQL Editor → Ejecutar consultas personalizadas
- Ejemplo:
  ```sql
  SELECT * FROM visitor_turn ORDER BY created_at DESC LIMIT 10;
  ```

**Monitoreo:**
- Database → Usage → Ver uso de storage, queries, etc.

---

## 🔐 Seguridad

### Variables de Entorno en Render

Además de `DATABASE_URL`, asegúrate de tener:

```
SECRET_KEY=tu-clave-super-secreta-aleatoria-larga
JWT_SECRET_KEY=otra-clave-secreta-diferente
FLASK_ENV=production
FLASK_DEBUG=False
```

Para generar claves seguras, puedes usar:
```python
import secrets
print(secrets.token_hex(32))
```

### No Subas Credenciales a Git

Verifica que tu `.gitignore` incluya:
```
.env
*.db
instance/
__pycache__/
```

---

## 💾 Migrar Datos de SQLite a PostgreSQL (Opcional)

Si ya tenías datos en SQLite local y querés migrarlos:

### Opción 1: Manualmente (Pocos datos)

1. Exporta de SQLite:
```bash
python
>>> from app import db, app
>>> with app.app_context():
>>>     users = User.query.all()
>>>     for u in users:
>>>         print(f"{u.username},{u.role}")
```

2. Copia esos datos e insértalos en la nueva DB

### Opción 2: Con Script (Muchos datos)

```python
# migrate_data.py
import os
os.environ['DATABASE_URL'] = 'tu-url-de-supabase'

from app import app, db
from app.models import User, VisitorTurn, ChatMessage

with app.app_context():
    # Ya tus datos deberían estar aquí si corriste init_db.py
    print(f"Users: {User.query.count()}")
    print(f"Turns: {VisitorTurn.query.count()}")
    print(f"Messages: {ChatMessage.query.count()}")
```

---

## 🆘 Troubleshooting

### Error: "could not connect to server"
- ✅ Verifica que la URL de Supabase esté correcta
- ✅ Verifica que la contraseña esté URL-encoded
- ✅ Chequea que el puerto sea 6543 (pooler) o 5432 (directo)

### Error: "password authentication failed"
- ✅ Tu contraseña tiene caracteres especiales → URL-encode
- ✅ Copia la contraseña directamente de Supabase Settings

### Error: "SSL required"
Agrega `?sslmode=require` al final de tu URL:
```
postgresql://postgres.xxx:pass@host:6543/postgres?sslmode=require
```

### La app dice "Database is locked"
- ✅ Esto significa que todavía está usando SQLite
- ✅ Verifica que `DATABASE_URL` esté configurada en Render
- ✅ Redesplega el servicio

### Render no redespliega después de cambiar variables
- ✅ Ve a "Manual Deploy" → "Deploy latest commit"

---

## 📈 Límites del Plan Gratis

| Recurso | Límite Gratis | Comentario |
|---------|---------------|------------|
| Database | 500 MB | Suficiente para 50,000+ turnos |
| Storage | 1 GB | Para archivos (no aplicable aún) |
| Bandwidth | 5 GB/mes | Transferencia de datos |
| API Requests | Ilimitado | Sin restricciones |

---

## 🎯 Resumen Rápido

```bash
# 1. Crear proyecto en Supabase
# 2. Copiar connection string
# 3. Configurar en Render:
DATABASE_URL=postgresql://postgres.xxx:password@host:6543/postgres

# 4. Render Shell:
python init_db.py

# 5. ¡Listo! 🎉
```

---

## 🔄 Próximos Pasos

- ✅ **Ya tienes DB permanente**
- ⏳ Testea que los datos persisten después de redeploys
- ⏳ Configura backups automáticos (opcional, ya incluido)
- ⏳ Monitorea el uso en Supabase Dashboard
- ⏳ Cuando tengas muchos datos, considera el plan Pro ($25/mes)

---

## 💡 Ventajas Extra de Supabase

1. **API REST automática**: Supabase genera endpoints REST para tus tablas
2. **Realtime**: Puedes suscribirte a cambios en tiempo real
3. **Auth**: Sistema de autenticación integrado (opcional, ya tienes Flask-Login)
4. **Storage**: Para subir archivos (DNI scans, fotos, etc.)
5. **Edge Functions**: Serverless functions (opcional)

🎉 **¡Tu turnero ya tiene base de datos permanente!**
