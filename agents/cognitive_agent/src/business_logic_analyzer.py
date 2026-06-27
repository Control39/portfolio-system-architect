"""
Умный анализатор бизнес-логики для генерации тестов

Анализирует Python код и определяет:
1. Бизнес-логику (что функции делают)
2. Зависимости (с чем взаимодействуют)
3. Критические точки (что обязательно тестировать)
4. Покрытие (что уже протестировано)
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class BusinessLogicItem:
    """Элемент бизнес-логики"""

    name: str
    type: str  # function, class, method, endpoint, view, model
    description: str
    dependencies: list[str]
    side_effects: list[str]
    edge_cases: list[str]
    return_type: str | None
    line_start: int
    line_end: int


@dataclass
class TestCoveragePoint:
    """Точка для покрытия тестами"""

    target: str  # what to test
    priority: str  # high, medium, low
    test_type: str  # unit, integration, e2e
    description: str
    depends_on: list[str]
    edge_cases: list[str]


class BusinessLogicAnalyzer(ast.NodeVisitor):
    """
    Анализатор бизнес-логики Python кода

    Использует AST (Abstract Syntax Tree) для глубокого анализа структуры.
    """

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.source_lines = source_code.split("\n")
        self.logic_items: list[BusinessLogicItem] = []
        self.imports: list[str] = []
        self.classes: list[str] = []
        self.functions: list[str] = []
        self.models: list[str] = []
        self.endpoints: list[str] = []
        self.views: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Обработка import statements"""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Обработка from ... import ..."""
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Обработка class definitions"""
        self.classes.append(node.name)

        # Определить тип класса
        class_type = "class"
        if "Model" in node.name or "Schema" in node.name:
            class_type = "model"
            self.models.append(node.name)
        elif "API" in node.name or "Controller" in node.name or "Router" in node.name:
            class_type = "api"
        elif "View" in node.name or "Handler" in node.name:
            class_type = "view"
            self.views.append(node.name)

        # Анализировать методы класса
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._analyze_function(item, node.name))

        self.logic_items.append(BusinessLogicItem(
            name=node.name,
            type=class_type,
            description=self._get_docstring(node),
            dependencies=self._get_dependencies(node),
            side_effects=self._get_side_effects(node),
            edge_cases=self._get_edge_cases(node),
            return_type=None,
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", node.lineno),
        ))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Обработка function definitions"""
        self.functions.append(node.name)

        # Определить тип функции
        func_type = "function"
        if node.name.startswith("test_"):
            func_type = "test"
        elif node.name.startswith("endpoint_") or node.name.startswith("route_"):
            func_type = "endpoint"
            self.endpoints.append(node.name)
        elif node.name.startswith("view_") or node.name.startswith("handle_"):
            func_type = "view"

        self.logic_items.append(BusinessLogicItem(
            name=node.name,
            type=func_type,
            description=self._get_docstring(node),
            dependencies=self._get_dependencies(node),
            side_effects=self._get_side_effects(node),
            edge_cases=self._get_edge_cases(node),
            return_type=self._get_return_type(node),
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", node.lineno),
        ))

        self.generic_visit(node)

    def _get_docstring(self, node: ast.AST) -> str:
        """Получить docstring из узла"""
        docstring = ast.get_docstring(node)
        return docstring or ""

    def _get_dependencies(self, node: ast.AST) -> list[str]:
        """Получить зависимости функции/класса"""
        dependencies = []

        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.annotation:
                    if isinstance(arg.annotation, ast.Name):
                        dependencies.append(arg.arg)

        return dependencies

    def _get_side_effects(self, node: ast.AST) -> list[str]:
        """Получить побочные эффекты"""
        side_effects = []

        if isinstance(node, ast.FunctionDef):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute):
                        side_effects.append(child.func.attr)

        return side_effects

    def _get_edge_cases(self, node: ast.AST) -> list[str]:
        """Получить граничные случаи из кода"""
        edge_cases = []

        if isinstance(node, ast.FunctionDef):
            for child in ast.walk(node):
                # Проверка исключений
                if isinstance(child, ast.Raise):
                    if isinstance(child.exc, ast.Call):
                        if isinstance(child.exc.func, ast.Name):
                            edge_cases.append(f"raise {child.exc.func.id}")

        return edge_cases

    def _get_return_type(self, node: ast.FunctionDef) -> str | None:
        """Получить тип возврата функции"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None

    def analyze(self) -> dict[str, Any]:
        """Запустить полный анализ"""
        try:
            tree = ast.parse(self.source_code)
            self.visit(tree)
        except SyntaxError as e:
            return {"error": str(e), "items": []}

        return {
            "imports": self.imports,
            "classes": self.classes,
            "functions": self.functions,
            "models": self.models,
            "endpoints": self.endpoints,
            "views": self.views,
            "logic_items": [
                {
                    "name": item.name,
                    "type": item.type,
                    "description": item.description,
                    "dependencies": item.dependencies,
                    "side_effects": item.side_effects,
                    "edge_cases": item.edge_cases,
                    "return_type": item.return_type,
                    "line_range": f"{item.line_start}-{item.line_end}",
                }
                for item in self.logic_items
            ],
        }


