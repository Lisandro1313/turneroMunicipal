# Plan para Implementar App Mobile - Turnero Municipal

## 📱 Objetivo
Crear una aplicación móvil que permita a los usuarios usar el sistema igual que en web, pero con notificaciones push cuando:
- Se crea un nuevo turno para su piso
- Un visitante es autorizado a subir
- Un turno cambia de estado

## 🎯 Recomendación: React Native + Expo

### ¿Por qué React Native + Expo?
- **Multiplataforma:** Una sola codebase para iOS y Android
- **Expo:** Facilita el desarrollo y testing sin necesidad de Xcode/Android Studio
- **Push Notifications:** Expo tiene servicio integrado de notificaciones
- **Fácil deployment:** Puedes publicar en App Store y Google Play
- **Gran comunidad:** Muchos recursos y bibliotecas disponibles

## 🏗️ Arquitectura Propuesta

```
┌─────────────────┐
│   App Mobile    │
│  (React Native) │
└────────┬────────┘
         │
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Backend Flask  │
│  + Socket.IO    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Render.com)  │
└─────────────────┘
```

## 📋 Paso 1: Modificaciones en el Backend

### 1.1 Agregar Socket.IO para Notificaciones en Tiempo Real

**Instalar dependencias:**
```bash
pip install python-socketio python-socketio[asyncio] flask-socketio
```

**Actualizar `requirements.txt`:**
```txt
Flask-SocketIO==5.3.5
python-socketio==5.10.0
```

### 1.2 Crear endpoint para registrar tokens de notificaciones

**Nuevo archivo: `app/notifications.py`**
```python
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from . import db

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

# Tabla para guardar tokens de dispositivos
class DeviceToken(db.Model):
    __tablename__ = 'device_token'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(500), nullable=False, unique=True)
    platform = db.Column(db.String(20), nullable=False)  # 'ios' o 'android'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@notifications_bp.route('/register-token', methods=['POST'])
@login_required
def register_token():
    """Registrar token de notificaciones push del dispositivo"""
    data = request.get_json()
    token = data.get('token')
    platform = data.get('platform')  # 'ios' o 'android'
    
    if not token or not platform:
        return jsonify({'error': 'Token y platform son requeridos'}), 400
    
    # Buscar o crear token
    device = DeviceToken.query.filter_by(token=token).first()
    if device:
        device.user_id = current_user.id
        device.updated_at = datetime.utcnow()
    else:
        device = DeviceToken(
            user_id=current_user.id,
            token=token,
            platform=platform
        )
        db.session.add(device)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Token registrado'})
```

### 1.3 Implementar servicio de notificaciones

**Nuevo archivo: `app/push_notifications.py`**
```python
import requests
from app.models import User
from app.notifications import DeviceToken

def send_push_notification(user_id, title, body, data=None):
    """
    Enviar notificación push a un usuario específico
    Usa Expo Push Notifications
    """
    tokens = DeviceToken.query.filter_by(user_id=user_id).all()
    
    if not tokens:
        return
    
    expo_tokens = [t.token for t in tokens if t.token.startswith('ExponentPushToken')]
    
    if not expo_tokens:
        return
    
    # Preparar mensaje para Expo
    messages = []
    for token in expo_tokens:
        messages.append({
            'to': token,
            'sound': 'default',
            'title': title,
            'body': body,
            'data': data or {},
        })
    
    # Enviar a Expo Push API
    response = requests.post(
        'https://exp.host/--/api/v2/push/send',
        json=messages,
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    )
    
    return response.json()

def notify_new_turn(turn):
    """Notificar a usuarios del piso cuando hay un nuevo turno"""
    # Buscar usuarios del piso correspondiente
    piso_role = f'piso{turn.piso}'
    users = User.query.filter_by(role=piso_role, is_active=True).all()
    
    for user in users:
        send_push_notification(
            user.id,
            f'Nuevo turno - {turn.area_nombre}',
            f'{turn.nombre} está esperando en recepción',
            data={
                'type': 'new_turn',
                'turn_id': turn.id,
                'screen': 'TurnoDetalle'
            }
        )

def notify_turn_authorized(turn):
    """Notificar cuando un turno es autorizado"""
    # Buscar usuarios del piso
    piso_role = f'piso{turn.piso}'
    users = User.query.filter_by(role=piso_role, is_active=True).all()
    
    for user in users:
        send_push_notification(
            user.id,
            f'Visitante autorizado',
            f'{turn.nombre} está subiendo al piso {turn.piso}',
            data={
                'type': 'turn_authorized',
                'turn_id': turn.id,
                'screen': 'TurnoDetalle'
            }
        )
```

