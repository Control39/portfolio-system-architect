/**
 * Главный файл экспорта пользовательских инструментов
 * Все инструменты автоматически загружаются CodeAssistant
 */

// Экспорт инструментов из system-analysis
export { projectScannerTool } from './system-analysis/project-scanner';

// Экспорт инструментов из cognitive
export { ragOptimizerTool } from './cognitive/rag-optimizer';

// Экспорт инструментов из productivity
export { workspaceOptimizerTool } from './productivity/workspace-optimizer';

// Экспорт инструментов из security
export { securityAuditorTool } from './security/security-auditor';

// Экспорт инструментов из monitoring
export { metricsAnalyzerTool } from './monitoring/metrics-analyzer';

// Дополнительные экспорты будут добавлены по мере создания инструментов

/**
 * Список всех доступных инструментов
 */
export const allTools = {
  project_scanner: 'Анализ технологического стека проекта',
  rag_optimizer: 'Оптимизация RAG систем',
  workspace_optimizer: 'Оптимизация рабочего пространства',
  security_auditor: 'Аудит безопасности кода',
  metrics_analyzer: 'Анализ метрик и мониторинг'
};

/**
 * Получить информацию о всех инструментах
 */
export function getToolsInfo() {
  return {
    count: Object.keys(allTools).length,
    categories: ['system-analysis', 'cognitive', 'productivity', 'security', 'monitoring'],
    tools: allTools,
    lastUpdated: new Date().toISOString()
  };
}

/**
 * Пример использования:
 *
 * import { projectScannerTool, securityAuditorTool } from 'codeassistant/tools';
 *
 * // Вызов инструмента анализа проекта
 * const projectResult = await projectScannerTool.execute({
 *   path: './my-project',
 *   depth: 2
 * });
 *
 * // Вызов инструмента аудита безопасности
 * const securityResult = await securityAuditorTool.execute({
 *   code: 'def test(): exec("print(1)")',
 *   language: 'python'
 * });
 */