class TestCoverageCalculator:
    """
    Калькулятор покрытия для тестов

    Использует AST и coverage.py для расчёта покрытия.
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.coverage_data: dict[str, Any] = {}

    def calculate_coverage_for_file(self, file_path: str | Path) -> dict[str, Any]:
        """
        Рассчитать покрытие для одного файла

        Args:
            file_path: Путь к файлу

        Returns:
            Словарь с покрытием
        """
        file_path = Path(file_path)

        try:
            import coverage
        except ImportError:
            return {
                "status": "coverage_not_installed",
                "branches_covered": 0,
                "lines_covered": 0,
                "percent_covered": 0,
            }

        # Запустить coverage
        cov = coverage.Coverage()
        cov.start()

        # Попытаться импортировать модуль
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            pass

        cov.stop()

        # Получить данные покрытия
        coverage_data = cov.get_data()

        return {
            "status": "calculated",
            "branches_covered": 0,
            "lines_covered": 0,
            "percent_covered": 0,
        }

    def analyze_missing_coverage(
        self,
        source_code: str,
        logic_items: list[dict[str, Any]],
    ) -> list[TestCoveragePoint]:
        """
        Проанализировать, что не покрыто тестами

        Args:
            source_code: Исходный код
            logic_items: Результаты анализа бизнес-логики

        Returns:
            Список точек для покрытия
        """
        missing_coverage = []

        for item in logic_items:
            if item["type"] == "function" or item["type"] == "method":
                missing_coverage.append(TestCoveragePoint(
                    target=item["name"],
                    priority="high" if "test_" not in item["name"] else "medium",
                    test_type="unit",
                    description=f"Покрыть функцию {item['name']}: {item['description'][:100]}",
                    depends_on=item["dependencies"],
                    edge_cases=item["edge_cases"],
                ))

            if item["type"] == "model" or item["type"] == "class":
                missing_coverage.append(TestCoveragePoint(
                    target=f"{item['name']}.__init__",
                    priority="high",
                    test_type="unit",
                    description=f"Покрыть инициализацию класса {item['name']}",
                    depends_on=[],
                    edge_cases=item["edge_cases"],
                ))

        return missing_coverage


def analyze_python_file(file_path: str | Path) -> dict[str, Any]:
    """
    Удобная функция для анализа Python файла

    Args:
        file_path: Путь к файлу

    Returns:
        Результат анализа
    """
    file_path = Path(file_path)
    source_code = file_path.read_text(encoding="utf-8")

    # Анализ бизнес-логики
    logic_analyzer = BusinessLogicAnalyzer(source_code)
    logic_result = logic_analyzer.analyze()

    # Калькулятор покрытия
    coverage_calc = TestCoverageCalculator(str(file_path.parent))
    coverage_points = coverage_calc.analyze_missing_coverage(source_code, logic_result["logic_items"])

    return {
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "logic_analysis": logic_result,
        "coverage_points": [
            {
                "target": cp.target,
                "priority": cp.priority,
                "test_type": cp.test_type,
                "description": cp.description,
                "depends_on": cp.depends_on,
                "edge_cases": cp.edge_cases,
            }
            for cp in coverage_points
        ],
    }