### 1.4 Integrar notificaciones en la creación de turnos

**Modificar `app/turns.py`:**
```python
from app.push_notifications import notify_new_turn, notify_turn_authorized

# En api_create_turn, después de crear el turno:
@turns_bp.route('/api/turnos', methods=['POST'])
@login_required
def api_create_turn():
    # ... código existente ...
    
    db.session.add(turno)
    db.session.commit()
    
    # 🔔 Enviar notificación push
    notify_new_turn(turno)
    
    return jsonify({
        'success': True,
        'data': turno.to_dict(),
        'message': 'Turno creado exitosamente'
    }), 201

# En api_autorizar_turno, después de autorizar:
@turns_bp.route('/api/turnos/<int:turno_id>/autorizar', methods=['POST'])
@login_required
def api_autorizar_turno(turno_id):
    # ... código existente ...
    
    turno.autorizar_subida(llamado_por=data.get('llamado_por', current_user.username))
    
    # 🔔 Enviar notificación push
    notify_turn_authorized(turno)
    
    return jsonify({
        'success': True,
        'data': turno.to_dict(),
        'message': 'Turno autorizado'
    })
```

## 📋 Paso 2: Crear la App Mobile con React Native

### 2.1 Crear proyecto con Expo

```bash
# Instalar Expo CLI globalmente
npm install -g expo-cli

# Crear nuevo proyecto
npx create-expo-app turnero-municipal-mobile
cd turnero-municipal-mobile

# Instalar dependencias necesarias
npm install @react-navigation/native @react-navigation/stack
npm install axios
npm install expo-notifications
npm install @react-native-async-storage/async-storage
```

### 2.2 Estructura de carpetas propuesta

```
turnero-municipal-mobile/
├── src/
│   ├── screens/           # Pantallas de la app
│   │   ├── LoginScreen.js
│   │   ├── RecepcionScreen.js
│   │   ├── PisoScreen.js
│   │   ├── TurnoDetalleScreen.js
│   │   └── EstadisticasScreen.js
│   ├── components/        # Componentes reutilizables
│   │   ├── TurnoCard.js
│   │   ├── AreaSelector.js
│   │   └── NotificationBadge.js
│   ├── services/          # Servicios de API
│   │   ├── api.js
│   │   ├── auth.js
│   │   └── notifications.js
│   ├── navigation/        # Navegación
│   │   └── AppNavigator.js
│   ├── context/          # Context API
│   │   └── AuthContext.js
│   └── utils/            # Utilidades
│       └── constants.js
├── App.js
└── package.json
```

### 2.3 Ejemplo de código - Servicio de API

**`src/services/api.js`:**
```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://turneromunicipal.onrender.com';  // O tu URL local en desarrollo

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username, password) => {
    const response = await api.post('/login', { username, password });
    return response.data;
  },
  logout: async () => {
    await AsyncStorage.removeItem('authToken');
  },
};

export const turnosService = {
  getTurnos: async (filters = {}) => {
    const response = await api.get('/api/turnos', { params: filters });
    return response.data;
  },
  
  getTurnosEnEspera: async (areaKey) => {
    const response = await api.get('/api/turnos/en-espera', {
      params: { area_key: areaKey }
    });
    return response.data;
  },
  
  createTurno: async (turnoData) => {
    const response = await api.post('/api/turnos', turnoData);
    return response.data;
  },
  
  autorizarTurno: async (turnoId, llamadoPor) => {
    const response = await api.post(`/api/turnos/${turnoId}/autorizar`, {
      llamado_por: llamadoPor
    });
    return response.data;
  },
  
  marcarAtendido: async (turnoId, atendidoPor) => {
    const response = await api.post(`/api/turnos/${turnoId}/atender`, {
      atendido_por: atendidoPor
    });
    return response.data;
  },
};

export default api;
```

### 2.4 Ejemplo - Servicio de Notificaciones

