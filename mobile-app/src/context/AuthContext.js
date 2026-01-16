import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';
import { registerForPushNotificationsAsync, setupNotificationListeners } from '../services/notifications';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pushToken, setPushToken] = useState(null);

  useEffect(() => {
    // Cargar datos del usuario guardados
    loadUser();
    
    // Configurar listeners de notificaciones
    const cleanup = setupNotificationListeners(
      (notification) => {
        // Notificación recibida
        console.log('Nueva notificación:', notification);
      },
      (data) => {
        // Usuario tocó la notificación
        console.log('Navegando por notificación:', data);
        // Aquí puedes agregar navegación si lo necesitas
      }
    );
    
    return cleanup;
  }, []);

  const loadUser = async () => {
    try {
      const userData = await authService.getUserData();
      if (userData) {
        setUser(userData);
      }
    } catch (error) {
      console.error('Error cargando usuario:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      // Hacer login
      const response = await authService.login(username, password);
      
      // Guardar datos del usuario
      const userData = {
        username,
        role: response.role || 'piso1', // Ajustar según respuesta del servidor
      };
      
      await authService.saveUserData(userData);
      setUser(userData);
      
      // Registrar token para notificaciones push
      try {
        const token = await registerForPushNotificationsAsync();
        setPushToken(token);
      } catch (error) {
        console.error('Error registrando notificaciones:', error);
      }
      
      return { success: true };
    } catch (error) {
      console.error('Error en login:', error);
      return { 
        success: false, 
        error: error.response?.data?.message || 'Error de conexión' 
      };
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
      setPushToken(null);
    } catch (error) {
      console.error('Error en logout:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, pushToken }}>
      {children}
    </AuthContext.Provider>
  );
};
