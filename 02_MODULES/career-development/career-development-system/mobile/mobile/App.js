// Мобильное приложение для системы управления карьерным развитием
// Использует React Native
// Улучшения: токены авторизации, индикаторы загрузки, навигация, интернационализация

import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useEffect, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    Button,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View
} from 'react-native';

const Stack = createNativeStackNavigator();

// Интернационализация
const translations = {
    ru: {
        login: 'Вход',
        logout: 'Выйти',
        register: 'Регистрация',
        username: 'Имя пользователя',
        password: 'Пароль',
        email: 'Email',
        skills: 'Навыки',
        markers: 'Маркеры компетенций',
        users: 'Пользователи',
        welcome: 'Добро пожаловать',
        error: 'Ошибка',
        success: 'Успех',
        loading: 'Загрузка...',
        fillAllFields: 'Пожалуйста, заполните все поля',
        loginSuccess: 'Вы успешно вошли в систему',
        loginError: 'Не удалось выполнить вход',
        registerSuccess: 'Пользователь успешно создан',
        registerError: 'Не удалось создать пользователя',
        logoutSuccess: 'Вы успешно вышли из системы',
        showSkills: 'Показать навыки'
    },
    en: {
        login: 'Login',
        logout: 'Logout',
        register: 'Register',
        username: 'Username',
        password: 'Password',
        email: 'Email',
        skills: 'Skills',
        markers: 'Competency Markers',
        users: 'Users',
        welcome: 'Welcome',
        error: 'Error',
        success: 'Success',
        loading: 'Loading...',
        fillAllFields: 'Please fill all fields',
        loginSuccess: 'Successfully logged in',
        loginError: 'Login failed',
        registerSuccess: 'User created successfully',
        registerError: 'Failed to create user',
        logoutSuccess: 'Successfully logged out',
        showSkills: 'Show skills'
    }
};