**`src/services/notifications.js`:**
```javascript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import api from './api';

// Configurar cómo se muestran las notificaciones
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotificationsAsync() {
  let token;
  
  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      alert('¡Necesitamos permisos para enviarte notificaciones!');
      return;
    }
    
    token = (await Notifications.getExpoPushTokenAsync()).data;
    console.log('Push token:', token);
    
    // Registrar token en el backend
    await api.post('/api/notifications/register-token', {
      token,
      platform: Platform.OS,
    });
    
  } else {
    alert('Debes usar un dispositivo físico para recibir notificaciones push');
  }
  
  return token;
}

export function setupNotificationListeners(onNotificationReceived) {
  // Notificación recibida mientras la app está en primer plano
  const notificationListener = Notifications.addNotificationReceivedListener(notification => {
    console.log('Notificación recibida:', notification);
    if (onNotificationReceived) {
      onNotificationReceived(notification);
    }
  });
  
  // Usuario tocó la notificación
  const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
    console.log('Usuario tocó la notificación:', response);
    const data = response.notification.request.content.data;
    
    // Navegar a la pantalla correspondiente
    if (data.screen) {
      // navigation.navigate(data.screen, { turnId: data.turn_id });
    }
  });
  
  return () => {
    Notifications.removeNotificationSubscription(notificationListener);
    Notifications.removeNotificationSubscription(responseListener);
  };
}
```

### 2.5 Ejemplo - Pantalla de Piso

**`src/screens/PisoScreen.js`:**
```javascript
import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  FlatList, 
  TouchableOpacity, 
  StyleSheet, 
  RefreshControl 
} from 'react-native';
import { turnosService } from '../services/api';

export default function PisoScreen({ route }) {
  const { numeroPiso, areas } = route.params;
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  const loadTurnos = async () => {
    try {
      setLoading(true);
      const response = await turnosService.getTurnos({
        piso: numeroPiso,
        estado: 'ESPERA'
      });
      setTurnos(response.data);
    } catch (error) {
      console.error('Error cargando turnos:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAutorizar = async (turnoId) => {
    try {
      await turnosService.autorizarTurno(turnoId, 'Usuario Mobile');
      loadTurnos(); // Recargar lista
    } catch (error) {
      console.error('Error autorizando turno:', error);
    }
  };
  
  useEffect(() => {
    loadTurnos();
    
    // Recargar cada 30 segundos
    const interval = setInterval(loadTurnos, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const renderTurno = ({ item }) => (
    <View style={styles.turnoCard}>
      <Text style={styles.turnoNombre}>{item.nombre}</Text>
      <Text style={styles.turnoArea}>{item.area_nombre}</Text>
      <Text style={styles.turnoDNI}>DNI: {item.dni || 'N/A'}</Text>
      <Text style={styles.turnoMotivo}>{item.motivo_texto}</Text>
      
      <TouchableOpacity 
        style={styles.btnAutorizar}
        onPress={() => handleAutorizar(item.id)}
      >
        <Text style={styles.btnText}>Autorizar Subida</Text>
      </TouchableOpacity>
    </View>
  );
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Piso {numeroPiso} - Turnos en Espera</Text>
      
      <FlatList
        data={turnos}
        renderItem={renderTurno}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={loadTurnos} />
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>No hay turnos en espera</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  turnoCard: {
    backgroundColor: 'white',
    padding: 16,
    marginBottom: 12,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  turnoNombre: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  turnoArea: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  turnoDNI: {
    fontSize: 14,
    color: '#999',
  },
  turnoMotivo: {
    fontSize: 14,
    marginTop: 8,
    marginBottom: 12,
  },
  btnAutorizar: {
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  btnText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 40,
    fontSize: 16,
    color: '#999',
  },
});
```

## 📋 Paso 3: Testing y Deployment

### 3.1 Testing Local

```bash
# En la carpeta del proyecto mobile
npm start

# Escanear QR con Expo Go app (iOS/Android)
```

### 3.2 Build para Producción

```bash
# Configurar app.json con tu información
# Luego construir:

# Para Android
eas build --platform android

# Para iOS
eas build --platform ios
```

## ⚡ Resumen de Próximos Pasos

1. ✅ Backend local funcionando
2. ✅ Usuarios separados por pisos
3. 🔲 Agregar Socket.IO para notificaciones en tiempo real
4. 🔲 Crear endpoint para registrar tokens de dispositivos
5. 🔲 Implementar servicio de notificaciones push
6. 🔲 Crear app mobile con React Native + Expo
7. 🔲 Implementar pantallas principales (Login, Piso, Recepción)
8. 🔲 Integrar notificaciones push en la app
9. 🔲 Testing completo
10. 🔲 Publicar en App Store y Google Play

## 🎯 Alternativas más Simples

Si quieres algo más rápido:

### Opción 1: PWA (Progressive Web App)
- Usar el sitio web existente
- Agregar manifest.json y service worker
- Se puede "instalar" como app nativa
- Notificaciones web push (limitadas en iOS)

### Opción 2: Capacitor
- Convertir tu web actual en app nativa
- Más rápido que React Native
- Reutilizas todo el código HTML/CSS/JS existente

¿Quieres que continúe con alguna de estas opciones?
