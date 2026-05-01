import time


class LowEnergyMode:
    """Специальный режим для работы в состоянии низкой энергии"""

    def __init__(self):
        self.enabled = False
        self.last_interaction = time.time()
        self.simple_menu = [
            "1. Посмотреть прогресс",
            "2. Простое упражнение",
            "3. Мотивационная цитата",
            "4. Выход из режима",
        ]
        self.exercises = [
            {
                "name": "Дыхание 4-7-8",
                "description": "Вдох на 4 счета, задержка на 7, выдох на 8",
                "duration": "2 минуты",
            },
            {
                "name": "Растяжка шеи",
                "description": "Медленные повороты головы в стороны",
                "duration": "1 минута",
            },
            {
                "name": "Взгляд в окно",
                "description": "2 минуты смотрите вдаль, расслабляя глаза",
                "duration": "2 минуты",
            },
        ]

    def activate(self):
        """Активировать режим низкой энергии"""
        self.enabled = True
        self.last_interaction = time.time()
        print("\n" + "=" * 50)
        print("😴 РЕЖИМ 'НИЗКОЙ ЭНЕРГИИ' АКТИВИРОВАН")
        print("=" * 50)
        print("В этом режиме доступны только базовые функции:")
        print("✅ Простые упражнения для восстановления энергии")
        print("✅ Мотивационные цитаты")
        print("✅ Просмотр текущего прогресса")
        print("🚫 Сложные аналитические функции")
        print("🚫 Настройки и конфигурация")
        print("🚫 Интеграция с внешними сервисами")
        print(
            "\n💡 Совет: Этот режим поможет вам восстановить силы и сосредоточиться на самом важном."
        )
        print("Нажмите Enter, чтобы перейти к упрощённому меню...")
        input()

    def is_active(self) -> bool:
        """Проверить, активен ли режим низкой энергии"""
        # Автоматическое отключение через 2 часа неактивности
        if self.enabled and (time.time() - self.last_interaction > 7200):
            self.deactivate()
        return self.enabled

    def deactivate(self):
        """Деактивировать режим низкой энергии"""
        if self.enabled:
            print("\n" + "=" * 50)
            print("⚡ РЕЖИМ 'НИЗКОЙ ЭНЕРГИИ' ДЕАКТИВИРОВАН")
            print("=" * 50)
            print("Все функции приложения доступны в полном объёме")
            print("=" * 50)
            self.enabled = False

    def show_simple_menu(self) -> str:
        """Показать упрощённое меню"""
        self.last_interaction = time.time()

        print("\n" + "=" * 40)
        print("😴 РЕЖИМ НИЗКОЙ ЭНЕРГИИ")
        print("=" * 40)

        for item in self.simple_menu:
            print(item)

        print("=" * 40)
        return input("\nВыберите опцию (1-4): ")

    def show_progress(self):
        """Показать упрощённый прогресс"""
        print("\n" + "=" * 40)
        print("📊 ВАШ ТЕКУЩИЙ ПРОГРЕСС")
        print("=" * 40)
        print("✅ Основные компетенции: 2 из 17")
        print("✅ Прогресс обучения: 12%")
        print("✅ Последнее достижение: 'Запуск приложения'")
        print("\n💡 Совет: Сегодня отлично подойдут простые упражнения для поддержания прогресса")
        print("=" * 40)
        input("\nНажмите Enter, чтобы продолжить...")

    def show_simple_exercise(self):
        """Показать простое упражнение"""
        exercise = self.exercises[0]  # Берём первое упражнение

        print("\n" + "=" * 40)
        print("🧘 ПРОСТОЕ УПРАЖНЕНИЕ")
        print("=" * 40)
        print(f"🎯 {exercise['name']}")
        print(f"📝 {exercise['description']}")
        print(f"⏱️ {exercise['duration']}")
        print("\n💡 Это упражнение поможет вам восстановить энергию и снизить уровень стресса")
        print("=" * 40)
        input("\nНажмите Enter, когда будете готовы выполнить упражнение...")

        print("\n⏳ Выполняем упражнение...")
        time.sleep(3)
        print("✅ Упражнение выполнено! Как вы себя чувствуете?")
        input("\nНажмите Enter, чтобы продолжить...")

    def run(self):
        """Запустить режим низкой энергии"""
        while self.is_active():
            choice = self.show_simple_menu()

            if choice == "1":
                self.show_progress()

            elif choice == "2":
                self.show_simple_exercise()

            elif choice == "3":
                # Здесь можно добавить импорт из mental_support.py
                try:
                    from core.mental_support import show_random_quote_on_startup

                    show_random_quote_on_startup()
                    input("\nНажмите Enter, чтобы продолжить...")
                except:
                    print("\n💡 Помните: маленькие шаги приводят к большим результатам")
                    input("\nНажмите Enter, чтобы продолжить...")

            elif choice == "4":
                self.deactivate()
                break

            else:
                print("❌ Неверный выбор. Пожалуйста, выберите опцию от 1 до 4.")
                input("\nНажмите Enter, чтобы продолжить...")


# Функция для интеграции в основное приложение
def get_low_energy_mode():
    """Получить экземпляр режима низкой энергии"""
    return LowEnergyMode()


if __name__ == "__main__":
    # Демонстрация работы режима
    mode = LowEnergyMode()
    mode.activate()
    mode.run()
