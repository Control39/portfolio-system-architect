import { Tool } from '../index';

/**
 * Инструмент аудита безопасности
 * Анализирует код на наличие уязвимостей и небезопасных практик
 */
export const securityAuditorTool: Tool = {
  name: "security_auditor",
  description: "Анализирует код на наличие уязвимостей безопасности и небезопасных практик",
  execute: async (args: any) => {
    const { code, language = 'python', checkLevel = 'standard' } = args;
    
    if (!code) {
      return {
        success: false,
        error: "Не предоставлен код для анализа"
      };
    }
    
    // Правила безопасности для разных языков
    const securityRules = {
      python: [
        {
          pattern: /exec\(|eval\(|compile\(/g,
          severity: 'high',
          description: 'Использование exec/eval/compile может привести к выполнению произвольного кода',
          recommendation: 'Используйте безопасные альтернативы или строго валидируйте входные данные'
        },
        {
          pattern: /subprocess\.run\(.*shell\s*=\s*True/g,
          severity: 'high',
          description: 'Использование shell=True в subprocess может привести к инъекциям команд',
          recommendation: 'Используйте shell=False и передавайте аргументы как список'
        },
        {
          pattern: /pickle\.loads\(|pickle\.load\(/g,
          severity: 'high',
          description: 'Десериализация pickle может привести к выполнению произвольного кода',
          recommendation: 'Используйте безопасные форматы сериализации (JSON, msgpack)'
        },
        {
          pattern: /password\s*=\s*['"][^'"]*['"]/gi,
          severity: 'medium',
          description: 'Жестко закодированные пароли в коде',
          recommendation: 'Используйте переменные окружения или секреты'
        },
        {
          pattern: /sql\s*=\s*f"SELECT.*{\w+}/g,
          severity: 'high',
          description: 'Потенциальная SQL инъекция через f-строки',
          recommendation: 'Используйте параметризованные запросы или ORM'
        }
      ],
      javascript: [
        {
          pattern: /eval\(|Function\(/g,
          severity: 'high',
          description: 'Использование eval или Function конструктора',
          recommendation: 'Избегайте динамического выполнения кода'
        },
        {
          pattern: /innerHTML\s*=/g,
          severity: 'medium',
          description: 'Прямое присваивание innerHTML может привести к XSS',
          recommendation: 'Используйте textContent или безопасные методы DOM'
        },
        {
          pattern: /localStorage\.setItem\(.*password/gi,
          severity: 'high',
          description: 'Хранение паролей в localStorage небезопасно',
          recommendation: 'Используйте безопасное хранилище (HttpOnly cookies)'
        }
      ],
      typescript: [
        {
          pattern: /any\s*:\s*any/g,
          severity: 'low',
          description: 'Использование типа any снижает безопасность типов',
          recommendation: 'Используйте конкретные типы или unknown'
        }
      ]
    };
    
    // Получаем правила для указанного языка
    const rules = securityRules[language as keyof typeof securityRules] || securityRules.python;
    
    // Анализируем код
    const vulnerabilities = [];
    let lineNumber = 1;
    
    const lines = code.split('\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      for (const rule of rules) {
        const matches = line.match(rule.pattern);
        if (matches) {
          vulnerabilities.push({
            line: lineNumber,
            code: line.trim(),
            severity: rule.severity,
            description: rule.description,
            recommendation: rule.recommendation,
            matches: matches.length
          });
        }
      }
      
      lineNumber++;
    }
    
    // Группируем уязвимости по уровню серьезности
    const highVulns = vulnerabilities.filter(v => v.severity === 'high');
    const mediumVulns = vulnerabilities.filter(v => v.severity === 'medium');
    const lowVulns = vulnerabilities.filter(v => v.severity === 'low');
    
    // Рассчитываем оценку безопасности
    const totalScore = 100;
    const highPenalty = highVulns.length * 20;
    const mediumPenalty = mediumVulns.length * 10;
    const lowPenalty = lowVulns.length * 5;
    
    const securityScore = Math.max(0, totalScore - highPenalty - mediumPenalty - lowPenalty);
    
    // Определяем уровень безопасности
    let securityLevel = 'excellent';
    if (securityScore < 60) securityLevel = 'critical';
    else if (securityScore < 70) securityLevel = 'poor';
    else if (securityScore < 80) securityLevel = 'fair';
    else if (securityScore < 90) securityLevel = 'good';
    
    // Генерируем рекомендации
    const recommendations = [];
    
    if (highVulns.length > 0) {
      recommendations.push({
        priority: 'high',
        action: 'Немедленно исправьте высокоуровневые уязвимости',
        details: `Найдено ${highVulns.length} критических уязвимостей`
      });
    }
    
    if (mediumVulns.length > 0) {
      recommendations.push({
        priority: 'medium',
        action: 'Исправьте среднеуровневые уязвимости в ближайшее время',
        details: `Найдено ${mediumVulns.length} уязвимостей средней серьезности`
      });
    }
    
    if (lowVulns.length > 0) {
      recommendations.push({
        priority: 'low',
        action: 'Рассмотрите исправление низкоуровневых уязвимостей',
        details: `Найдено ${lowVulns.length} незначительных уязвимостей`
      });
    }
    
    // Добавляем общие рекомендации
    if (vulnerabilities.length === 0) {
      recommendations.push({
        priority: 'info',
        action: 'Код выглядит безопасным',
        details: 'Продолжайте следовать best practices безопасности'
      });
    } else {
      recommendations.push({
        priority: 'info',
        action: 'Регулярно проводите аудит безопасности',
        details: 'Используйте статические анализаторы кода (Bandit, ESLint, SonarQube)'
      });
    }
    
    return {
      success: true,
      data: {
        analysis: {
          language,
          linesAnalyzed: lines.length,
          vulnerabilitiesFound: vulnerabilities.length,
          securityScore,
          securityLevel
        },
        vulnerabilities: {
          high: highVulns,
          medium: mediumVulns,
          low: lowVulns
        },
        recommendations,
        summary: {
          message: `Найдено ${vulnerabilities.length} уязвимостей безопасности`,
          riskLevel: securityLevel,
          immediateActions: highVulns.length > 0 ? 'Требуется немедленное исправление' : 'Нет критических уязвимостей'
        }
      }
    };
  }
};