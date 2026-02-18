// Мобильное приложение для системы управления карьерным развитием
// Использует React Native

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Button, TextInput, Alert } from 'react-native';

const App = () => {
  const [users, setUsers] = useState([]);
  const [markers, setMarkers] = useState([]);
  const [skills, setSkills] = useState({});
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '' });
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Базовый URL API
  const API_BASE_URL = 'http://localhost:5000/api';
  
  // Загрузка пользователей
  const loadUsers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/users`);
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error);
      Alert.alert('Ошибка', 'Не удалось загрузить пользователей');
    }
  };

  // Создание нового пользователя
  const createUser = async () => {
    if (!newUser.username || !newUser.email || !newUser.password) {
      Alert.alert('Ошибка', 'Пожалуйста, заполните все поля');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: newUser.username,
          email: newUser.email,
          password: newUser.password
        })
      });
      
      if (response.ok) {
        const createdUser = await response.json();
        setUsers([...users, createdUser]);
        setNewUser({ username: '', email: '', password: '' });
        Alert.alert('Успех', 'Пользователь успешно создан');
      } else {
        const errorData = await response.json();
        Alert.alert('Ошибка', errorData.error || 'Не удалось создать пользователя');
      }
    } catch (error) {
      console.error('Ошибка создания пользователя:', error);
      Alert.alert('Ошибка', 'Произошла ошибка при создании пользователя');
    }
  };

  // Загрузка маркеров компетенций
  const loadMarkers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/markers`);
      const data = await response.json();
      setMarkers(data);
    } catch (error) {
      console.error('Ошибка загрузки маркеров:', error);
      Alert.alert('Ошибка', 'Не удалось загрузить маркеры компетенций');
    }
  };

  // Функция входа
  const handleLogin = async () => {
    if (!loginData.username || !loginData.password) {
      Alert.alert('Ошибка', 'Пожалуйста, заполните все поля');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: loginData.username,
          password: loginData.password
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setIsLoggedIn(true);
        setCurrentUser(data.user);
        Alert.alert('Успех', 'Вы успешно вошли в систему');
      } else {
        const errorData = await response.json();
        Alert.alert('Ошибка', errorData.error || 'Не удалось выполнить вход');
      }
    } catch (error) {
      console.error('Ошибка входа:', error);
      Alert.alert('Ошибка', 'Произошла ошибка при входе в систему');
    }
  };
  
  // Функция выхода
  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST'
      });
      setIsLoggedIn(false);
      setCurrentUser(null);
      setSkills({});
      Alert.alert('Успех', 'Вы успешно вышли из системы');
    } catch (error) {
      console.error('Ошибка выхода:', error);
      Alert.alert('Ошибка', 'Произошла ошибка при выходе из системы');
    }
  };
  
  // Загрузка навыков пользователя
  const loadUserSkills = async (userId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/${userId}/skills`);
      const data = await response.json();
      setSkills(prev => ({ ...prev, [userId]: data }));
    } catch (error) {
      console.error('Ошибка загрузки навыков:', error);
      Alert.alert('Ошибка', 'Не удалось загрузить навыки пользователя');
    }
  };
  
  // Показ навыков пользователя
  const showUserSkills = (userId) => {
    // Если навыки еще не загружены, загружаем их
    if (!skills[userId]) {
      loadUserSkills(userId);
    }
    
    // Здесь можно открыть отдельный экран с навыками пользователя
    Alert.alert('Навыки', 'Здесь будут отображаться навыки пользователя');
  };
  
  // Загрузка данных при запуске приложения
  useEffect(() => {
    loadMarkers();
    // Проверяем статус аутентификации
    checkAuthStatus();
  }, []);
  
  // Проверка статуса аутентификации
  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/status`);
      const data = await response.json();
      if (data.authenticated) {
        setIsLoggedIn(true);
        setCurrentUser(data.user);
      }
    } catch (error) {
      console.error('Ошибка проверки статуса аутентификации:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {!isLoggedIn ? (
        // Экран входа
        <View style={styles.section}>
          <Text style={styles.title}>Вход в систему</Text>
          
          <View style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Имя пользователя"
              value={loginData.username}
              onChangeText={text => setLoginData({...loginData, username: text})}
            />
            <TextInput
              style={styles.input}
              placeholder="Пароль"
              secureTextEntry
              value={loginData.password}
              onChangeText={text => setLoginData({...loginData, password: text})}
            />
            <Button title="Войти" onPress={handleLogin} />
          </View>
          
          {/* Форма регистрации */}
          <Text style={styles.sectionTitle}>Регистрация нового пользователя</Text>
          <View style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Имя пользователя"
              value={newUser.username}
              onChangeText={text => setNewUser({...newUser, username: text})}
            />
            <TextInput
              style={styles.input}
              placeholder="Email"
              value={newUser.email}
              onChangeText={text => setNewUser({...newUser, email: text})}
            />
            <TextInput
              style={styles.input}
              placeholder="Пароль"
              secureTextEntry
              value={newUser.password}
              onChangeText={text => setNewUser({...newUser, password: text})}
            />
            <Button title="Зарегистрироваться" onPress={createUser} />
          </View>
        </View>
      ) : (
        // Основной интерфейс после входа
        <View>
          <Text style={styles.title}>Система управления карьерным развитием</Text>
          <Text style={styles.subtitle}>Добро пожаловать, {currentUser?.username}!</Text>
          <Button title="Выйти" onPress={handleLogout} />
          
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Пользователи</Text>
            {users.map(user => (
              <View key={user.id} style={styles.card}>
                <Text style={styles.cardTitle}>{user.username}</Text>
                <Text>{user.email}</Text>
                <Button title="Показать навыки" onPress={() => showUserSkills(user.id)} />
              </View>
            ))}
          </View>
          
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Маркеры компетенций</Text>
            {markers.map(marker => (
              <View key={marker.id} style={styles.card}>
                <Text style={styles.cardTitle}>{marker.title}</Text>
                <Text>{marker.description || 'Описание отсутствует'}</Text>
                <Text>Требуемый уровень: {marker.required_level}</Text>
              </View>
            ))}
          </View>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginVertical: 20,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#666',
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  card: {
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  form: {
    marginTop: 15,
  },
  input: {
    height: 40,
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 4,
    paddingHorizontal: 10,
    marginBottom: 10,
    backgroundColor: 'white',
  },
});

export default App;