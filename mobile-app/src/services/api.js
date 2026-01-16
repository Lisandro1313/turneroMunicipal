import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// IMPORTANTE: Cambia esta URL por la URL de tu servidor
// Para desarrollo local en Android emulator: http://10.0.2.2:5000
// Para desarrollo local en iOS simulator: http://localhost:5000
// Para desarrollo local en dispositivo físico: http://192.168.0.29:5000 (tu IP local)
// Para producción: https://turneromunicipal.onrender.com
const API_URL = 'http://192.168.0.29:5000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('authToken');
    const sessionCookie = await AsyncStorage.getItem('sessionCookie');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    if (sessionCookie) {
      config.headers.Cookie = sessionCookie;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y guardar cookies de sesión
api.interceptors.response.use(
  async (response) => {
    // Guardar cookies de sesión si vienen en la respuesta
    const setCookie = response.headers['set-cookie'];
    if (setCookie) {
      await AsyncStorage.setItem('sessionCookie', setCookie[0]);
    }
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username, password) => {
    const response = await api.post('/api/login', { username, password });
    return response.data;
  },
  
  logout: async () => {
    try {
      await api.get('/logout');
    } catch (error) {
      console.log('Error en logout:', error);
    }
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('sessionCookie');
    await AsyncStorage.removeItem('userData');
  },
  
  saveUserData: async (userData) => {
    await AsyncStorage.setItem('userData', JSON.stringify(userData));
  },
  
  getUserData: async () => {
    const data = await AsyncStorage.getItem('userData');
    return data ? JSON.parse(data) : null;
  },
};

export const turnosService = {
  getTurnos: async (filters = {}) => {
    const response = await api.get('/turns/api/turnos', { params: filters });
    return response.data;
  },
  
  getTurnosEnEspera: async (piso) => {
    const response = await api.get('/turns/api/turnos', {
      params: { estado: 'ESPERA', piso }
    });
    return response.data;
  },
  
  createTurno: async (turnoData) => {
    const response = await api.post('/turns/api/turnos', turnoData);
    return response.data;
  },
  
  autorizarTurno: async (turnoId, llamadoPor) => {
    const response = await api.post(`/turns/api/turnos/${turnoId}/autorizar`, {
      llamado_por: llamadoPor
    });
    return response.data;
  },
  
  marcarAtendido: async (turnoId, atendidoPor) => {
    const response = await api.post(`/turns/api/turnos/${turnoId}/atender`, {
      atendido_por: atendidoPor
    });
    return response.data;
  },
};

export const notificationsService = {
  registerToken: async (token, platform) => {
    const response = await api.post('/api/notifications/register-token', {
      token,
      platform
    });
    return response.data;
  },
  
  unregisterToken: async (token) => {
    const response = await api.post('/api/notifications/unregister-token', {
      token
    });
    return response.data;
  },
};

export default api;
