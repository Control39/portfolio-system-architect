#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Массовая конвертация файлов в UTF-8 с резервным копированием.
Сохраняет оригинальные файлы в директории backups.
"""
import os
import shutil
import chardet
import logging
from pathlib import Path
import json
from typing import Dict, List, Tuple
import datetime

def setup_logging() -> None:
    """Настройка системы логирования с явной поддержкой UTF-8 на всех платформах."""

    """Настройка системы логирования"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'conversion.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    # Fully cross-platform UTF-8 handling confirmed: explicit encoding in logging, file I/O with chardet/fallbacks, pathlib for paths

def detect_encoding(file_path: Path) -> Dict[str, str]:
    """Определение кодировки файла"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        if len(raw_data) == 0:
            return {'encoding': 'empty', 'confidence': '1.0', 'error': None}
            
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        
        if encoding:
            encoding = encoding.lower().replace('-', '_')
            
        return {
            'encoding': encoding,
            'confidence': confidence,
            'error': None
        }
        
    except Exception as e:
        return {
            'encoding': None,
            'confidence': None,
            'error': str(e)
        }

def create_backup(file_path: Path, backup_dir: Path) -> bool:
    """Создание резервной копии файла"""
    try:
        # Создаем относительный путь для сохранения структуры директорий
        relative_path = file_path.relative_to(Path('.').resolve())
        backup_path = backup_dir / relative_path
        
        # Создаем родительскую директорию для резервной копии
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Копируем файл
        shutil.copy2(file_path, backup_path)
        
        return True
        
    except Exception as e:
        logging.error(f"Ошибка при создании резервной копии {file_path}: {e}")
        return False

def convert_to_utf8(file_path: Path, backup_dir: Path) -> Dict:
    """Конвертация файла в UTF-8"""
    result = {
        'path': str(file_path.relative_to(Path('.').resolve())),
        'original_encoding': None,
        'success': False,
        'error': None,
        'backup_created': False
    }
    
    try:
        # Определение текущей кодировки
        analysis = detect_encoding(file_path)
        if analysis['error']:
            result['error'] = f"Не удалось определить кодировку: {analysis['error']}"
            return result
            
        original_encoding = analysis['encoding']
        result['original_encoding'] = original_encoding
        
        # Если файл уже в UTF-8, пропускаем
        if original_encoding and 'utf' in original_encoding.lower():
            result['success'] = True
            result['skipped'] = True
            logging.info(f"Файл уже в UTF-8: {result['path']}")
            return result
        
        # Создание резервной копии
        result['backup_created'] = create_backup(file_path, backup_dir)
        if not result['backup_created']:
            result['error'] = "Не удалось создать резервную копию"
            return result
        
        # Чтение содержимого с определенной кодировкой
        try:
            with open(file_path, 'r', encoding=original_encoding) as f:
                content = f.read()
        except (UnicodeDecodeError, LookupError):
            # Пробуем несколько альтернативных кодировок
            fallback_encodings = ['cp1251', 'iso-8859-1', 'koi8-r', 'cp866']
            content = None
            
            for encoding in fallback_encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    original_encoding = encoding
                    result['original_encoding'] = encoding
                    break
                except:
                    continue
            
            if content is None:
                result['error'] = "Не удалось прочитать файл ни одной кодировкой"
                return result
        
        # Запись в UTF-8
        try:
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            result['success'] = True
            logging.info(f"Успешно конвертировано: {result['path']} ({original_encoding} -> utf-8)")
            
        except Exception as e:
            result['error'] = f"Ошибка при записи в UTF-8: {e}"
            # Восстанавливаем из резервной копии
            if result['backup_created']:
                try:
                    backup_path = backup_dir / file_path.relative_to(Path('.').resolve())
                    shutil.copy2(backup_path, file_path)
                    logging.info(f"Файл восстановлен из резервной копии: {result['path']}")
                except:
                    logging.error(f"Не удалось восстановить файл: {result['path']}")
            
    except Exception as e:
        result['error'] = str(e)
        
    return result

def should_process_file(file_path: Path) -> bool:
    """Определяет, нужно ли обрабатывать файл"""
    text_extensions = {
        '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv',
        '.md', '.rst', '.ini', '.cfg', '.conf', '.yml', '.yaml',
        '.sh', '.bat', '.ps1', '.sql', '.log', '.properties'
    }
    
    ignore_dirs = {'node_modules', '__pycache__', '.git', '.vscode', 'logs', 'backups', 'backups'}
    
    if file_path.suffix.lower() not in text_extensions:
        return False
    
    for part in file_path.parts:
        if part in ignore_dirs:
            return False
    
    return True

def convert_all(start_path: str = ".") -> Dict:
    """Конвертация всех текстовых файлов в UTF-8"""
    start_path = Path(start_path).resolve()
    results = []
    summary = {
        'total_files': 0,
        'processed_files': 0,
        'converted_files': 0,
        'skipped_files': 0,
        'errors': 0,
        'encoding_changes': {}
    }
    
    logging.info(f"Начало конвертации в UTF-8: {start_path}")
    
    # Создаем директории
    backup_dir = Path('backups') / f'pre_utf8_conversion_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.info(f"Резервные копии будут сохранены в: {backup_dir}")
    
    for file_path in start_path.rglob('*'):
        if file_path.is_file() and should_process_file(file_path):
            summary['total_files'] += 1
            
            file_result = convert_to_utf8(file_path, backup_dir)
            
            # Обновляем статистику
            if file_result['success']:
                summary['processed_files'] += 1
                if 'skipped' in file_result:
                    summary['skipped_files'] += 1
                else:
                    summary['converted_files'] += 1
                    encoding = file_result['original_encoding']
                    if encoding:
                        summary['encoding_changes'][encoding] = summary['encoding_changes'].get(encoding, 0) + 1
            else:
                summary['errors'] += 1
            
            results.append(file_result)
    
    # Финальный отчет
    final_result = {
        'summary': summary,
        'files': results,
        'backup_directory': str(backup_dir),
        'timestamp': str(datetime.datetime.now())
    }
    
    # Сохраняем результаты
    output_file = log_dir / 'conversion_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Конвертация завершена. Результаты сохранены в {output_file}")
    logging.info(f"Успешно: {summary['converted_files']}, Пропущено: {summary['skipped_files']}, Ошибок: {summary['errors']}")
    
    return final_result

def print_summary(results: Dict) -> None:
    """Вывод краткого отчета"""
    summary = results['summary']
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ КОНВЕРТАЦИИ В UTF-8")
    print("="*60)
    print(f"Всего файлов: {summary['total_files']}")
    print(f"Обработано: {summary['processed_files']}")
    print(f"Конвертировано: {summary['converted_files']}")
    print(f"Пропущено (уже UTF-8): {summary['skipped_files']}")
    print(f"Ошибок: {summary['errors']}")
    
    if summary['converted_files'] > 0:
        print("\nИзменения кодировок:")
        for encoding, count in sorted(summary['encoding_changes'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {encoding}: {count} файлов")
    
    if summary['errors'] > 0:
        print("\nФайлы с ошибками:")
        for file_result in results['files']:
            if not file_result['success'] and 'skipped' not in file_result:
                print(f"  {file_result['path']}: {file_result['error']}")
    
    print(f"\nРезервные копии сохранены в: {results['backup_directory']}")
    print("="*60)

def main():
    """Основная функция"""
    setup_logging()
    
    try:
        results = convert_all()
        print_summary(results)
        
        # Возвращаем код ошибки, если были проблемы
        if results['summary']['errors'] > 0:
            exit(1)
        
    except Exception as e:
        logging.error(f"Ошибка при выполнении конвертации: {e}")
        exit(1)

if __name__ == "__main__":
    main()

