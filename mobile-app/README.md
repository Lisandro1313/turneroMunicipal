# 📱 Turnero Municipal - App Móvil

App móvil para el sistema de gestión de turnos municipal, con soporte para notificaciones push y funcionamiento standalone.

## ✨ Características

- 🔐 Login para Recepción y Pisos (1, 2, 3)
- 📋 **Recepción**: Registrar visitantes, ver cola en tiempo real
- 📞 **Pisos**: Llamar y atender visitantes
- 🔔 **Notificaciones Push**: Recibe alertas de nuevos turnos
- 📱 **Standalone**: Se instala como app nativa (no requiere Expo Go)
- 🎨 UI moderna con React Native

## 🚀 Quick Start

### Desarrollo con Expo Go (Testing rápido)

```bash
# Instalar dependencias
npm install

# Iniciar el servidor
npm start

# Escanea el QR con Expo Go en tu celular
```

### Build Standalone (APK instalable)

Para crear una app instalable que no requiere Expo Go:

**Ver guía completa:** [GUIA_BUILD_APP.md](GUIA_BUILD_APP.md)

```bash
# Instalar EAS CLI
npm install -g eas-cli

# Login en Expo
eas login

# Configurar proyecto
eas build:configure

# Crear APK para Android
npm run build:android:preview
```

## 📦 Estructura del proyecto

```
mobile-app/
├── App.js                          # Componente principal
├── app.json                        # Configuración de Expo
├── package.json                    # Dependencias
├── src/
│   ├── context/
│   │   └── AuthContext.js         # Contexto de autenticación
│   ├── screens/
│   │   ├── LoginScreen.js         # Pantalla de login
│   │   ├── PisoScreen.js          # Pantalla para piso1/2/3
│   │   └── RecepcionScreen.js     # Pantalla para recepción
│   └── services/
│       ├── api.js                 # Cliente HTTP y endpoints
│       └── notifications.js       # Manejo de notificaciones push
```

## 🔐 Usuarios de prueba

La aplicación viene con usuarios precargados:

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| recepcion | recepcion123 | Recepcionista |
| piso1 | piso1 | Piso 1 |
| piso2 | piso2 | Piso 2 |
| piso3 | piso3 | Piso 3 |

## 🔔 Notificaciones Push

Las notificaciones se envían automáticamente cuando:
- **Nuevo turno**: Un visitante llega y se registra en recepción
- **Turno autorizado**: Recepción autoriza la subida de un visitante

### Configuración
- Las notificaciones funcionan solo en dispositivos físicos (no en emuladores)
- Se requiere permisos del sistema operativo (se solicitan automáticamente)
- El token de notificaciones se registra al hacer login

## 🎯 Funcionalidades

### 👤 Recepcionista
- Crear nuevos turnos
- Seleccionar piso y área de destino
- Ingresar nombre, DNI y motivo de visita
- Interfaz simple y rápida

### 🏢 Usuario de Piso (piso1/2/3)
- Ver turnos en espera para su piso
- Autorizar subida de visitantes
- Marcar turnos como atendidos
- Recibir notificaciones push de nuevos turnos
- Auto-refresh cada 15 segundos

## 🔧 Configuración del Backend

La app se conecta al backend en:
- **Desarrollo local**: http://127.0.0.1:5000
- **Producción**: https://turneromunicipal.onrender.com

Para cambiar la URL del backend, editar `src/services/api.js`:
```javascript
const API_URL = 'http://tu-servidor.com';
```

## 📱 Compilación para Producción

### Build APK (Android)
```bash
npm install -g eas-cli
eas login
eas build --platform android
```

### Build IPA (iOS)
```bash
eas build --platform ios
```

## 🐛 Troubleshooting

### Las notificaciones no funcionan
- Verificar que estás usando un dispositivo físico (no emulador)
- Revisar que los permisos de notificaciones estén habilitados
- Comprobar que el backend esté corriendo

### Error de conexión al backend
- Verificar que el servidor Flask esté corriendo
- Si usas desarrollo local, cambiar API_URL a la IP local de tu PC
- Verificar que no haya firewall bloqueando el puerto 5000

### La sesión no se mantiene
- Borrar datos de la app y volver a hacer login
- Verificar que AsyncStorage tenga permisos

## 📚 Tecnologías utilizadas

- **React Native** 0.73.0
- **Expo** ~50.0.0
- **React Navigation** 6.x
- **Axios** para peticiones HTTP
- **Expo Notifications** para push notifications
- **AsyncStorage** para persistencia local

## 🤝 Integración con Backend

El backend Flask provee los siguientes endpoints:

- `POST /api/auth/login` - Autenticación
- `GET /api/turnos/en_espera/{piso}` - Obtener turnos
- `POST /api/turnos/crear` - Crear nuevo turno
- `POST /api/turnos/{id}/autorizar` - Autorizar subida
- `POST /api/turnos/{id}/atender` - Marcar atendido
- `POST /api/notifications/register-token` - Registrar token push

## 📄 Licencia

MIT License
