# 🗄️ Alternativas GRATIS para Base de Datos PostgreSQL

## ❌ Problema
- Supabase sin proyectos gratis disponibles
- Render borra la base de datos cada 30 días

## ✅ Soluciones Alternativas

---

## 🥇 OPCIÓN 1: Neon.tech (RECOMENDADA)

**Por qué es la mejor:**
- ✅ PostgreSQL gratis **permanente**
- ✅ **10 GB de storage** gratis
- ✅ No requiere tarjeta de crédito
- ✅ Auto-pausa cuando no se usa (ahorra recursos)
- ✅ Serverless (ultra rápido)
- ✅ Región en USA (buena latencia desde Argentina)

### Paso a Paso

#### 1. Crear cuenta en Neon

1. Ve a **https://neon.tech**
2. Click en **"Sign Up"**
3. Regístrate con GitHub/Google/Email (gratis, sin tarjeta)

#### 2. Crear proyecto

1. Click en **"Create Project"**
2. Completa:
   - **Project name**: `turnero-municipal`
   - **Region**: `US East (Ohio)` (el más cercano a Argentina)
   - **PostgreSQL version**: 16 (la más nueva)
3. Click **"Create Project"**

#### 3. Obtener Connection String

Una vez creado el proyecto, verás la **Connection String**:

```
postgresql://usuario:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Copia esta URL completa** (incluye el `?sslmode=require` al final)

#### 4. Configurar en Render

1. Ve a tu servicio en **Render Dashboard**
2. **Environment** → Busca o agrega `DATABASE_URL`
3. Pega la connection string de Neon:
   ```
   DATABASE_URL=postgresql://usuario:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Save Changes** → Render se redesplegará automáticamente

#### 5. Inicializar Base de Datos

Una vez que Render termine de redesplegar:

1. En Render → Tu servicio → **Shell** (arriba a la derecha)
2. Ejecuta:
   ```bash
   python init_db.py
   ```

✅ **¡LISTO! Base de datos permanente configurada.**

#### Verificar

- En **Neon Dashboard** → **Tables** → Verás tus tablas (user, visitor_turn, chat_message)
- En tu app web → Registra un turno → Refresca → Debe seguir ahí

---

## 🥈 OPCIÓN 2: Railway.app

**Características:**
- ✅ PostgreSQL gratis con **$5 de crédito/mes**
- ✅ Suficiente para proyectos pequeños (~500 horas)
- ✅ Interface muy linda
- ⚠️ Requiere verificación (pero no tarjeta de crédito)

### Paso a Paso

#### 1. Crear cuenta
1. Ve a **https://railway.app**
2. Sign up con GitHub
3. Verifica tu email

#### 2. Crear proyecto
1. Click **"New Project"**
2. Selecciona **"Provision PostgreSQL"**
3. Espera 10-20 segundos

#### 3. Obtener Connection String
1. Click en tu base de datos PostgreSQL
2. Ve a la pestaña **"Connect"**
3. Copia la **"Postgres Connection URL"**

#### 4. Configurar en Render
Igual que con Neon, pega la URL en `DATABASE_URL`

---

## 🥉 OPCIÓN 3: ElephantSQL

**Características:**
- ✅ PostgreSQL gratis
- ⚠️ Solo **20 MB** de storage (muy poco)
- ✅ Bueno para testing, no para producción

### Paso a Paso

#### 1. Crear cuenta
1. Ve a **https://www.elephantsql.com**
2. Sign up (gratis)

#### 2. Crear instancia
1. Click **"Create New Instance"**
2. **Name**: `turnero-municipal`
3. **Plan**: Tiny Turtle (Free)
4. **Region**: US-East-1 (Virginia)
5. Click **"Create instance"**

#### 3. Obtener URL
1. Click en tu instancia
2. Copia la **"URL"** completa

#### 4. Configurar en Render
Pega en `DATABASE_URL`

---

## 🏆 OPCIÓN 4: Render PostgreSQL (Limitado)

