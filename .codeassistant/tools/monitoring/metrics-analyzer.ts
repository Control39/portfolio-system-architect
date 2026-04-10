import { Tool } from '../index';

/**
 * Инструмент анализа метрик и мониторинга
 * Анализирует метрики производительности, доступности и использования ресурсов
 */
export const metricsAnalyzerTool: Tool = {
  name: "metrics_analyzer",
  description: "Анализирует метрики производительности, доступности и использования ресурсов системы",
  execute: async (args: any) => {
    const { 
      metrics = {}, 
      timeRange = '24h',
      thresholds = {
        cpu: 80,
        memory: 85,
        disk: 90,
        latency: 1000,
        errorRate: 5,
        availability: 99.5
      }
    } = args;
    
    // Примерные метрики, если не предоставлены
    const defaultMetrics = {
      cpu: {
        current: 45,
        avg: 42,
        max: 78,
        min: 25,
        trend: 'stable'
      },
      memory: {
        current: 65,
        avg: 62,
        max: 82,
        min: 45,
        trend: 'increasing'
      },
      disk: {
        usage: 72,
        iops: 1500,
        throughput: 120,
        trend: 'stable'
      },
      network: {
        inbound: 45,
        outbound: 32,
        connections: 1250,
        trend: 'stable'
      },
      application: {
        latency: {
          p50: 120,
          p95: 450,
          p99: 1200,
          avg: 180
        },
        throughput: 850,
        errorRate: 2.3,
        availability: 99.8
      },
      business: {
        activeUsers: 12500,
        requestsPerSecond: 850,
        conversionRate: 3.2,
        revenue: 125000
      }
    };
    
    const actualMetrics = Object.keys(metrics).length > 0 ? metrics : defaultMetrics;
    
    // Анализ метрик
    const analysis = {
      performance: analyzePerformance(actualMetrics, thresholds),
      availability: analyzeAvailability(actualMetrics, thresholds),
      resources: analyzeResources(actualMetrics, thresholds),
      anomalies: detectAnomalies(actualMetrics),
      trends: analyzeTrends(actualMetrics)
    };
    
    // Генерация рекомендаций
    const recommendations = generateRecommendations(analysis, thresholds);
    
    // Расчет общего здоровья системы
    const systemHealth = calculateSystemHealth(analysis);
    
    return {
      success: true,
      data: {
        metadata: {
          timeRange,
          timestamp: new Date().toISOString(),
          metricsSource: Object.keys(metrics).length > 0 ? 'provided' : 'default'
        },
        metrics: actualMetrics,
        analysis,
        recommendations,
        health: {
          score: systemHealth.score,
          level: systemHealth.level,
          components: systemHealth.components
        },
        alerts: generateAlerts(analysis, thresholds),
        dashboard: generateDashboardData(actualMetrics, analysis)
      }
    };
  }
};

// Вспомогательные функции
function analyzePerformance(metrics: any, thresholds: any) {
  const app = metrics.application;
  const perf = {
    latency: {
      status: app.latency.p95 <= thresholds.latency ? 'good' : 'poor',
      value: app.latency.p95,
      threshold: thresholds.latency,
      description: app.latency.p95 <= thresholds.latency 
        ? 'Латентность в пределах нормы' 
        : 'Высокая латентность, требуется оптимизация'
    },
    throughput: {
      status: 'good', // Без порога
      value: app.throughput,
      description: 'Пропускная способность приемлемая'
    },
    errorRate: {
      status: app.errorRate <= thresholds.errorRate ? 'good' : 'poor',
      value: app.errorRate,
      threshold: thresholds.errorRate,
      description: app.errorRate <= thresholds.errorRate
        ? 'Уровень ошибок в пределах нормы'
        : 'Высокий уровень ошибок, требуется исследование'
    }
  };
  
  return perf;
}

function analyzeAvailability(metrics: any, thresholds: any) {
  const app = metrics.application;
  const avail = {
    availability: {
      status: app.availability >= thresholds.availability ? 'good' : 'poor',
      value: app.availability,
      threshold: thresholds.availability,
      description: app.availability >= thresholds.availability
        ? 'Доступность соответствует SLA'
        : 'Доступность ниже требуемого уровня'
    },
    uptime: {
      status: 'good',
      value: '99.95%',
      description: 'Время безотказной работы хорошее'
    }
  };
  
  return avail;
}

