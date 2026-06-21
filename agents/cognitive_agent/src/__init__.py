"""
Инициализация модуля src для Cognitive Agent
"""

from .base_agent import (
    BaseCognitiveAgent,
    AGENT_DATA_DIR,
    AGENT_LOGS_DIR,
    AGENT_REPORTS_DIR,
    AGENT_SCANS_DIR,
    AGENT_CONFIG_DIR,
    AGENT_DATA_STORAGE_DIR,
    AGENT_STATUS_DIR,
    AGENT_PLANS_DIR,
    AGENT_METRICS_DIR,
    AGENT_CACHE_DIR,
)
from .task_planner import TaskPlanner, EnhancedTaskPlanner, TaskStatus
from .logging_config import setup_logging
from .service_registry import ServiceRegistry, ServiceProfile, ServiceDiscovery
from .test_generator import TestGenerator
from .code_analyzer import CodeAnalyzer, AnalysisTool, AnalysisResult
from .documentation_analyzer import DocumentationAnalyzer
from .test_analyzer import TestAnalyzer

__all__ = [
    'BaseCognitiveAgent',
    # Agent data directories
    'AGENT_DATA_DIR',
    'AGENT_LOGS_DIR',
    'AGENT_REPORTS_DIR',
    'AGENT_SCANS_DIR',
    'AGENT_CONFIG_DIR',
    'AGENT_DATA_STORAGE_DIR',
    'AGENT_STATUS_DIR',
    'AGENT_PLANS_DIR',
    'AGENT_METRICS_DIR',
    'AGENT_CACHE_DIR',
    'TaskPlanner',
    'EnhancedTaskPlanner',
    'TaskStatus',
    'setup_logging',
    'ServiceRegistry',
    'ServiceProfile',
    'ServiceDiscovery',
    'TestGenerator',
    'CodeAnalyzer',
    'AnalysisTool',
    'AnalysisResult',
    'DocumentationAnalyzer',
    'TestAnalyzer'
]
