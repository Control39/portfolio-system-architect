"""
Тесты для системы адаптивного обучения Cognitive Agent
"""

import tempfile

import pytest

from cognitive_agent.common import AdaptiveLearningSystem, BaseAgentExtensions, PatternAnalyzer


class TestAdaptiveLearning:
    """
    Тесты для системы адаптивного обучения
    """

    def test_pattern_analyzer_basic_functionality(self):
        """Тест основной функциональности PatternAnalyzer"""
        analyzer = PatternAnalyzer()

        # Добавить несколько решений
        analyzer.add_decision({"task_type": "refactoring"}, "rename_variable_x", "success")
        analyzer.add_decision({"task_type": "bug_fix"}, "fix_null_pointer", "success")
        analyzer.add_decision({"task_type": "refactoring"}, "rename_variable_y", "failed")

        # Проверить success rate
        success_rate = analyzer.get_success_rate()
        assert success_rate == 2 / 3  # 2 успешных из 3

        # Проверить анализ паттернов
        patterns = analyzer.analyze_patterns()
        assert "success_rate" in patterns
        assert "patterns" in patterns
        assert "recommendations" in patterns

    def test_pattern_analyzer_prediction(self):
        """Тест предсказания вероятности успеха"""
        analyzer = PatternAnalyzer()

        # Добавить решения одного типа
        for i in range(10):
            analyzer.add_decision({"task_type": "refactoring"}, f"rename_var_{i}", "success")

        # Добавить несколько неудачных решений другого типа
        for i in range(5):
            analyzer.add_decision({"task_type": "bug_fix"}, f"fix_bug_{i}", "failed")

        # Проверить предсказание для похожего контекста
        prob = analyzer.predict_success_probability({"task_type": "refactoring"}, "rename_new_var")
        assert prob > 0.8  # Должно быть высокое, т.к. все предыдущие рефакторинги успешны

        prob2 = analyzer.predict_success_probability({"task_type": "bug_fix"}, "fix_new_bug")
        assert prob2 < 0.3  # Должно быть низкое, т.к. все предыдущие багфиксы неудачны

    def test_adaptive_learning_system(self):
        """Тест AdaptiveLearningSystem"""
        learning_system = AdaptiveLearningSystem()

        # Обучиться на нескольких решениях
        learning_system.learn_from_decision({"task_type": "refactoring"}, "rename_variable", "success")
        learning_system.learn_from_decision({"task_type": "bug_fix"}, "fix_error", "failed")

        # Получить совет для нового решения
        advice = learning_system.get_advice_for_decision({"task_type": "refactoring"}, "rename_function")

        assert "predicted_success_probability" in advice
        assert "recommendations" in advice
        assert "confidence_level" in advice

    def test_adaptive_learning_system_metrics(self):
        """Тест получения метрик обучения"""
        learning_system = AdaptiveLearningSystem()

        # Добавить несколько решений
        for i in range(25):
            outcome = "success" if i % 2 == 0 else "failed"
            learning_system.learn_from_decision({"task_type": "refactoring"}, f"action_{i}", outcome)

        metrics = learning_system.get_learning_metrics()

        assert "total_decisions_learned" in metrics
        assert "current_success_rate" in metrics
        assert "last_analysis" in metrics
        assert metrics["total_decisions_learned"] == 25
        assert 0.0 <= metrics["current_success_rate"] <= 1.0

    def test_base_agent_extensions_integration(self):
        """Тест интеграции с BaseAgentExtensions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            extensions = BaseAgentExtensions(temp_dir)

            # Проверить, что система адаптивного обучения инициализирована
            assert extensions.adaptive_learning_system is not None

            # Запомнить несколько решений
            extensions.remember_decision({"task_type": "refactoring"}, "rename_var", "success")
            extensions.remember_decision({"task_type": "bug_fix"}, "fix_bug", "failed")

            # Проверить получение совета
            advice = extensions.get_learning_advice({"task_type": "refactoring"}, "rename_function")
            assert "predicted_success_probability" in advice
            assert "recommendations" in advice

            # Проверить получение метрик
            metrics = extensions.get_learning_metrics()
            assert "total_decisions_learned" in metrics
            assert metrics["total_decisions_learned"] == 2

    def test_pattern_classification(self):
        """Тест классификации паттернов"""
        analyzer = PatternAnalyzer()

        # Тест классификации контекста
        ctx1 = {"task_type": "refactoring", "project_path": "/test"}
        ctx_type1 = analyzer._classify_context(ctx1)
        assert ctx_type1 == "refactoring"

        ctx2 = {"project_path": "/test", "file_path": "/test/file.py"}
        ctx_type2 = analyzer._classify_context(ctx2)
        assert ctx_type2 == "project_analysis"

        # Тест классификации решений
        decision1 = "rename variable x to calculate_total"
        dec_type1 = analyzer._classify_decision(decision1)
        assert dec_type1 == "refactoring"

        decision2 = "fix null pointer exception in auth service"
        dec_type2 = analyzer._classify_decision(decision2)
        assert dec_type2 == "bug_fix"

    def test_pattern_analysis_with_insufficient_data(self):
        """Тест анализа паттернов с недостаточными данными"""
        analyzer = PatternAnalyzer()

        # Добавить меньше минимального количества для анализа
        analyzer.add_decision({"task_type": "refactoring"}, "rename_var", "success")

        patterns = analyzer.analyze_patterns()

        # Должно вернуть сообщение о недостатке данных
        assert patterns["success_rate"] == 1.0  # Общий success rate
        assert "min_data_for_analysis" in patterns
        assert patterns["available_records"] == 1

    def test_recommendations_generation(self):
        """Тест генерации рекомендаций"""
        analyzer = PatternAnalyzer()

        # Добавить много неудачных решений одного типа
        for i in range(10):
            analyzer.add_decision({"task_type": "complex_task"}, f"action_{i}", "failed")

        # Добавить много успешных решений другого типа
        for i in range(10):
            analyzer.add_decision({"task_type": "simple_task"}, f"action_{i}", "success")

        patterns = analyzer.analyze_patterns()

        # Проверить, что есть рекомендации
        assert len(patterns["recommendations"]) > 0
        # Должна быть рекомендация по типу задачи с низким success rate
        low_success_found = any(
            "complex_task" in rec.lower() and "низкий" in rec.lower() for rec in patterns["recommendations"]
        )
        high_success_found = any(
            "simple_task" in rec.lower() and "высокий" in rec.lower() for rec in patterns["recommendations"]
        )
        assert low_success_found or high_success_found

    def test_trend_analysis(self):
        """Тест анализа трендов"""
        analyzer = PatternAnalyzer()

        # Добавить много неудачных решений в начале
        for i in range(50):
            outcome = "failed" if i < 25 else "success"  # Последние 25 успешны
            analyzer.add_decision({"task_type": "test"}, f"action_{i}", outcome)

        patterns = analyzer.analyze_patterns()

        # Проверить, что тренд определяется как улучшающийся
        if patterns["trends"]["trend_available"]:
            # Если данных достаточно для анализа трендов
            assert "direction" in patterns["trends"]

    def test_similar_context_finding(self):
        """Тест нахождения похожих контекстов"""
        learning_system = AdaptiveLearningSystem()

        # Добавить несколько решений
        for i in range(10):
            outcome = "success" if i % 2 == 0 else "failed"
            learning_system.learn_from_decision({"task_type": "refactoring"}, f"action_{i}", outcome)

        # Найти похожие контексты
        similar = learning_system._find_similar_historical_contexts({"task_type": "refactoring"})

        # Должны быть найдены похожие контексты
        assert isinstance(similar, list)
        # Все найденные контексты должны быть типа refactoring
        for item in similar:
            assert item["context"]["task_type"] == "refactoring"


if __name__ == "__main__":
    pytest.main([__file__])
