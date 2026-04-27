"""
Клиент для тестирования MCP сервера
"""

import requests
import json
import argparse
import sys
from typing import Dict, Any, List

# Base URL of the MCP server
BASE_URL = "http://localhost:8000"

class MCPTestClient:
    """Клиент для тестирования MCP сервера"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self) -> bool:
        """Тестирование health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            result = response.json()
            print(f"✓ Health check passed: {result}")
            return True
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False
    
    def test_get_rules(self) -> bool:
        """Тестирование get rules endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/rules")
            response.raise_for_status()
            rules = response.json()
            print(f"✓ Get rules passed:")
            print(json.dumps(rules, indent=2))
            return True
        except Exception as e:
            print(f"✗ Get rules failed: {e}")
            return False
    
    def test_process_prompt(
        self, 
        prompt: str = "Test prompt for MCP server",
        variables: Dict[str, Any] = None,
        rules: List[str] = None
    ) -> bool:
        """Тестирование process prompt endpoint"""
        if variables is None:
            variables = {"test_var": "test_value"}
        if rules is None:
            rules = ["Test rule 1", "Test rule 2"]
            
        try:
            payload = {
                "prompt": prompt,
                "variables": variables,
                "rules": rules
            }
            
            response = self.session.post(
                f"{self.base_url}/process-prompt", 
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Process prompt passed:")
            print(json.dumps(result, indent=2))
            return True
        except Exception as e:
            print(f"✗ Process prompt failed: {e}")
            return False
    
    def run_all_tests(self) -> int:
        """Запуск всех тестов"""
        print("Starting MCP Server tests...\n")
        
        success = True
        
        if not self.test_health_check():
            success = False
        
        if not self.test_get_rules():
            success = False
        
        if not self.test_process_prompt():
            success = False
        
        print("\nTests completed.")
        status = 'SUCCESS' if success else 'FAILED'
        print(f"Status: {status}")
        
        return 0 if success else 1

def main():
    """Основная функция с поддержкой командной строки"""
    parser = argparse.ArgumentParser(description='Test client for MCP server')
    parser.add_argument('--url', default=BASE_URL, help='MCP server URL')
    parser.add_argument('--prompt', help='Prompt to test')
    parser.add_argument('--variable', action='append', nargs=2, metavar=('KEY', 'VALUE'), 
                       help='Variables for the prompt (can be used multiple times)')
    parser.add_argument('--rule', action='append', help='Rules to apply (can be used multiple times)')
    
    args = parser.parse_args()
    
    # Создаем клиент
    client = MCPTestClient(args.url)
    
    # Если указаны параметры командной строки, тестируем только process-prompt
    if args.prompt:
        # Преобразуем переменные в словарь
        variables = {}
        if args.variable:
            for key, value in args.variable:
                variables[key] = value
        
        # Используем указанные правила или правила по умолчанию
        rules = args.rule if args.rule else None
        
        # Тестируем только process-prompt с заданными параметрами
        success = client.test_process_prompt(args.prompt, variables, rules)
        return 0 if success else 1
    
    # Иначе запускаем все тесты
    return client.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())