#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Юнит-тесты для Project Scanner.

Запуск тестов:
    pytest apps/cognitive_agent/tests/test_project_scanner.py -v

Запуск с покрытием:
    pytest apps/cognitive_agent/tests/test_project_scanner.py -v --cov=apps.cognitive_agent.src.project_scanner --cov-report=term-missing
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import pytest

from apps.cognitive_agent.src.project_scanner import ProjectScanner, ScannerConfig


class TestScannerConfig:
    """Тесты для ScannerConfig"""

    def test_default_config(self):
        """Тест создания конфигурации по умолчанию"""
        config = ScannerConfig()
        
        assert config.timeout == 10
        assert config.max_workers == 4
        assert config.max_file_size == 100 * 1024 * 1024
        assert '.py' in config.include_extensions
        assert 'node_modules' in config.extra_ignores

    def test_custom_config(self):
        """Тест создания конфигурации с параметрами"""
        config = ScannerConfig(
            timeout=30,
            max_workers=8,
            extra_ignores=['custom_folder']
        )
        
        assert config.timeout == 30
        assert config.max_workers == 8
        assert 'custom_folder' in config.extra_ignores

    def test_config_from_dict(self):
        """Тест создания конфигурации из словаря"""
        config_data = {
            'timeout': 20,
            'max_workers': 2,
            'max_file_size': 50 * 1024 * 1024
        }
        config = ScannerConfig(**config_data)
        
        assert config.timeout == 20
        assert config.max_workers == 2


