import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { turnosService } from '../services/api';

export default function RecepcionScreen({ navigation }) {
  const { logout } = useAuth();
  const [formData, setFormData] = useState({
    nombre: '',
    dni: '',
    piso: '1',
    area: '',
    motivo: '',
  });
  const [loading, setLoading] = useState(false);

  const areas = {
    1: ['Intendencia', 'Secretaría', 'Tesorería', 'Obras Públicas'],
    2: ['Desarrollo Social', 'Cultura', 'Deportes', 'Turismo'],
    3: ['Sistemas', 'Recursos Humanos', 'Compras', 'Legal'],
  };

  const handleSubmit = async () => {
    // Validaciones
    if (!formData.nombre.trim()) {
      Alert.alert('Error', 'Por favor ingrese el nombre del visitante');
      return;
    }

    if (!formData.area.trim()) {
      Alert.alert('Error', 'Por favor seleccione un área');
      return;
    }

    if (!formData.motivo.trim()) {
      Alert.alert('Error', 'Por favor ingrese el motivo de la visita');
      return;
    }

    setLoading(true);

    try {
      const response = await turnosService.createTurno({
        nombre: formData.nombre.trim(),
        dni: formData.dni.trim() || null,
        piso: parseInt(formData.piso),
        area: formData.area,
        motivo: formData.motivo.trim(),
      });

      if (response.success) {
        Alert.alert(
          '✅ Turno Creado',
          `${formData.nombre} fue agregado correctamente`,
          [
            {
              text: 'OK',
              onPress: () => {
                // Limpiar formulario
                setFormData({
                  nombre: '',
                  dni: '',
                  piso: '1',
                  area: '',
                  motivo: '',
                });
              },
            },
          ]
        );
      }
    } catch (error) {
      Alert.alert('Error', 'No se pudo crear el turno. Intente nuevamente.');
      console.error('Error creando turno:', error);
    } finally {
      setLoading(false);
    }
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

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Recepción</Text>
          <Text style={styles.headerSubtitle}>Crear nuevo turno</Text>
        </View>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn}>
          <Text style={styles.logoutText}>Salir</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.scrollContent}>
        <View style={styles.form}>
          <Text style={styles.label}>Nombre del visitante *</Text>
          <TextInput
            style={styles.input}
            value={formData.nombre}
            onChangeText={(text) => setFormData({ ...formData, nombre: text })}
            placeholder="Ej: Juan Pérez"
            autoCapitalize="words"
          />

          <Text style={styles.label}>DNI (opcional)</Text>
          <TextInput
            style={styles.input}
            value={formData.dni}
            onChangeText={(text) => setFormData({ ...formData, dni: text })}
            placeholder="Ej: 12345678"
            keyboardType="numeric"
          />

          <Text style={styles.label}>Piso de destino *</Text>
          <View style={styles.pisoButtons}>
            {['1', '2', '3'].map((piso) => (
              <TouchableOpacity
                key={piso}
                style={[
                  styles.pisoBtn,
                  formData.piso === piso && styles.pisoBtnActive,
                ]}
                onPress={() => {
                  setFormData({ ...formData, piso, area: '' });
                }}
              >
                <Text
                  style={[
                    styles.pisoBtnText,
                    formData.piso === piso && styles.pisoBtnTextActive,
                  ]}
                >
                  Piso {piso}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.label}>Área de destino *</Text>
          <View style={styles.areaContainer}>
            {areas[formData.piso].map((area) => (
              <TouchableOpacity
                key={area}
                style={[
                  styles.areaBtn,
                  formData.area === area && styles.areaBtnActive,
                ]}
                onPress={() => setFormData({ ...formData, area })}
              >
                <Text
                  style={[
                    styles.areaBtnText,
                    formData.area === area && styles.areaBtnTextActive,
                  ]}
                >
                  {area}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.label}>Motivo de la visita *</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={formData.motivo}
            onChangeText={(text) => setFormData({ ...formData, motivo: text })}
            placeholder="Ej: Consulta sobre habilitación comercial"
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />

          <TouchableOpacity
            style={[styles.submitBtn, loading && styles.submitBtnDisabled]}
            onPress={handleSubmit}
            disabled={loading}
          >
            <Text style={styles.submitBtnText}>
              {loading ? 'Creando...' : '✅ Crear Turno'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#FF5722',
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
  content: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  form: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    minHeight: 100,
    paddingTop: 12,
  },
  pisoButtons: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 8,
  },
  pisoBtn: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#ddd',
    alignItems: 'center',
  },
  pisoBtnActive: {
    backgroundColor: '#2196F3',
    borderColor: '#2196F3',
  },
  pisoBtnText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#666',
  },
  pisoBtnTextActive: {
    color: '#fff',
  },
  areaContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  areaBtn: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#f9f9f9',
  },
  areaBtnActive: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  areaBtnText: {
    fontSize: 14,
    color: '#666',
  },
  areaBtnTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  submitBtn: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 24,
  },
  submitBtnDisabled: {
    backgroundColor: '#ccc',
  },
  submitBtnText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