function analyzeResources(metrics: any, thresholds: any) {
  const resources = {
    cpu: {
      status: metrics.cpu.current <= thresholds.cpu ? 'good' : 'warning',
      value: metrics.cpu.current,
      threshold: thresholds.cpu,
      description: metrics.cpu.current <= thresholds.cpu
        ? 'Использование CPU в норме'
        : 'Высокое использование CPU'
    },
    memory: {
      status: metrics.memory.current <= thresholds.memory ? 'good' : 'warning',
      value: metrics.memory.current,
      threshold: thresholds.memory,
      description: metrics.memory.current <= thresholds.memory
        ? 'Использование памяти в норме'
        : 'Высокое использование памяти'
    },
    disk: {
      status: metrics.disk.usage <= thresholds.disk ? 'good' : 'warning',
      value: metrics.disk.usage,
      threshold: thresholds.disk,
      description: metrics.disk.usage <= thresholds.disk
        ? 'Использование диска в норме'
        : 'Высокое использование диска'
    }
  };
  
  return resources;
}

function detectAnomalies(metrics: any) {
  const anomalies = [];
  
  // Проверка на аномалии в CPU
  if (metrics.cpu.current > 90) {
    anomalies.push({
      type: 'cpu_spike',
      severity: 'high',
      description: 'Резкий рост использования CPU',
      metric: 'cpu',
      value: metrics.cpu.current,
      recommendation: 'Проверьте процессы с высоким использованием CPU'
    });
  }
  
  // Проверка на аномалии в памяти
  if (metrics.memory.trend === 'increasing' && metrics.memory.current > 80) {
    anomalies.push({
      type: 'memory_leak',
      severity: 'medium',
      description: 'Возможная утечка памяти',
      metric: 'memory',
      value: metrics.memory.current,
      recommendation: 'Проверьте приложение на утечки памяти'
    });
  }
  
  // Проверка на аномалии в латентности
  if (metrics.application.latency.p99 > 2000) {
    anomalies.push({
      type: 'high_latency',
      severity: 'high',
      description: 'Очень высокая латентность (p99 > 2s)',
      metric: 'latency',
      value: metrics.application.latency.p99,
      recommendation: 'Оптимизируйте медленные запросы'
    });
  }
  
  return anomalies;
}

function analyzeTrends(metrics: any) {
  const trends = [];
  
  if (metrics.cpu.trend === 'increasing') {
    trends.push({
      metric: 'cpu',
      trend: 'increasing',
      description: 'Использование CPU растет',
      implication: 'Может потребоваться масштабирование'
    });
  }
  
  if (metrics.memory.trend === 'increasing') {
    trends.push({
      metric: 'memory',
      trend: 'increasing',
      description: 'Использование памяти растет',
      implication: 'Возможна утечка памяти'
    });
  }
  
  if (metrics.application.errorRate > 5) {
    trends.push({
      metric: 'error_rate',
      trend: 'high',
      description: 'Высокий уровень ошибок',
      implication: 'Требуется отладка приложения'
    });
  }
  
  return trends;
}

function generateRecommendations(analysis: any, thresholds: any) {
  const recommendations = [];
  
  // Рекомендации по производительности
  if (analysis.performance.latency.status === 'poor') {
    recommendations.push({
      category: 'performance',
      priority: 'high',
      action: 'Оптимизировать латентность приложения',
      details: `p95 латентность ${analysis.performance.latency.value}ms превышает порог ${thresholds.latency}ms`,
      steps: [
        'Проанализировать медленные эндпоинты',
        'Оптимизировать запросы к базе данных',
        'Рассмотреть кэширование'
      ]
    });
  }
  
  if (analysis.performance.errorRate.status === 'poor') {
    recommendations.push({
      category: 'reliability',
      priority: 'high',
      action: 'Снизить уровень ошибок',
      details: `Уровень ошибок ${analysis.performance.errorRate.value}% превышает порог ${thresholds.errorRate}%`,
      steps: [
        'Проанализировать логи ошибок',
        'Улучшить обработку исключений',
        'Добавить retry логику'
      ]
    });
  }
  
  // Рекомендации по ресурсам
  if (analysis.resources.cpu.status === 'warning') {
    recommendations.push({
      category: 'resources',
      priority: 'medium',
      action: 'Масштабировать CPU',
      details: `Использование CPU ${analysis.resources.cpu.value}% близко к порогу ${thresholds.cpu}%`,
      steps: [
        'Добавить больше реплик приложения',
        'Оптимизировать CPU-intensive операции',
        'Рассмотреть вертикальное масштабирование'
      ]
    });
  }
  
  if (analysis.resources.memory.status === 'warning') {
    recommendations.push({
      category: 'resources',
      priority: 'medium',
      action: 'Увеличить память',
      details: `Использование памяти ${analysis.resources.memory.value}% близко к порогу ${thresholds.memory}%`,
      steps: [
        'Увеличить лимиты памяти',
        'Оптимизировать использование памяти',
        'Добавить мониторинг утечек памяти'
      ]
    });
  }
  
  // Общие рекомендации
  if (recommendations.length === 0) {
    recommendations.push({
      category: 'general',
      priority: 'low',
      action: 'Продолжать мониторинг',
      details: 'Система работает стабильно',
      steps: [
        'Продолжать регулярный мониторинг',
        'Планировать capacity planning',
        'Обновлять пороги мониторинга'
      ]
    });
  }
  
  return recommendations;
}

