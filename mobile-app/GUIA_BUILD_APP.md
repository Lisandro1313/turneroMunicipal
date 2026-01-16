# 📱 Guía Completa: App Móvil Standalone

## 🎯 Objetivo
Convertir la app de Expo Go a una **app instalable** (APK/IPA) con **notificaciones push**.

---

## 📋 REQUISITOS PREVIOS

### 1. Instalar EAS CLI
```bash
npm install -g eas-cli
```

### 2. Crear cuenta en Expo
- Ve a https://expo.dev
- Sign up / Login

### 3. Login desde terminal
```bash
cd mobile-app
eas login
```

---

## 🔧 CONFIGURACIÓN INICIAL

### 1. Inicializar EAS en el proyecto
```bash
cd mobile-app
eas build:configure
```

Esto te pedirá:
- **Project ID**: Se creará automáticamente
- Copia el `projectId` que te muestre

### 2. Actualizar app.json
Reemplaza `YOUR_PROJECT_ID_HERE` en `app.json` con tu Project ID real:
```json
"extra": {
  "eas": {
    "projectId": "abc123-tu-project-id-real"
  }
}
```

---

## 📱 OPCIÓN 1: BUILD ANDROID (APK) - RECOMENDADO PARA EMPEZAR

### Paso 1: Crear el Build
```bash
npm run build:android:preview
```

Este comando:
- ✅ Crea un APK instalable
- ✅ No requiere Google Play Store
- ✅ Se puede distribuir directamente (por WhatsApp, email, etc.)
- ⏱️ Tarda 10-15 minutos

### Paso 2: Descargar el APK
Una vez que termine, el comando te dará:
1. Un link para descargar el APK
2. Un QR code que puedes escanear con el celular

### Paso 3: Instalar en Android
1. Descarga el APK en tu celular
2. Android te pedirá permiso para instalar de "fuentes desconocidas"
3. Acepta y listo!

### Paso 4: Probar notificaciones
La app ya tiene configuradas las notificaciones, solo falta el backend que envíe push notifications.

---

## 🍎 OPCIÓN 2: BUILD iOS (iPhone)

**NOTA**: Para iOS necesitas:
- ❌ Una cuenta de Apple Developer ($99/año)
- ❌ Una Mac para hacer el build (o usar EAS cloud)

Si querés probar en iPhone:
```bash
npm run build:ios
```

---

## 🔔 CONFIGURAR NOTIFICACIONES PUSH

### Backend (Flask)

Necesitamos agregar Expo Push Notifications al backend. Creá este archivo:

**app/push_notifications.py**:
```python
import requests
import json
from typing import List, Dict

EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'

def send_push_notification(
    expo_tokens: List[str],
    title: str,
    body: str,
    data: Dict = None
):
    """
    Envía una notificación push a dispositivos móviles
    
    Args:
        expo_tokens: Lista de tokens de Expo Push Notifications
        title: Título de la notificación
        body: Mensaje de la notificación
        data: Datos adicionales (opcional)
    """
    if not expo_tokens:
        return
    
    messages = []
    for token in expo_tokens:
        if not token.startswith('ExponentPushToken'):
            continue
            
        messages.append({
            'to': token,
            'sound': 'default',
            'title': title,
            'body': body,
            'data': data or {},
            'priority': 'high',
            'channelId': 'default'
        })
    
    if not messages:
        return
    
    try:
        response = requests.post(
            EXPO_PUSH_URL,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            data=json.dumps(messages)
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error enviando push notification: {e}")
        return None


# Ejemplos de uso:

def notificar_nuevo_turno(area: str, numero_turno: int):
    """Notifica a los pisos que hay un nuevo turno"""
    # Obtener tokens de los usuarios de ese piso
    # tokens = obtener_tokens_piso(area)
    
    send_push_notification(
        expo_tokens=['ExponentPushToken[xxxxxx]'],  # Reemplazar con tokens reales
        title='Nuevo turno en espera',
        body=f'Turno #{numero_turno} para {area}',
        data={'turno_id': numero_turno, 'area': area}
    )


def notificar_turno_llamado(visitante_nombre: str, piso: str):
    """Notifica a recepción que un turno fue llamado"""
    send_push_notification(
        expo_tokens=['ExponentPushToken[xxxxxx]'],
        title='Turno llamado',
        body=f'{visitante_nombre} fue llamado por {piso}',
        data={'piso': piso}
    )
```

### Frontend Móvil

En `src/services/notifications.js`, agrega función para registrar el token:

```javascript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import api from './api';

export async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#2196F3',
    });
  }

  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      alert('No se pudieron obtener permisos para notificaciones');
      return;
    }
    
    token = (await Notifications.getExpoPushTokenAsync()).data;
    console.log('Push Token:', token);
    
    // Enviar token al backend
    try {
      await api.post('/api/register-push-token', { token });
    } catch (error) {
      console.error('Error registrando token:', error);
    }
  } else {
    alert('Debes usar un dispositivo físico para recibir notificaciones');
  }

  return token;
}
```

---

## 🚀 DISTRIBUCIÓN

### Para Testing (Android)
1. **Opción A - Directo**: Pasa el APK por WhatsApp/Email
2. **Opción B - Firebase App Distribution**: Gratis, para equipos
3. **Opción C - Link público**: EAS Build genera un link compartible

### Para Producción
1. **Google Play Store** (Android):
   - Necesitas una cuenta de desarrollador ($25 único)
   - Sube el APK o AAB
   - Proceso de revisión ~1-3 días

2. **Apple App Store** (iOS):
   - Necesitas Apple Developer ($99/año)
   - Proceso de revisión ~1-7 días

---

## 📝 COMANDOS ÚTILES

```bash
# Ver builds anteriores
eas build:list

# Cancelar un build en progreso
eas build:cancel

# Ver logs de un build
eas build:view BUILD_ID

# Crear build de producción (AAB para Play Store)
eas build --platform android --profile production

# Build local (más rápido, requiere Android Studio)
eas build --platform android --local
```

---

## 🔍 TROUBLESHOOTING

### Error: "No se puede instalar el APK"
- Solución: Habilita "Instalar apps de fuentes desconocidas" en Ajustes

### Error: "Build failed"
- Revisa los logs con `eas build:view BUILD_ID`
- Asegúrate que todos los assets existen (icon.png, splash.png, etc.)

### Notificaciones no llegan
1. Verifica que el token se esté registrando correctamente
2. Revisa los permisos de notificaciones en el celular
3. Usa https://expo.dev/notifications para testear tokens

---

## 📊 PRÓXIMOS PASOS

1. ✅ **Hacer el primer build**: `npm run build:android:preview`
2. ✅ **Instalar y probar en tu celular**
3. ⏳ **Agregar registro de push tokens en el backend**
4. ⏳ **Testear notificaciones reales**
5. ⏳ **Decidir si vas a publicar en Play Store**

---

## 💡 TIPS

- 🆓 **EAS Build**: 30 builds gratis/mes con cuenta gratuita
- 📦 **Preview builds** (APK): Perfecto para testing
- 🏪 **Production builds** (AAB): Para Google Play Store
- 🔔 **Expo Push**: Gratis para notificaciones ilimitadas
- 📱 **Over-the-Air Updates**: Puedes actualizar la app sin rebuild (con `expo-updates`)