const App = () => {
    const [users, setUsers] = useState([]);
    const [markers, setMarkers] = useState([]);
    const [skills, setSkills] = useState({});
    const [newUser, setNewUser] = useState({ username: '', email: '', password: '' });
    const [loginData, setLoginData] = useState({ username: '', password: '' });
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [language, setLanguage] = useState('ru');

    const t = translations[language];

    // Базовый URL API
    const API_BASE_URL = 'http://localhost:5000/api';

    // Функция для получения заголовков с токеном авторизации
    const getAuthHeaders = () => ({
        'Content-Type': 'application/json',
        ...(currentUser?.token && { 'Authorization': `Bearer ${currentUser.token}` })
    });

    // Загрузка пользователей
    const loadUsers = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/users`, {
                headers: getAuthHeaders()
            });
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            console.error('Ошибка загрузки пользователей:', error);
            Alert.alert(t.error, 'Не удалось загрузить пользователей');
        } finally {
            setLoading(false);
        }
    };

    // Создание нового пользователя
    const createUser = async () => {
        if (!newUser.username || !newUser.email || !newUser.password) {
            Alert.alert(t.error, t.fillAllFields);
            return;
        }

        setLoading(true);
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
                Alert.alert(t.success, t.registerSuccess);
            } else {
                const errorData = await response.json();
                Alert.alert(t.error, errorData.error || t.registerError);
            }
        } catch (error) {
            console.error('Ошибка создания пользователя:', error);
            Alert.alert(t.error, t.registerError);
        } finally {
            setLoading(false);
        }
    };

    // Загрузка маркеров компетенций
    const loadMarkers = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/markers`, {
                headers: getAuthHeaders()
            });
            const data = await response.json();
            setMarkers(data);
        } catch (error) {
            console.error('Ошибка загрузки маркеров:', error);
            Alert.alert(t.error, 'Не удалось загрузить маркеры компетенций');
        } finally {
            setLoading(false);
        }
    };

    // Функция входа
    const handleLogin = async () => {
        if (!loginData.username || !loginData.password) {
            Alert.alert(t.error, t.fillAllFields);
            return;
        }

        setLoading(true);
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
                await loadUsers();
                await loadMarkers();
                Alert.alert(t.success, t.loginSuccess);
            } else {
                const errorData = await response.json();
                Alert.alert(t.error, errorData.error || t.loginError);
            }
        } catch (error) {
            console.error('Ошибка входа:', error);
            Alert.alert(t.error, t.loginError);
        } finally {
            setLoading(false);
        }
    };

    // Функция выхода
    const handleLogout = async () => {
        setLoading(true);
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            setIsLoggedIn(false);
            setCurrentUser(null);
            setSkills({});
            setUsers([]);
            Alert.alert(t.success, t.logoutSuccess);
        } catch (error) {
            console.error('Ошибка выхода:', error);
            Alert.alert(t.error, 'Произошла ошибка при выходе из системы');
        } finally {
            setLoading(false);
        }
    };

    // Загрузка навыков пользователя
    const loadUserSkills = async (userId) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}/skills`, {
                headers: getAuthHeaders()
            });
            const data = await response.json();
            setSkills(prev => ({ ...prev, [userId]: data }));
            // Показываем навыки в алерте (для простоты)
            Alert.alert(
                t.skills,
                JSON.stringify(data, null, 2).substring(0, 500)
            );
        } catch (error) {
            console.error('Ошибка загрузки навыков:', error);
            Alert.alert(t.error, 'Не удалось загрузить навыки пользователя');
        } finally {
            setLoading(false);
        }
    };

    // Проверка статуса аутентификации
    const checkAuthStatus = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/auth/status`, {
                headers: getAuthHeaders()
            });
            const data = await response.json();
            if (data.authenticated) {
                setIsLoggedIn(true);
                setCurrentUser(data.user);
                await loadUsers();
                await loadMarkers();
            }
        } catch (error) {
            console.error('Ошибка проверки статуса аутентификации:', error);
        } finally {
            setLoading(false);
        }
    };

    // Загрузка данных при запуске приложения
    useEffect(() => {
        checkAuthStatus();
    }, []);

    // Компонент экрана входа
    const LoginScreen = () => (
        <ScrollView style={styles.container}>
            <View style={styles.languageSwitcher}>
                <TouchableOpacity
                    style={[styles.langButton, language === 'ru' && styles.langButtonActive]}
                    onPress={() => setLanguage('ru')}
                >
                    <Text>Русский</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.langButton, language === 'en' && styles.langButtonActive]}
                    onPress={() => setLanguage('en')}
                >
                    <Text>English</Text>
                </TouchableOpacity>
            </View>

            <Text style={styles.title}>{t.login}</Text>

            {loading && <ActivityIndicator size="large" color="#0000ff" />}

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t.login}</Text>
                <View style={styles.form}>
                    <TextInput
                        style={styles.input}
                        placeholder={t.username}
                        value={loginData.username}
                        onChangeText={text => setLoginData({ ...loginData, username: text })}
                        editable={!loading}
                    />
                    <TextInput
                        style={styles.input}
                        placeholder={t.password}
                        secureTextEntry
                        value={loginData.password}
                        onChangeText={text => setLoginData({ ...loginData, password: text })}
                        editable={!loading}
                    />
                    <Button
                        title={t.login}
                        onPress={handleLogin}
                        disabled={loading}
                    />
                </View>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t.register}</Text>
                <View style={styles.form}>
                    <TextInput
                        style={styles.input}
                        placeholder={t.username}
                        value={newUser.username}
                        onChangeText={text => setNewUser({ ...newUser, username: text })}
                        editable={!loading}
                    />
                    <TextInput
                        style={styles.input}
                        placeholder={t.email}
                        value={newUser.email}
                        onChangeText={text => setNewUser({ ...newUser, email: text })}
                        editable={!loading}
                    />
                    <TextInput
                        style={styles.input}
                        placeholder={t.password}
                        secureTextEntry
                        value={newUser.password}
                        onChangeText={text => setNewUser({ ...newUser, password: text })}
                        editable={!loading}
                    />
                    <Button
                        title={t.register}
                        onPress={createUser}
                        disabled={loading}
                    />
                </View>
            </View>
        </ScrollView>
    );

    // Компонент главного экрана (после входа)
    const MainScreen = () => (
        <ScrollView style={styles.container}>
            <View style={styles.languageSwitcher}>
                <TouchableOpacity
                    style={[styles.langButton, language === 'ru' && styles.langButtonActive]}
                    onPress={() => setLanguage('ru')}
                >
                    <Text>Русский</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.langButton, language === 'en' && styles.langButtonActive]}
                    onPress={() => setLanguage('en')}
                >
                    <Text>English</Text>
                </TouchableOpacity>
            </View>

            <Text style={styles.title}>{t.welcome}, {currentUser?.username}!</Text>
            <Button title={t.logout} onPress={handleLogout} disabled={loading} />

            {loading && <ActivityIndicator size="large" color="#0000ff" />}

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t.users}</Text>
                {users.map(user => (
                    <View key={user.id} style={styles.card}>
                        <Text style={styles.cardTitle}>{user.username}</Text>
                        <Text>{user.email}</Text>
                        <Button
                            title={t.showSkills}
                            onPress={() => loadUserSkills(user.id)}
                            disabled={loading}
                        />
                    </View>
                ))}
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>{t.markers}</Text>
                {markers.map(marker => (
                    <View key={marker.id} style={styles.card}>
                        <Text style={styles.cardTitle}>{marker.title}</Text>
                        <Text>{marker.description || 'Описание отсутствует'}</Text>
                        <Text>Требуемый уровень: {marker.required_level}</Text>
                    </View>
                ))}
            </View>
        </ScrollView>
    );

    return (
        <SafeAreaView style={{ flex: 1 }}>
            <NavigationContainer>
                <Stack.Navigator screenOptions={{ headerShown: false }}>
                    {!isLoggedIn ? (
                        <Stack.Screen name="Login" component={LoginScreen} />
                    ) : (
                        <Stack.Screen name="Main" component={MainScreen} />
                    )}
                </Stack.Navigator>
            </NavigationContainer>
        </SafeAreaView>
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
    languageSwitcher: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
        marginBottom: 10,
    },
    langButton: {
        padding: 8,
        marginLeft: 10,
        borderRadius: 4,
        backgroundColor: '#ddd',
    },
    langButtonActive: {
        backgroundColor: '#007AFF',
    },
});

export default App;