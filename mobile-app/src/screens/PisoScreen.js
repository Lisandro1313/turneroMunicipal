import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { turnosService } from '../services/api';

export default function PisoScreen({ route, navigation }) {
  const { numeroPiso } = route.params;
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    loadTurnos();
    
    // Auto-refresh cada 15 segundos
    const interval = setInterval(loadTurnos, 15000);
    return () => clearInterval(interval);
  }, []);

  const loadTurnos = async () => {
    try {
      setLoading(true);
      const response = await turnosService.getTurnosEnEspera(numeroPiso);
      if (response.success) {
        setTurnos(response.data);
      }
    } catch (error) {
      console.error('Error cargando turnos:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleAutorizar = async (turnoId, nombreVisitante) => {
    Alert.alert(
      'Autorizar subida',
      `¿Llamar a ${nombreVisitante}?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sí, Llamar',
          onPress: async () => {
            try {
              const response = await turnosService.autorizarTurno(
                turnoId,
                user?.username || 'Usuario Mobile'
              );
              if (response.success) {
                Alert.alert('✅ Éxito', 'Visitante autorizado a subir');
                loadTurnos();
              }
            } catch (error) {
              Alert.alert('Error', 'No se pudo autorizar el turno');
              console.error('Error autorizando:', error);
            }
          },
        },
      ]
    );
  };

  const handleMarcarAtendido = async (turnoId, nombreVisitante) => {
    Alert.alert(
      'Marcar como atendido',
      `¿${nombreVisitante} ya fue atendido?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sí, Atendido',
          onPress: async () => {
            try {
              const response = await turnosService.marcarAtendido(
                turnoId,
                user?.username || 'Usuario Mobile'
              );
              if (response.success) {
                Alert.alert('✅ Éxito', 'Turno marcado como atendido');
                loadTurnos();
              }
            } catch (error) {
              Alert.alert('Error', 'No se pudo marcar como atendido');
              console.error('Error marcando atendido:', error);
            }
          },
        },
      ]
    );
  };

  const handleLogout = () => {
    Alert.alert('Cerrar sesión', '¿Estás seguro?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Sí, Salir',
        onPress: async () => {
          await logout();
          navigation.replace('Login');
        },
      },
    ]);
  };

  const renderTurno = ({ item }) => {
    const hora = new Date(item.hora_llegada).toLocaleTimeString('es-AR', {
      hour: '2-digit',
      minute: '2-digit',
    });

    return (
      <View style={styles.turnoCard}>
        <View style={styles.turnoHeader}>
          <Text style={styles.turnoNombre}>{item.nombre}</Text>
          <Text style={styles.turnoHora}>{hora}</Text>
        </View>

        <Text style={styles.turnoArea}>📍 {item.area_nombre}</Text>
        <Text style={styles.turnoDNI}>🆔 DNI: {item.dni || 'No especificado'}</Text>
        <Text style={styles.turnoMotivo}>💬 {item.motivo_texto}</Text>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.btnAutorizar}
            onPress={() => handleAutorizar(item.id, item.nombre)}
          >
            <Text style={styles.btnText}>✅ Autorizar Subida</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.btnAtendido}
            onPress={() => handleMarcarAtendido(item.id, item.nombre)}
          >
            <Text style={styles.btnText}>✔️ Atendido</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Piso {numeroPiso}</Text>
          <Text style={styles.headerSubtitle}>Turnos en espera: {turnos.length}</Text>
        </View>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn}>
          <Text style={styles.logoutText}>Salir</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={turnos}
        renderItem={renderTurno}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => {
            setRefreshing(true);
            loadTurnos();
          }} />
        }
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>✨</Text>
            <Text style={styles.emptyText}>No hay turnos en espera</Text>
            <Text style={styles.emptySubtext}>
              Las notificaciones te avisarán cuando llegue alguien
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  logoutBtn: {
    padding: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 6,
  },
  logoutText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  listContent: {
    padding: 16,
  },
  turnoCard: {
    backgroundColor: '#fff',
    padding: 16,
    marginBottom: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  turnoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  turnoNombre: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  turnoHora: {
    fontSize: 14,
    color: '#2196F3',
    fontWeight: 'bold',
  },
  turnoArea: {
    fontSize: 15,
    color: '#555',
    marginBottom: 4,
  },
  turnoDNI: {
    fontSize: 14,
    color: '#777',
    marginBottom: 4,
  },
  turnoMotivo: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    marginTop: 8,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  btnAutorizar: {
    flex: 1,
    backgroundColor: '#4CAF50',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  btnAtendido: {
    flex: 1,
    backgroundColor: '#2196F3',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  btnText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 15,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 80,
  },
  emptyIcon: {
    fontSize: 80,
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    paddingHorizontal: 40,
  },
});
