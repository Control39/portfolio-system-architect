import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  ActivityIndicator
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import io from 'socket.io-client';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const Tab = createBottomTabNavigator();
const { width } = Dimensions.get('window');

// ============================================================================
// ЭКРАН МОНИТОРИНГА
// ============================================================================
function MonitorScreen() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Подключаемся к серверу мониторинга
    const newSocket = io('http://your-server-ip:3000');
    setSocket(newSocket);

    newSocket.on('status-update', (data) => {
      setStatus(data);
      setLoading(false);
    });

    return () => newSocket.close();
  }, []);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007acc" />
        <Text style={styles.loadingText}>Подключение к серверу...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📊 Мониторинг</Text>
        <Text style={styles.timestamp}>
          {new Date(status?.timestamp).toLocaleString()}
        </Text>
      </View>

      {/* Статус Ollama */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Icon name="memory" size={24} color="#007acc" />
          <Text style={styles.cardTitle}>Ollama</Text>
        </View>
        <View style={styles.statusRow}>
          <View style={[
            styles.statusDot,
            status?.ollama?.running ? styles.online : styles.offline
          ]} />
          <Text style={styles.statusText}>
            {status?.ollama?.running ? 'Работает' : 'Не запущен'}
          </Text>
        </View>
        {status?.ollama?.models?.map((model, i) => (
          <View key={i} style={styles.modelRow}>
            <Icon name="model-training" size={16} color="#888" />
            <Text style={styles.modelText}>{model.name}</Text>
            <Text style={styles.modelSize}>{model.size}</Text>
          </View>
        ))}
      </View>

      {/* Конфиги */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Icon name="settings" size={24} color="#007acc" />
          <Text style={styles.cardTitle}>Конфиги</Text>
        </View>
        {Object.entries(status?.configs || {}).map(([name, info]) => (
          <View key={name} style={styles.configRow}>
            <Icon
              name={info.exists ? 'check-circle' : 'error'}
              size={20}
              color={info.exists ? '#2ecc71' : '#e74c3c'}
            />
            <Text style={styles.configName}>{name}</Text>
            <Text style={styles.configSize}>
              {info.exists ? `${(info.size/1024).toFixed(0)}KB` : 'нет'}
            </Text>
          </View>
        ))}
      </View>

      {/* График памяти */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Icon name="memory" size={24} color="#007acc" />
          <Text style={styles.cardTitle}>Память</Text>
        </View>
        {status?.memory && (
          <LineChart
            data={{
              labels: ['Исп.', 'Св.'],
              datasets: [{
                data: [
                  status.memory.heapUsed / 1024 / 1024,
                  (status.memory.heapTotal - status.memory.heapUsed) / 1024 / 1024
                ]
              }]
            }}
            width={width - 60}
            height={200}
            chartConfig={{
              backgroundColor: '#2d2d2d',
              backgroundGradientFrom: '#2d2d2d',
              backgroundGradientTo: '#2d2d2d',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(0, 122, 204, ${opacity})`,
              style: { borderRadius: 16 }
            }}
            style={styles.chart}
          />
        )}
      </View>
    </ScrollView>
  );
}

// ============================================================================
// ЭКРАН КОНФИГУРАЦИИ
// ============================================================================
function ConfigScreen() {
  const [configs, setConfigs] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState(null);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    // Загружаем сохранённые конфиги
    const saved = await AsyncStorage.getItem('configs');
    if (saved) {
      setConfigs(JSON.parse(saved));
    }
  };

  const generateNewConfig = () => {
    Alert.alert(
      'Новый конфиг',
      'Выберите тип конфига:',
      [
        { text: 'Ollama', onPress: () => createOllamaConfig() },
        { text: 'GigaChat', onPress: () => createGigaChatConfig() },
        { text: 'YandexGPT', onPress: () => createYandexConfig() },
        { text: 'Отмена', style: 'cancel' }
      ]
    );
  };

  const createOllamaConfig = () => {
    const newConfig = {
      id: Date.now().toString(),
      name: 'Новая конфигурация',
      type: 'ollama',
      models: [],
      createdAt: new Date().toISOString()
    };
    setConfigs([...configs, newConfig]);
    AsyncStorage.setItem('configs', JSON.stringify([...configs, newConfig]));
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>⚙️ Конфиги</Text>
        <TouchableOpacity style={styles.addButton} onPress={generateNewConfig}>
          <Icon name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <ScrollView>
        {configs.map(config => (
          <TouchableOpacity
            key={config.id}
            style={styles.configCard}
            onPress={() => setSelectedConfig(config)}
          >
            <Icon name="description" size={24} color="#007acc" />
            <View style={styles.configInfo}>
              <Text style={styles.configTitle}>{config.name}</Text>
              <Text style={styles.configType}>{config.type}</Text>
            </View>
            <Text style={styles.configDate}>
              {new Date(config.createdAt).toLocaleDateString()}
            </Text>
          </TouchableOpacity>
        ))}

        {configs.length === 0 && (
          <View style={styles.emptyState}>
            <Icon name="info" size={48} color="#404040" />
            <Text style={styles.emptyText}>
              Нет сохранённых конфигураций
            </Text>
            <TouchableOpacity style={styles.createButton} onPress={generateNewConfig}>
              <Text style={styles.createButtonText}>Создать</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

// ============================================================================
// ЭКРАН УВЕДОМЛЕНИЙ
// ============================================================================
function NotificationsScreen() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Симуляция получения уведомлений
    const interval = setInterval(() => {
      const types = ['info', 'warning', 'error'];
      const type = types[Math.floor(Math.random() * types.length)];
      const messages = {
        info: '✅ Ollama работает нормально',
        warning: '⚠️ Высокая нагрузка на CPU',
        error: '❌ Ошибка подключения к GigaChat'
      };

      setNotifications(prev => [{
        id: Date.now(),
        type,
        message: messages[type],
        time: new Date().toLocaleTimeString()
      }, ...prev].slice(0, 20));
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🔔 Уведомления</Text>
        <TouchableOpacity onPress={() => setNotifications([])}>
          <Icon name="clear-all" size={24} color="#007acc" />
        </TouchableOpacity>
      </View>

      <ScrollView>
        {notifications.map(notif => (
          <View key={notif.id} style={[
            styles.notificationCard,
            notif.type === 'error' && styles.errorCard,
            notif.type === 'warning' && styles.warningCard
          ]}>
            <Icon
              name={
                notif.type === 'error' ? 'error' :
                notif.type === 'warning' ? 'warning' : 'info'
              }
              size={24}
              color={
                notif.type === 'error' ? '#e74c3c' :
                notif.type === 'warning' ? '#f1c40f' : '#2ecc71'
              }
            />
            <View style={styles.notificationContent}>
              <Text style={styles.notificationText}>{notif.message}</Text>
              <Text style={styles.notificationTime}>{notif.time}</Text>
            </View>
          </View>
        ))}

        {notifications.length === 0 && (
          <View style={styles.emptyState}>
            <Icon name="notifications-none" size={48} color="#404040" />
            <Text style={styles.emptyText}>Нет уведомлений</Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

// ============================================================================
// ОСНОВНОЕ ПРИЛОЖЕНИЕ
// ============================================================================
export default function App() {
  return (
    <NavigationContainer>
      <StatusBar barStyle="light-content" backgroundColor="#1e1e1e" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;
            if (route.name === 'Мониторинг') {
              iconName = 'dashboard';
            } else if (route.name === 'Конфиги') {
              iconName = 'settings';
            } else if (route.name === 'Уведомления') {
              iconName = 'notifications';
            }
            return <Icon name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#007acc',
          tabBarInactiveTintColor: '#888',
          tabBarStyle: {
            backgroundColor: '#2d2d2d',
            borderTopColor: '#404040'
          },
          headerStyle: {
            backgroundColor: '#2d2d2d',
          },
          headerTintColor: '#fff',
        })}
      >
        <Tab.Screen name="Мониторинг" component={MonitorScreen} />
        <Tab.Screen name="Конфиги" component={ConfigScreen} />
        <Tab.Screen name="Уведомления" component={NotificationsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

// ============================================================================
// СТИЛИ
// ============================================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1e1e1e',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1e1e1e',
  },
  loadingText: {
    color: '#888',
    marginTop: 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#2d2d2d',
    borderBottomWidth: 1,
    borderBottomColor: '#404040',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
  },
  timestamp: {
    color: '#888',
    fontSize: 12,
  },
  card: {
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 15,
    borderRadius: 10,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
    marginLeft: 10,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  online: {
    backgroundColor: '#2ecc71',
  },
  offline: {
    backgroundColor: '#e74c3c',
  },
  statusText: {
    color: '#fff',
    fontSize: 14,
  },
  modelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#404040',
  },
  modelText: {
    color: '#fff',
    marginLeft: 10,
    flex: 1,
  },
  modelSize: {
    color: '#888',
    fontSize: 12,
  },
  configRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#404040',
  },
  configName: {
    color: '#fff',
    marginLeft: 10,
    flex: 1,
  },
  configSize: {
    color: '#888',
    fontSize: 12,
  },
  chart: {
    marginVertical: 10,
    borderRadius: 10,
  },
  addButton: {
    backgroundColor: '#007acc',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  configCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 15,
    borderRadius: 10,
  },
  configInfo: {
    flex: 1,
    marginLeft: 15,
  },
  configTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  configType: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  configDate: {
    color: '#888',
    fontSize: 12,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyText: {
    color: '#888',
    fontSize: 16,
    marginTop: 10,
    marginBottom: 20,
  },
  createButton: {
    backgroundColor: '#007acc',
    paddingHorizontal: 30,
    paddingVertical: 10,
    borderRadius: 5,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
  },
  notificationCard: {
    flexDirection: 'row',
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  errorCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#e74c3c',
  },
  warningCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#f1c40f',
  },
  notificationContent: {
    flex: 1,
    marginLeft: 15,
  },
  notificationText: {
    color: '#fff',
    fontSize: 14,
  },
  notificationTime: {
    color: '#888',
    fontSize: 11,
    marginTop: 2,
  },
});
