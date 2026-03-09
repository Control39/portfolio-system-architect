"""
Веб-интерфейс для IT Compass
Основное приложение с веб-интерфейсом для отслеживания навыков
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Импортируем модули из проекта
from ..core.tracker import SkillTracker
from ..core.api_integration import APIIntegration
from ..utils.portfolio_gen import PortfolioGenerator
from ..core.mental.psychological_support import PsychologicalSupport


class ITCompassApp:
    """Основной класс веб-приложения IT Compass"""
    
    def __init__(self):
        """Инициализация приложения"""
        self.tracker = SkillTracker()
        self.api_integration = APIIntegration()
        self.portfolio_gen = PortfolioGenerator()
        self.psychological_support = PsychologicalSupport()
        
        # Настройка страницы
        st.set_page_config(
            page_title="IT Compass - Трекер навыков",
            page_icon="🧭",
            layout="wide"
        )
    
    def render_header(self):
        """Отображение заголовка приложения"""
        st.title("🧭 IT Compass")
        st.subheader("Ваш персональный навигатор в мире IT")
        
        # Краткая информация
        st.markdown("""
        IT Compass помогает отслеживать ваш прогресс в освоении IT навыков,
        планировать развитие и создавать профессиональное портфолио.
        """)
    
    def render_progress_overview(self):
        """Отображение обзора прогресса"""
        st.header("📊 Обзор прогресса")
        
        # Получаем сводку прогресса
        summary = self.tracker.get_progress_summary()
        
        # Отображаем основные метрики
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Всего маркеров", summary['total_markers'])
        
        with col2:
            st.metric("Выполнено", summary['completed_markers'])
        
        with col3:
            st.metric("Процент выполнения", f"{summary['completion_percentage']}%")
        
        # Прогресс-бар
        st.progress(summary['completion_percentage'] / 100)
        
        # Статистика по направлениям
        if summary['directions']:
            st.subheader("По направлениям")
            directions_data = summary['directions']
            
            # Создаем списки для диаграммы
            directions = list(directions_data.keys())
            counts = list(directions_data.values())
            
            # Отображаем данные в виде таблицы
            st.table({
                "Направление": directions,
                "Выполнено маркеров": counts
            })
    
    def render_markers_list(self):
        """Отображение списка маркеров"""
        st.header("🎯 Маркеры навыков")
        
        # Фильтры
        directions = list(set([marker.direction for marker in self.tracker.markers.values()]))
        selected_direction = st.selectbox("Фильтр по направлению", ["Все"] + directions)
        
        levels = ["basic", "advanced", "expert"]
        selected_level = st.selectbox("Фильтр по уровню", ["Все"] + levels)
        
        # Фильтрация маркеров
        filtered_markers = list(self.tracker.markers.values())
        
        if selected_direction != "Все":
            filtered_markers = [m for m in filtered_markers if m.direction == selected_direction]
        
        if selected_level != "Все":
            filtered_markers = [m for m in filtered_markers if m.level == selected_level]
        
        # Отображение маркеров
        for marker in filtered_markers:
            completed = self.tracker.is_marker_completed(marker.id)
            
            # Карточка маркера
            card_color = "🟢" if completed else "⚪"
            st.markdown(f"### {card_color} {marker.title}")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Направление:** {marker.direction}")
                st.markdown(f"**Уровень:** {marker.level}")
                st.markdown(f"**Описание:** {marker.description}")
                
                # Примеры
                if marker.examples:
                    st.markdown("**Примеры:**")
                    for example in marker.examples:
                        st.markdown(f"- {example}")
            
            with col2:
                # Кнопка выполнения/отмены
                if completed:
                    if st.button("Отменить", key=f"uncomplete_{marker.id}"):
                        self.tracker.uncomplete_marker(marker.id)
                        st.experimental_rerun()
                else:
                    if st.button("Выполнить", key=f"complete_{marker.id}"):
                        # Показываем форму для добавления артефактов
                        st.session_state[f"show_artifacts_{marker.id}"] = True
            
            with col3:
                # Статус выполнения
                if completed:
                    st.success("Выполнено")
                else:
                    st.info("Не выполнено")
            
            # Форма для добавления артефактов
            if st.session_state.get(f"show_artifacts_{marker.id}", False):
                st.markdown("#### Добавить артефакты")
                artifacts = st.text_area("Артефакты (по одному на строку)", 
                                       key=f"artifacts_{marker.id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Подтвердить выполнение", key=f"confirm_{marker.id}"):
                        artifact_list = [a.strip() for a in artifacts.split('\n') if a.strip()]
                        self.tracker.complete_marker(marker.id, artifact_list)
                        st.session_state[f"show_artifacts_{marker.id}"] = False
                        st.experimental_rerun()
                
                with col2:
                    if st.button("Отмена", key=f"cancel_{marker.id}"):
                        st.session_state[f"show_artifacts_{marker.id}"] = False
                        st.experimental_rerun()
            
            st.markdown("---")
    
    def render_portfolio_section(self):
        """Отображение раздела портфолио"""
        st.header("📁 Портфолио")
        
        # Генерация портфолио
        if st.button("Сгенерировать портфолио"):
            try:
                self.portfolio_gen.generate_portfolio()
                st.success("Портфолио успешно сгенерировано!")
                
                # Показываем ссылки на сгенерированные файлы
                st.markdown("### Сгенерированные файлы:")
                st.markdown("- [README.md](./portfolio/README.md)")
                st.markdown("- [portfolio.json](./portfolio/portfolio.json)")
                st.markdown("- [index.html](./portfolio/index.html)")
                
            except Exception as e:
                st.error(f"Ошибка генерации портфолио: {e}")
        
        # Экспорт прогресса
        st.subheader("Экспорт данных")
        if st.button("Экспортировать прогресс"):
            try:
                progress_data = self.tracker.export_progress()
                progress_json = json.dumps(progress_data, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="Скачать прогресс (JSON)",
                    data=progress_json,
                    file_name="it_compass_progress.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"Ошибка экспорта: {e}")
    
    def render_support_section(self):
        """Отображение раздела поддержки"""
        st.header("💖 Поддержка")
        
        # Психологическая поддержка
        if st.button("Получить поддержку"):
            support_report = self.psychological_support.generate_support_report()
            
            st.markdown("### 💖 Психологическая поддержка")
            st.markdown(f"**{support_report['gentle_encouragement']}**")
            
            st.markdown("#### Простые активности:")
            for activity in support_report['simple_activities']:
                st.markdown(f"- {activity}")
            
            st.markdown(f"**Цитата:** {support_report['motivational_quote']}")
            st.markdown(f"**Аффирмация:** {support_report['positive_affirmation']}")
            
            # Проверяем риск выгорания
            # В реальном приложении здесь будут реальные данные
            recent_activity = {
                "last_activity": datetime.now().isoformat(),
                "break_count": 0
            }
            
            if self.psychological_support.is_burnout_risk(recent_activity):
                st.warning("⚠️ Обнаружен риск выгорания!")
                recovery_plan = self.psychological_support.suggest_recovery_plan()
                st.markdown("#### План восстановления:")
                st.markdown(f"**{recovery_plan['title']}**")
                st.markdown(recovery_plan['description'])
                
                for step in recovery_plan['steps']:
                    st.markdown(f"**День {step['day']}:**")
                    for activity in step['activities']:
                        st.markdown(f"- {activity}")
    
    def render_integrations_section(self):
        """Отображение раздела интеграций"""
        st.header("🔌 Интеграции")
        
        # GitHub интеграция
        st.subheader("GitHub")
        github_username = st.text_input("Имя пользователя GitHub")
        if st.button("Получить данные с GitHub") and github_username:
            try:
                github_data = self.api_integration.github_integration(github_username)
                if github_data:
                    st.success(f"Получены данные для пользователя {github_username}")
                    st.json(github_data)
                else:
                    st.error("Не удалось получить данные с GitHub")
            except Exception as e:
                st.error(f"Ошибка интеграции с GitHub: {e}")
        
        # Stack Overflow интеграция
        st.subheader("Stack Overflow")
        stackoverflow_id = st.text_input("ID пользователя Stack Overflow")
        if st.button("Получить данные с Stack Overflow") and stackoverflow_id:
            try:
                stackoverflow_data = self.api_integration.stackoverflow_integration(stackoverflow_id)
                if stackoverflow_data:
                    st.success(f"Получены данные для пользователя {stackoverflow_id}")
                    st.json(stackoverflow_data)
                else:
                    st.error("Не удалось получить данные с Stack Overflow")
            except Exception as e:
                st.error(f"Ошибка интеграции с Stack Overflow: {e}")
    
    def run(self):
        """Запуск приложения"""
        # Инициализация состояния сессии
        if 'show_artifacts' not in st.session_state:
            st.session_state['show_artifacts'] = {}
        
        # Отображение заголовка
        self.render_header()
        
        # Навигация по разделам
        section = st.sidebar.radio(
            "Навигация",
            ["Обзор", "Маркеры", "Портфолио", "Поддержка", "Интеграции"]
        )
        
        # Отображение выбранного раздела
        if section == "Обзор":
            self.render_progress_overview()
        elif section == "Маркеры":
            self.render_markers_list()
        elif section == "Портфолио":
            self.render_portfolio_section()
        elif section == "Поддержка":
            self.render_support_section()
        elif section == "Интеграции":
            self.render_integrations_section()
        
        # Футер
        st.sidebar.markdown("---")
        st.sidebar.markdown("### IT Compass")
        st.sidebar.markdown(f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Запуск приложения
if __name__ == "__main__":
    app = ITCompassApp()
    app.run()