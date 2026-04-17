// Данные для демонстрации
const projectData = [
    {
        id: 1,
        name: "E-commerce Platform",
        description: "Платформа для онлайн-торговли с полным набором функций",
        status: "in-progress",
        progress: 75,
        deadline: "2026-03-15"
    },
    {
        id: 2,
        name: "Mobile Banking App",
        description: "Мобильное приложение для банковских операций",
        status: "pending",
        progress: 0,
        deadline: "2026-04-30"
    },
    {
        id: 3,
        name: "Data Analytics Dashboard",
        description: "Панель для визуализации и анализа бизнес-данных",
        status: "completed",
        progress: 100,
        deadline: "2026-01-20"
    },
    {
        id: 4,
        name: "AI Chatbot",
        description: "Интеллектуальный чат-бот для поддержки клиентов",
        status: "in-progress",
        progress: 40,
        deadline: "2026-05-10"
    }
];

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    updateDashboard();
    renderProjectList();
    initCharts();
});

// Обновление дашборда
function updateDashboard() {
    // Общее количество проектов
    document.getElementById('total-projects').textContent = projectData.length;

    // Проекты в работе
    const inProgressCount = projectData.filter(project => project.status === 'in-progress').length;
    document.getElementById('in-progress').textContent = inProgressCount;

    // Завершенные проекты
    const completedCount = projectData.filter(project => project.status === 'completed').length;
    document.getElementById('completed').textContent = completedCount;

    // Ближайшие дедлайны (в течение 30 дней)
    const upcomingDeadlines = projectData.filter(project => {
        const deadline = new Date(project.deadline);
        const now = new Date();
        const diffTime = deadline - now;
        const diffDays = diffTime / (1000 * 60 * 60 * 24);
        return diffDays > 0 && diffDays <= 30;
    }).length;
    document.getElementById('upcoming-deadlines').textContent = upcomingDeadlines;
}

// Отображение списка проектов
function renderProjectList() {
    const projectList = document.getElementById('project-list');
    projectList.innerHTML = '';

    projectData.forEach(project => {
        const projectElement = document.createElement('div');
        projectElement.className = 'project-item';
        projectElement.innerHTML = `
            <h3>${project.name}</h3>
            <p>${project.description}</p>
            <p><strong>Прогресс:</strong> ${project.progress}%</p>
            <p><strong>Дедлайн:</strong> ${project.deadline}</p>
            <span class="status ${project.status}">${getStatusText(project.status)}</span>
        `;
        projectList.appendChild(projectElement);
    });
}

// Получение текстового представления статуса
function getStatusText(status) {
    switch(status) {
        case 'completed':
            return 'Завершен';
        case 'in-progress':
            return 'В работе';
        case 'pending':
            return 'Ожидает';
        default:
            return status;
    }
}

// Инициализация графиков
function initCharts() {
    // Для демонстрации создаем простой график с использованием Canvas
    const canvas = document.getElementById('projects-chart');
    const ctx = canvas.getContext('2d');

    // Устанавливаем размеры canvas
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Очищаем canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Рисуем простую диаграмму
    const statuses = ['completed', 'in-progress', 'pending'];
    const counts = [
        projectData.filter(p => p.status === 'completed').length,
        projectData.filter(p => p.status === 'in-progress').length,
        projectData.filter(p => p.status === 'pending').length
    ];

    const barWidth = 50;
    const spacing = 20;
    const maxCount = Math.max(...counts);

    statuses.forEach((status, index) => {
        const barHeight = (counts[index] / maxCount) * (canvas.height - 50);
        const x = index * (barWidth + spacing) + 50;
        const y = canvas.height - barHeight - 20;

        // Рисуем столбец
        ctx.fillStyle = getStatusColor(status);
        ctx.fillRect(x, y, barWidth, barHeight);

        // Подпись
        ctx.fillStyle = '#000';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(status, x + barWidth/2, canvas.height - 5);
        ctx.fillText(counts[index].toString(), x + barWidth/2, y - 5);
    });
}

// Получение цвета для статуса
function getStatusColor(status) {
    switch(status) {
        case 'completed':
            return '#2ecc71';
        case 'in-progress':
            return '#f39c12';
        case 'pending':
            return '#95a5a6';
        default:
            return '#3498db';
    }
}

// Обработчики событий для навигации
document.querySelectorAll('nav a').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();

        const targetId = this.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