function calculateSystemHealth(analysis: any) {
  let score = 100;
  const components = [];
  
  // Вычитаем баллы за проблемы
  if (analysis.performance.latency.status === 'poor') score -= 20;
  if (analysis.performance.errorRate.status === 'poor') score -= 25;
  if (analysis.availability.availability.status === 'poor') score -= 30;
  if (analysis.resources.cpu.status === 'warning') score -= 10;
  if (analysis.resources.memory.status === 'warning') score -= 10;
  if (analysis.resources.disk.status === 'warning') score -= 10;
  
  // Добавляем аномалии
  if (analysis.anomalies.length > 0) {
    score -= analysis.anomalies.length * 5;
  }
  
  // Ограничиваем score
  score = Math.max(0, Math.min(100, score));
  
  // Определяем уровень здоровья
  let level = 'healthy';
  if (score < 60) level = 'critical';
  else if (score < 70) level = 'unhealthy';
  else if (score < 80) level = 'degraded';
  else if (score < 90) level = 'stable';
  
  // Компоненты здоровья
  components.push({
    name: 'performance',
    status: analysis.performance.latency.status === 'poor' || analysis.performance.errorRate.status === 'poor' ? 'poor' : 'good',
    score: analysis.performance.latency.status === 'poor' ? 60 : 100
  });
  
  components.push({
    name: 'availability',
    status: analysis.availability.availability.status,
    score: analysis.availability.availability.status === 'poor' ? 70 : 100
  });
  
  components.push({
    name: 'resources',
    status: analysis.resources.cpu.status === 'warning' || analysis.resources.memory.status === 'warning' ? 'warning' : 'good',
    score: 85
  });
  
  return { score, level, components };
}

function generateAlerts(analysis: any, thresholds: any) {
  const alerts = [];
  
  if (analysis.performance.latency.status === 'poor') {
    alerts.push({
      type: 'performance',
      severity: 'high',
      title: 'Высокая латентность',
      description: `p95 латентность ${analysis.performance.latency.value}ms превышает порог ${thresholds.latency}ms`,
      timestamp: new Date().toISOString()
    });
  }
  
  if (analysis.availability.availability.status === 'poor') {
    alerts.push({
      type: 'availability',
      severity: 'critical',
      title: 'Низкая доступность',
      description: `Доступность ${analysis.availability.availability.value}% ниже порога ${thresholds.availability}%`,
      timestamp: new Date().toISOString()
    });
  }
  
  if (analysis.anomalies.length > 0) {
    analysis.anomalies.forEach((anomaly: any) => {
      alerts.push({
        type: 'anomaly',
        severity: anomaly.severity,
        title: `Аномалия: ${anomaly.type}`,
        description: anomaly.description,
        timestamp: new Date().toISOString()
      });
    });
  }
  
  return alerts;
}

function generateDashboardData(metrics: any, analysis: any) {
  return {
    summary: {
      health: analysis.health,
      performance: analysis.performance,
      availability: analysis.availability
    },
    charts: {
      cpu: {
        data: [metrics.cpu.min, metrics.cpu.avg, metrics.cpu.current, metrics.cpu.max],
        labels: ['Min', 'Avg', 'Current', 'Max']
      },
      memory: {
        data: [metrics.memory.min, metrics.memory.avg, metrics.memory.current, metrics.memory.max],
        labels: ['Min', 'Avg', 'Current', 'Max']
      },
      latency: {
        data: [metrics.application.latency.p50, metrics.application.latency.p95, metrics.application.latency.p99],
        labels: ['p50', 'p95', 'p99']
      }
    },
    kpis: [
      {
        name: 'Availability',
        value: `${metrics.application.availability}%`,
        target: '99.5%',
        status: analysis.availability.availability.status
      },
      {
        name: 'Error Rate',
        value: `${metrics.application.errorRate}%`,
        target: '< 5%',
        status: analysis.performance.errorRate.status
      },
      {
        name: 'Active Users',
        value: metrics.business.activeUsers.toLocaleString(),
        target: 'Growing',
        status: 'good'
      }
    ]
  };
}