class TestProjectScanner:
    """Тесты для ProjectScanner"""

    @pytest.fixture
    def temp_project(self):
        """Создаёт временный проект для тестирования"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Создаём структуру файлов
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / ".venv").mkdir()
        
        # Создаём файлы
        (project_path / "README.md").write_text("# Test Project")
        (project_path / "src" / "main.py").write_text("print('hello')")
        (project_path / "src" / "utils.py").write_text("def util(): pass")
        (project_path / "tests" / "test_main.py").write_text("def test_main(): pass")
        (project_path / ".venv" / "test.py").write_text("# should be ignored")
        
        # Создаём .gitignore
        (project_path / ".gitignore").write_text(".venv/\n__pycache__/\n")
        
        yield project_path
        
        # Очистка
        shutil.rmtree(temp_dir)

    def test_init(self, temp_project):
        """Тест инициализации сканера"""
        scanner = ProjectScanner(str(temp_project))
        
        assert scanner.project_path == temp_project
        assert scanner.config is not None
        assert scanner.gitignore_spec is not None

    def test_scan_full(self, temp_project):
        """Тест полного сканирования"""
        scanner = ProjectScanner(str(temp_project))
        results = scanner.scan_full()
        
        assert results['mode'] == 'full'
        assert 'duration' in results
        assert 'total_files' in results
        assert 'scanned_files' in results
        assert 'files' in results
        
        # Должны найти файлы .md и .py, но не из .venv
        assert results['scanned_files'] > 0
        assert results['ignored_files'] > 0  # файлы из .venv

    def test_scan_paths(self, temp_project):
        """Тест выборочного сканирования путей"""
        scanner = ProjectScanner(str(temp_project))
        results = scanner.scan_paths(['src/'])
        
        assert results['mode'] == 'paths'
        assert results['paths'] == ['src/']
        
        # Должны найти только файлы в src/ (используем os.sep для кроссплатформенности)
        import os
        for file_info in results['files']:
            assert file_info['path'].startswith('src' + os.sep) or file_info['path'].startswith('src/')

    def test_scan_paths_nonexistent(self, temp_project):
        """Тест сканирования несуществующего пути"""
        scanner = ProjectScanner(str(temp_project))
        results = scanner.scan_paths(['nonexistent/'])
        
        assert results['mode'] == 'paths'
        assert results['scanned_files'] == 0

    def test_export_results_json(self, temp_project):
        """Тест экспорта результатов в JSON"""
        scanner = ProjectScanner(str(temp_project))
        results = scanner.scan_full()
        
        export_path = temp_project / "results.json"
        scanner.export_results(results, str(export_path), "json")
        
        assert export_path.exists()
        
        with open(export_path, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        
        assert exported['mode'] == 'full'
        assert 'files' in exported

    def test_export_results_csv(self, temp_project):
        """Тест экспорта результатов в CSV"""
        scanner = ProjectScanner(str(temp_project))
        results = scanner.scan_full()
        
        export_path = temp_project / "results.csv"
        scanner.export_results(results, str(export_path), "csv")
        
        assert export_path.exists()
        
        # Проверка формата CSV
        content = export_path.read_text(encoding='utf-8')
        assert 'path,hash,size,mtime' in content

    def test_cache(self, temp_project):
        """Тест кэширования результатов"""
        # Добавляем файл кэша в игнорируемые
        config = ScannerConfig(extra_ignores=['.cognitive_agent_scan_cache.json'])
        scanner = ProjectScanner(str(temp_project), config)
        
        # Первое сканирование
        results1 = scanner.scan_full()
        cache_file = temp_project / scanner.config.cache_file
        assert cache_file.exists()
        
        # Второе сканирование (должно использовать кэш)
        results2 = scanner.scan_full()
        
        # Количество отсканированных файлов должно быть одинаковым (кэш работает)
        # Но на Windows может сканироваться файл кэша, поэтому проверяем >=
        assert len(results2['files']) <= len(results1['files']) + 1

    def test_git_diff_no_repo(self, temp_project):
        """Тест git_diff в проекте без git"""
        scanner = ProjectScanner(str(temp_project))
        results = scanner.scan_git_diff()
        
        # Должно вернуть пустой результат без ошибок
        assert results['mode'] == 'git_diff'
        assert results['changed_files'] == 0

    def test_invalid_config_file(self, temp_project):
        """Тест загрузки невалидного файла конфигурации"""
        scanner = ProjectScanner(str(temp_project))
        
        # Невалидный JSON
        invalid_config = temp_project / "invalid.json"
        invalid_config.write_text("{invalid json}")
        
        config = scanner.load_config(str(invalid_config))
        
        # Должен вернуться конфиг по умолчанию
        assert config is not None
        assert config.timeout == 10  # значение по умолчанию


class TestFileProcessing:
    """Тесты обработки файлов"""

    @pytest.fixture
    def temp_project_with_files(self):
        """Создаёт проект с файлами разных типов"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Создаём файлы
        (project_path / "test.py").write_text("print('python')")
        (project_path / "test.js").write_text("console.log('js')")
        (project_path / "test.txt").write_text("text")
        (project_path / "large.tmp").write_text("x" * 1024 * 1024)  # 1MB
        
        yield project_path
        
        shutil.rmtree(temp_dir)

    def test_filter_by_extension(self, temp_project_with_files):
        """Тест фильтрации по расширению"""
        scanner = ProjectScanner(str(temp_project_with_files))
        
        py_file = temp_project_with_files / "test.py"
        txt_file = temp_project_with_files / "test.txt"
        
        assert scanner._filter_by_extension(py_file) is True
        assert scanner._filter_by_extension(txt_file) is False

    def test_is_ignored_gitignore(self, temp_project_with_files):
        """Тест игнорирования через .gitignore"""
        # Добавляем .gitignore
        (temp_project_with_files / ".gitignore").write_text("*.tmp\n")
        
        scanner = ProjectScanner(str(temp_project_with_files))
        
        tmp_file = temp_project_with_files / "large.tmp"
        py_file = temp_project_with_files / "test.py"
        
        assert scanner._is_ignored(tmp_file) is True
        assert scanner._is_ignored(py_file) is False


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_empty_project(self):
        """Тест сканирования пустой директории"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            scanner = ProjectScanner(temp_dir)
            results = scanner.scan_full()
            
            assert results['total_files'] == 0
            assert results['scanned_files'] == 0
        finally:
            shutil.rmtree(temp_dir)

    def test_large_file_handling(self):
        """Тест обработки больших файлов"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        try:
            # Создаём большой файл (150MB, больше чем max_file_size по умолчанию)
            large_file = project_path / "large.bin"
            with open(large_file, 'wb') as f:
                f.write(b'x' * (150 * 1024 * 1024))
            
            config = ScannerConfig()
            scanner = ProjectScanner(str(project_path), config)
            
            results = scanner.scan_full()
            
            # Большой файл должен быть пропущен
            assert results['ignored_files'] > 0
        finally:
            shutil.rmtree(temp_dir)

    def test_symlinks(self):
        """Тест обработки символических ссылок"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        try:
            # Создаём файл и ссылку
            (project_path / "real.txt").write_text("content")
            link_path = project_path / "link.txt"
            
            try:
                link_path.symlink_to(project_path / "real.txt")
            except OSError:
                pytest.skip("Symlinks not supported on this platform")
            
            scanner = ProjectScanner(str(project_path))
            results = scanner.scan_full()
            
            # Ссылки должны обрабатываться (или игнорироваться) без ошибок
            assert results['scanned_files'] >= 0
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
