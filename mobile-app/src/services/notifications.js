import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { notificationsService } from './api';

export async function registerForPushNotificationsAsync() {
  let token;
  
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
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
      alert('¡Necesitamos permisos para enviarte notificaciones de nuevos turnos!');
      return;
    }
    
    try {
      token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log('Push token obtenido:', token);
      
      // Registrar token en el backend
      await notificationsService.registerToken(token, Platform.OS);
      console.log('Token registrado en el backend');
      
      return token;
    } catch (error) {
      console.error('Error obteniendo token:', error);
    }
  } else {
    alert('Debes usar un dispositivo físico para recibir notificaciones push');
  }
  
  return null;
}

export function setupNotificationListeners(onNotificationReceived, onNotificationTapped) {
  // Notificación recibida mientras la app está en primer plano
  const notificationListener = Notifications.addNotificationReceivedListener(notification => {
    console.log('📱 Notificación recibida:', notification);
    if (onNotificationReceived) {
      onNotificationReceived(notification);
    }
  });
  
  // Usuario tocó la notificación
  const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
    console.log('👆 Usuario tocó la notificación:', response);
    const data = response.notification.request.content.data;
    
    if (onNotificationTapped) {
      onNotificationTapped(data);
    }
  });
  
  return () => {
    Notifications.removeNotificationSubscription(notificationListener);
    Notifications.removeNotificationSubscription(responseListener);
  };
}