Render también ofrece PostgreSQL gratis, pero:
- ⚠️ Se borra después de **90 días de inactividad**
- ✅ Pero si tu app está activa, no se borra
- ✅ 1 GB de storage
- ✅ Integración perfecta (mismo dashboard)

### Paso a Paso

#### 1. Crear base de datos
1. En Render Dashboard → **"New +"** → **"PostgreSQL"**
2. **Name**: `turnero-db`
3. **Plan**: Free
4. Click **"Create Database"**

#### 2. Conectar a tu Web Service
1. Una vez creada, ve a la pestaña **"Connect"**
2. Copia la **"Internal Database URL"**
3. Ve a tu Web Service → **Environment**
4. Edita `DATABASE_URL` y pega la URL

#### 3. Inicializar
En Render Shell:
```bash
python init_db.py
```

---

## 📊 Comparación Rápida

| Servicio | Storage Gratis | Límite | Requiere Tarjeta | Recomendación |
|----------|----------------|--------|------------------|---------------|
| **Neon.tech** | 10 GB | Ilimitado en tiempo | ❌ No | ⭐⭐⭐⭐⭐ |
| **Railway** | ~$5/mes crédito | 500 horas/mes | ❌ No | ⭐⭐⭐⭐ |
| **Render Postgres** | 1 GB | 90 días inactividad | ❌ No | ⭐⭐⭐ |
| **ElephantSQL** | 20 MB | Muy poco | ❌ No | ⭐⭐ |

---

## 🎯 Mi Recomendación

### Para tu proyecto: **Neon.tech** 🏆

**Razones:**
1. 10 GB es más que suficiente (tienes espacio para ~100,000 turnos)
2. No caduca nunca
3. Auto-pausa cuando no se usa (no gasta recursos)
4. Serverless = muy rápido
5. Setup súper fácil

**Tiempo**: 5 minutos en total

---

## 🆘 Si Neon Tampoco Funciona

Opciones adicionales:

### 5. **Vercel Postgres**
- https://vercel.com/storage/postgres
- Gratis con límites
- Requiere cuenta Vercel

### 6. **PlanetScale** (MySQL)
- https://planetscale.com
- 5 GB gratis
- ⚠️ Es MySQL (tendrías que cambiar un poco el código)

### 7. **MongoDB Atlas** (NoSQL)
- https://www.mongodb.com/atlas
- 512 MB gratis
- ⚠️ Es NoSQL (requiere cambiar mucho el código)

---

## 🔧 Alternativa Local (No Recomendada)

Si NINGUNA opción funciona, podrías:
1. Correr PostgreSQL en tu PC
2. Usar **ngrok** para exponerlo a internet
3. Tu app en Render se conecta a tu PC

**Problemas:**
- Tu PC debe estar prendida 24/7
- Posibles problemas de red/firewall
- No es profesional

---

## 📝 Notas Importantes

### URL Encoding
Si tu contraseña tiene caracteres especiales, codifícalos:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- Espacio → `%20`

### SSL Mode
Algunas bases de datos requieren `?sslmode=require` al final de la URL:
```
postgresql://user:pass@host:5432/db?sslmode=require
```

### Testing
Después de configurar, siempre testea:
1. Registra un turno
2. Redesplega tu app en Render (Manual Deploy)
3. Verifica que el turno siga ahí

---

## 🚀 Próximos Pasos

1. ☐ Elegir servicio (recomiendo Neon.tech)
2. ☐ Crear cuenta
3. ☐ Crear proyecto/base de datos
4. ☐ Copiar connection string
5. ☐ Configurar en Render (`DATABASE_URL`)
6. ☐ Redesplegar
7. ☐ Ejecutar `python init_db.py` en Shell
8. ☐ ¡Probar!

---

## 💡 Tip Pro

Una vez que funcione, guarda tu connection string en un lugar seguro (password manager, archivo local cifrado, etc.) por si algún día necesitas reconfigurar.

---

¿Empezamos con Neon? Es literalmente 5 minutos 🚀
