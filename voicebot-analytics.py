#!/usr/bin/env python3
"""
voicebot-analytics
Дашборд для аналитика по анализу диалогов бота
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
from collections import Counter
import random

# ============================================================================
# КОНФИГУРАЦИЯ И ГЕНЕРАЦИЯ ДАННЫХ
# ============================================================================

@st.cache_data
def generate_synthetic_data(num_dialogs=11486):
    """Генерируем синтетические данные для демонстрации"""
    np.random.seed(42)
    random.seed(42)
    
    # Даты за неделю
    end_date = datetime(2026, 6, 5)
    start_date = end_date - timedelta(days=7)
    
    # Возможные причины завершения
    end_reasons = [
        'client_hangup', 'client_hangup', 'client_hangup', 
        'bot_hangup', 'bot_hangup', 
        'no_answer', 'busy', 'technical_error', 'timeout'
    ]
    
    # Возможные статусы
    statuses = ['completed', 'failed', 'answered', 'no_answer', 'busy']
    
    # генерация данных
    data = []
    
    for i in range(num_dialogs):
        # Дата и время
        call_time = start_date + timedelta(
            days=np.random.randint(0, 7),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        
        # Телефон (обезличенный)
        phone = f"+7(***){np.random.randint(1000000, 9999999)}"
        
        # Длительность
        if np.random.random() < 0.15:  # 15% очень короткие
            duration_sec = np.random.randint(0, 10)
        elif np.random.random() < 0.3:  # 30% короткие
            duration_sec = np.random.randint(10, 30)
        elif np.random.random() < 0.4:  # 40% средние
            duration_sec = np.random.randint(30, 120)
        else:  # 15% длинные
            duration_sec = np.random.randint(120, 600)
        
        duration_min = duration_sec // 60
        duration_sec_remain = duration_sec % 60
        duration_str = f"{duration_min}:{duration_sec_remain:02d}"
        
        # Статус
        status = np.random.choice(statuses)
        
        # Причина завершения
        if duration_sec < 5:
            end_reason = 'client_hangup' if np.random.random() < 0.8 else 'no_answer'
        else:
            end_reason = np.random.choice(end_reasons)
        
        # Определяем этап диалога
        stage = determine_dialog_stage(duration_sec, end_reason)
        
        # Генерация истории диалога
        dialog_history = generate_dialog_history(stage, end_reason)
        
        # Ссылка на аудио
        audio_url = f"https://storage.botamin.ai/calls/{phone}_{call_time.strftime('%Y%m%d_%H%M%S')}.mp3"
        
        data.append({
            'телефон': phone,
            'дата и время': call_time,
            'длительность мин:сек': duration_str,
            'длительность сек': duration_sec,
            'статус': status,
            'запись аудио': audio_url,
            'причина завершения': end_reason,
            'история диалога юзер-бот': dialog_history,
            'этап': stage,
            'день недели': call_time.strftime('%A'),
            'час дня': call_time.hour
        })
    
    df = pd.DataFrame(data)
    return df


def determine_dialog_stage(duration_sec, end_reason):
    """Определяем этап диалога на основе длительности и причины завершения"""
    if end_reason == 'no_answer' or duration_sec < 3:
        return 0  # Не начался
    
    # Вероятности достижения этапов
    r = random.random()
    
    if r < 0.25:
        return 1  # Только приветствие
    elif r < 0.55:
        return 2  # Приветствие + оффер
    elif r < 0.80:
        return 3  # Приветствие + оффер + встреча
    else:
        return 4  # Все этапы


def generate_dialog_history(stage, end_reason):
    """Генерируем историю диалога в зависимости от этапа"""
    if stage == 0:
        return ""  # Нет диалога
    
    dialogs = {
        1: [
            "Бот: Здравствуйте! Могу я занимать вас две минуты?",
            "Клиент: Да, слушаю.",
            "Бот: Спасибо. Меня зовут Анна, я из компании Botamin."
        ],
        2: [
            "Бот: Здравствуйте! Могу я занимать вас две минуты?",
            "Клиент: Да, слушаю.",
            "Бот: Спасибо. Меня зовут Анна, я из компании Botamin. Мы помогаем бизнесу автоматизировать продажи.",
            "Бот: У нас есть специальное предложение для таких компаний, как ваша.",
            "Клиент: Расскажите подробнее."
        ],
        3: [
            "Бот: Здравствуйте! Могу я занимать вас две минуты?",
            "Клиент: Да, слушаю.",
            "Бот: Спасибо. Меня зовут Анна, я из компании Botamin. Мы помогаем бизнесу автоматизировать продажи.",
            "Бот: У нас есть специальное предложение для таких компаний, как ваша.",
            "Клиент: Интересно. А сколько это стоит?",
            "Бот: Давайте обсудим это на встрече. Когда вам удобно?"
        ],
        4: [
            "Бот: Здравствуйте! Могу я занимать вас две минуты?",
            "Клиент: Да, слушаю.",
            "Бот: Спасибо. Меня зовут Анна, я из компании Botamin. Мы помогаем бизнесу автоматизировать продажи.",
            "Бот: У нас есть специальное предложение для таких компаний, как ваша.",
            "Клиент: Интересно. А сколько это стоит?",
            "Бот: Давайте обсудим это на встрече. Когда вам удобно?",
            "Клиент: В среду в 15:00.",
            "Бот: Отлично! А какой у вас примерный бюджет на автоматизацию?"
        ]
    }
    
    if stage in dialogs:
        history = "\n".join(dialogs[stage])
        
        # Добавляем причину завершения
        if end_reason == 'client_hangup':
            history += "\n\nКлиент положил трубку"
        elif end_reason == 'bot_hangup':
            history += "\n\nБот завершил звонок"
        
        return history
    
    return ""


@st.cache_data
def load_and_process_data():
    """Загружаем и обрабатываем данные"""
    # Пытаемся загрузить реальные данные, если они есть
    try:
        df = pd.read_csv('botamin_calls.csv')
        st.success("Загружены реальные данные из botamin_calls.csv")
    except FileNotFoundError:
        # Генерируем синтетические данные
        df = generate_synthetic_data()
        st.info("Используются синтетические данные для демонстрации")
    
    # Обработка данных
    if 'дата и время' in df.columns:
        df['дата и время'] = pd.to_datetime(df['дата и время'])
    
    if 'длительность мин:сек' in df.columns:
        # Парсим длительность
        def parse_duration(duration_str):
            if pd.isna(duration_str):
                return 0
            try:
                parts = str(duration_str).split(':')
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
                return 0
            except:
                return 0
        
        df['длительность сек'] = df['длительность мин:сек'].apply(parse_duration)
    
    # Определяем этапы, если их нет
    if 'этап' not in df.columns:
        df['этап'] = df.apply(
            lambda row: determine_dialog_stage(row.get('длительность сек', 0), row.get('причина завершения', 'client_hangup')),
            axis=1
        )
    
    # День недели и час
    if 'дата и время' in df.columns:
        df['день недели'] = df['дата и время'].dt.day_name()
        df['час дня'] = df['дата и время'].dt.hour
    
    return df


# ============================================================================
# ОСНОВНЫЕ МЕТРИКИ
# ============================================================================

def calculate_metrics(df):
    """Считаем основные метрики"""
    total_calls = len(df)
    
    # Конверсия по этапам
    stage_counts = df['этап'].value_counts().sort_index()
    stages = [0, 1, 2, 3, 4]
    stage_conversion = {}
    
    for stage in stages:
        count = stage_counts.get(stage, 0)
        stage_conversion[stage] = count
    
    # Конверсия от общего числа
    conversion_rates = {
        'Stage 0 (No dialog)': stage_conversion[0] / total_calls * 100,
        'Stage 1 (Greeting)': stage_conversion[1] / total_calls * 100,
        'Stage 2 (Offer)': stage_conversion[2] / total_calls * 100,
        'Stage 3 (Meeting)': stage_conversion[3] / total_calls * 100,
        'Stage 4 (Qualification)': stage_conversion[4] / total_calls * 100
    }
    
    # Конверсия между этапами
    stage_transition = {
        '1→2': (stage_conversion[2] / max(stage_conversion[1], 1)) * 100,
        '2→3': (stage_conversion[3] / max(stage_conversion[2], 1)) * 100,
        '3→4': (stage_conversion[4] / max(stage_conversion[3], 1)) * 100
    }
    
    # Причины завершения
    end_reasons = df['причина завершения'].value_counts()
    
    # Средняя длительность
    avg_duration = df['длительность сек'].mean()
    median_duration = df['длительность сек'].median()
    
    # Доля успешных диалогов (дошли до этапа 4)
    success_rate = (stage_conversion[4] / total_calls) * 100
    
    # Доля диалогов без истории
    no_dialog_pct = (stage_conversion[0] / total_calls) * 100
    
    return {
        'total_calls': total_calls,
        'stage_conversion': stage_conversion,
        'conversion_rates': conversion_rates,
        'stage_transition': stage_transition,
        'end_reasons': end_reasons,
        'avg_duration': avg_duration,
        'median_duration': median_duration,
        'success_rate': success_rate,
        'no_dialog_pct': no_dialog_pct
    }


# ============================================================================
# ВИЗУАЛИЗАЦИИ
# ============================================================================

def plot_funnel_chart(metrics):
    """Строим воронку конверсии"""
    stages = ['Всего звонков', 'Этап 1: Приветствие', 'Этап 2: Оффер', 'Этап 3: Встреча', 'Этап 4: Квалификация']
    counts = [
        metrics['total_calls'],
        metrics['stage_conversion'][1],
        metrics['stage_conversion'][2],
        metrics['stage_conversion'][3],
        metrics['stage_conversion'][4]
    ]
    
    # Создаем воронку
    fig = go.Figure(go.Funnel(
        y=stages,
        x=counts,
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]),
        hovertemplate="%{y}<br>Количество: %{x}<br>Доля: %{percent initial:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title="Воронка конверсии диалогов",
        yaxis_title="Этап",
        xaxis_title="Количество диалогов",
        height=500,
        showlegend=False
    )
    
    return fig


def plot_end_reasons(metrics):
    """Строим диаграмму причин завершения"""
    end_reasons = metrics['end_reasons']
    
    fig = px.pie(
        values=end_reasons.values,
        names=end_reasons.index,
        title="Распределение причин завершения диалогов",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>Количество: %{value}<br>Доля: %{percent}<extra></extra>'
    )
    
    fig.update_layout(height=500)
    
    return fig


def plot_duration_distribution(df):
    """Строим распределение длительности диалогов"""
    # Фильтруем только диалоги с ненулевой длительностью
    df_filtered = df[df['длительность сек'] > 0]
    
    fig = px.histogram(
        df_filtered,
        x='длительность сек',
        nbins=50,
        title="Распределение длительности диалогов",
        labels={'длительность сек': 'Длительность (секунды)', 'count': 'Количество'},
        color_discrete_sequence=['#FF6B6B']
    )
    
    # Добавляем линии среднего и медианы
    avg = df_filtered['длительность сек'].mean()
    median = df_filtered['длительность сек'].median()
    
    fig.add_vline(x=avg, line_dash="dash", line_color="green", 
                  annotation_text=f"Среднее: {avg:.0f}с")
    fig.add_vline(x=median, line_dash="dash", line_color="blue", 
                  annotation_text=f"Медиана: {median:.0f}с")
    
    fig.update_layout(height=500, showlegend=False)
    
    return fig


def plot_hourly_conversion(df):
    """Строим конверсию по часам"""
    # Группируем по часу
    hourly_data = df.groupby('час дня').agg({
        'этап': lambda x: (x >= 4).sum(),  # Успешные (этап 4)
        'телефон': 'count'  # Всего
    }).reset_index()
    
    hourly_data['conversion_rate'] = (hourly_data['этап'] / hourly_data['телефон']) * 100
    
    fig = px.line(
        hourly_data,
        x='час дня',
        y='conversion_rate',
        title="Конверсия в успешные диалоги по часам дня",
        labels={'час дня': 'Час дня', 'conversion_rate': 'Конверсия (%)'},
        markers=True
    )
    
    fig.update_traces(line_color='#FF6B6B', line_width=3)
    fig.update_layout(height=500)
    
    return fig


def plot_stage_transition(metrics):
    """Строим конверсию между этапами"""
    transitions = metrics['stage_transition']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=list(transitions.keys()),
        y=list(transitions.values()),
        text=[f"{v:.1f}%" for v in transitions.values()],
        textposition='auto',
        marker=dict(color=['#4ECDC4', '#45B7D1', '#96CEB4']),
        hovertemplate='%{x}<br>Конверсия: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Конверсия между этапами диалога",
        xaxis_title="Переход",
        yaxis_title="Конверсия (%)",
        height=400,
        showlegend=False
    )
    
    return fig


def plot_daily_activity(df):
    """Строим активность по дням недели"""
    daily_data = df.groupby('день недели').size().reset_index(name='count')
    
    # Порядок дней недели
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_data['день недели'] = pd.Categorical(daily_data['день недели'], categories=day_order, ordered=True)
    daily_data = daily_data.sort_values('день недели')
    
    # Русские названия
    day_names_ru = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }
    daily_data['день недели'] = daily_data['день недели'].map(day_names_ru)
    
    fig = px.bar(
        daily_data,
        x='день недели',
        y='count',
        title="Распределение звонков по дням недели",
        labels={'день недели': 'День недели', 'count': 'Количество звонков'},
        color='count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400, showlegend=False)
    
    return fig


def plot_stage_by_end_reason(df):
    """Строим распределение этапов по причинам завершения"""
    # Группируем по причине и этапу
    stage_reason = df.groupby(['причина завершения', 'этап']).size().reset_index(name='count')
    
    fig = px.bar(
        stage_reason,
        x='причина завершения',
        y='count',
        color='этап',
        title="Распределение этапов по причинам завершения",
        labels={'count': 'Количество', 'этап': 'Этап'},
        barmode='stack',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=500)
    
    return fig


# ============================================================================
# АНАЛИЗ ТЕКСТА
# ============================================================================

def analyze_dialog_text(df):
    """Анализируем текст диалогов"""
    # Фильтруем диалоги с текстом
    df_with_text = df[df['история диалога юзер-бот'].notna() & (df['история диалога юзер-бот'] != '')]
    
    if len(df_with_text) == 0:
        return None, None, None
    
    # Собираем все тексты
    all_text = " ".join(df_with_text['история диалога юзер-бот'].astype(str))
    
    # Удаляем стоп-слова и чистим текст
    stop_words = {'бот', 'клиент', 'здравствуйте', 'спасибо', 'пожалуйста', 
                  'да', 'нет', 'хорошо', 'ладно', 'ок', 'в', 'на', 'за', 'с', 'по'}
    
    words = re.findall(r'\b[а-яА-Яa-zA-Z]{3,}\b', all_text.lower())
    words = [w for w in words if w not in stop_words]
    
    word_counts = Counter(words).most_common(20)
    
    # Создаем DataFrame для визуализации
    word_df = pd.DataFrame(word_counts, columns=['Слово', 'Частота'])
    
    # Визуализация
    fig = px.bar(
        word_df,
        x='Частота',
        y='Слово',
        orientation='h',
        title="Топ-20 самых частых слов в диалогах",
        color='Частота',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
    
    # Анализ отказов
    rejection_keywords = ['нет', 'не интересно', 'не нужно', 'не подходит', 'отказ', 'не хочу']
    rejections = []
    
    for text in df_with_text['история диалога юзер-бот']:
        text_lower = str(text).lower()
        for keyword in rejection_keywords:
            if keyword in text_lower:
                rejections.append(keyword)
                break
    
    rejection_counts = Counter(rejections)
    
    # Создаем диаграмму отказов
    if rejection_counts:
        rejection_df = pd.DataFrame(rejection_counts.most_common(), columns=['Причина', 'Частота'])
        fig_rejections = px.bar(
            rejection_df,
            x='Причина',
            y='Частота',
            title="Частые причины отказов",
            color='Частота',
            color_continuous_scale='Oranges'
        )
        fig_rejections.update_layout(height=400, showlegend=False)
    else:
        fig_rejections = None
    
    return fig, fig_rejections, word_df


# ============================================================================
# ГЛАВНЫЙ ИНТЕРФЕЙС
# ============================================================================

def main():
    """Главная функция Streamlit-приложения"""
    
    # Настройки страницы
    st.set_page_config(
        page_title="Botamin Analytics Dashboard",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Заголовок
    st.title("🤖 Botamin Analytics Dashboard")
    st.markdown("""
    **Дашборд для аналитика** - инструмент для анализа эффективности диалогов бота и поиска точек роста.
    
    *Цель: Повышать конверсию, анализируя диалоги и выявляя слабые места в скрипте бота.*
    """)
    
    # Загрузка данных
    with st.spinner("Загрузка и обработка данных..."):
        df = load_and_process_data()
        metrics = calculate_metrics(df)
    
    # Боковая панель с фильтрами
    st.sidebar.header("🔍 Фильтры")
    
    # Фильтр по дате
    if 'дата и время' in df.columns:
        date_range = st.sidebar.date_input(
            "Диапазон дат",
            value=[df['дата и время'].min().date(), df['дата и время'].max().date()],
            min_value=df['дата и время'].min().date(),
            max_value=df['дата и время'].max().date()
        )
        
        if len(date_range) == 2:
            df = df[
                (df['дата и время'].dt.date >= date_range[0]) & 
                (df['дата и время'].dt.date <= date_range[1])
            ]
            metrics = calculate_metrics(df)
    
    # Фильтр по причине завершения
    end_reasons = df['причина завершения'].unique()
    selected_reasons = st.sidebar.multiselect(
        "Причина завершения",
        options=end_reasons,
        default=end_reasons
    )
    
    if selected_reasons:
        df = df[df['причина завершения'].isin(selected_reasons)]
        metrics = calculate_metrics(df)
    
    # Фильтр по этапу
    stages = sorted(df['этап'].unique())
    selected_stages = st.sidebar.multiselect(
        "Этап диалога",
        options=stages,
        default=stages
    )
    
    if selected_stages:
        df = df[df['этап'].isin(selected_stages)]
        metrics = calculate_metrics(df)
    
    # Ключевые метрики вверху
    st.header("📊 Ключевые метрики")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Всего звонков",
            f"{metrics['total_calls']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Конверсия в этап 4",
            f"{metrics['success_rate']:.1f}%",
            delta=f"{metrics['success_rate'] - 10:.1f}%",  # Для примера
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Средняя длительность",
            f"{metrics['avg_duration']/60:.1f} мин",
            delta=None
        )
    
    with col4:
        st.metric(
            "Без диалога",
            f"{metrics['no_dialog_pct']:.1f}%",
            delta_color="inverse"
        )
    
    with col5:
        most_common_reason = metrics['end_reasons'].index[0]
        st.metric(
            "Топ причина завершения",
            most_common_reason,
            f"{metrics['end_reasons'].values[0]} звонков"
        )
    
    st.markdown("---")
    
    # Воронка конверсии
    st.header("🎯 Воронка конверсии")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        funnel_fig = plot_funnel_chart(metrics)
        st.plotly_chart(funnel_fig, use_container_width=True)
    
    with col2:
        st.markdown("### Конверсия между этапами")
        transition_fig = plot_stage_transition(metrics)
        st.plotly_chart(transition_fig, use_container_width=True)
        
        st.markdown("### Легенда этапов:")
        st.markdown("""
        - **Этап 0**: Звонок не состоялся / клиент сбросил сразу
        - **Этап 1**: Приветствие и получение согласия
        - **Этап 2**: Рассказ про оффер
        - **Этап 3**: Договоренность о встрече
        - **Этап 4**: Квалификация клиента
        """)
    
    st.markdown("---")
    
    # Причины завершения
    st.header("📞 Причины завершения диалогов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        end_reasons_fig = plot_end_reasons(metrics)
        st.plotly_chart(end_reasons_fig, use_container_width=True)
    
    with col2:
        stage_reason_fig = plot_stage_by_end_reason(df)
        st.plotly_chart(stage_reason_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Временной анализ
    st.header("⏰ Временной анализ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hourly_fig = plot_hourly_conversion(df)
        st.plotly_chart(hourly_fig, use_container_width=True)
    
    with col2:
        daily_fig = plot_daily_activity(df)
        st.plotly_chart(daily_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Анализ длительности
    st.header("⏱️ Анализ длительности диалогов")
    
    duration_fig = plot_duration_distribution(df)
    st.plotly_chart(duration_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Анализ текста
    st.header("📝 Анализ текста диалогов")
    
    with st.expander("Показать анализ текста", expanded=False):
        text_fig, rejection_fig, word_df = analyze_dialog_text(df)
        
        if text_fig:
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(text_fig, use_container_width=True)
            
            with col2:
                if rejection_fig:
                    st.plotly_chart(rejection_fig, use_container_width=True)
        
        st.markdown("""
        **Инсайты из текстового анализа:**
        - Частые слова могут указывать на темы, которые часто обсуждаются
        - Причины отказов помогают выявить слабые места в скрипте
        - Анализ ключевых фраз может показать, что именно смущает клиентов
        """)
    
    st.markdown("---")
    
    # Инсайты и рекомендации
    st.header("💡 Инсайты и рекомендации")
    
    # Определяем самую проблематичную точку
    stage_transition = metrics['stage_transition']
    weakest_point = min(stage_transition, key=stage_transition.get)
    weakest_conversion = stage_transition[weakest_point]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Выявленные проблемы")
        
        st.markdown(f"""
        **Самая слабая точка конверсии:** {weakest_point} ({weakest_conversion:.1f}%)
        
        Это означает, что бот теряет больше всего клиентов при переходе от:
        - **{weakest_point.split('→')[0]}** к **{weakest_point.split('→')[1]}**
        
        **Другие наблюдения:**
        - {metrics['no_dialog_pct']:.1f}% звонков не доходят до диалога
        - Самая частая причина завершения: **{metrics['end_reasons'].index[0]}** ({metrics['end_reasons'].values[0]} звонков)
        - Средняя длительность успешных диалогов: **{df[df['этап']==4]['длительность сек'].mean()/60:.1f} мин**
        - Средняя длительность неудачных: **{df[df['этап']<4]['длительность сек'].mean()/60:.1f} мин**
        """)
    
    with col2:
        st.subheader("🚀 Рекомендации по А/Б-тестам")
        
        if weakest_point == '1→2':
            st.markdown("""
            **Проблема:** Бот теряет клиентов после приветствия
            
            **Гипотеза:** Приветствие слишком длинное или неинтересное
            
            **А/Б-тест:**
            - **Вариант A:** Текущий скрипт приветствия
            - **Вариант B:** Более короткое иdirect приветствие
            
            **Метрика успеха:** Конверсия из этапа 1 в этап 2
            
            **Ожидаемый результат:** Повышение конверсии на 10-15%
            """)
        elif weakest_point == '2→3':
            st.markdown("""
            **Проблема:** Бот теряет клиентов при переходе к обсуждению встречи
            
            **Гипотеза:** Оффер недостаточно убедительный или нерелевантный
            
            **А/Б-тест:**
            - **Вариант A:** Текущий оффер
            - **Вариант B:** Оффер с акцентом на выгоды для клиента
            
            **Метрика успеха:** Конверсия из этапа 2 в этап 3
            
            **Ожидаемый результат:** Повышение конверсии на 15-20%
            """)
        else:  # 3→4
            st.markdown("""
            **Проблема:** Бот теряет клиентов при квалификации
            
            **Гипотеза:** Вопросы по квалификации слишком личные или сложные
            
            **А/Б-тест:**
            - **Вариант A:** Текущие вопросы по квалификации
            - **Вариант B:** Более мягкие и постепенные вопросы
            
            **Метрика успеха:** Конверсия из этапа 3 в этап 4
            
            **Ожидаемый результат:** Повышение конверсии на 10-15%
            """)
        
        st.markdown("""
        **Общие рекомендации:**
        1. Проанализировать аудиозаписи диалогов, которые завершились на слабом этапе
        2. Выявить паттерны в поведении клиентов
        3. Провести А/Б-тест с измененным скриптом
        4. Измерить impacto на общую конверсию
        """)
    
    st.markdown("---")
    
    # Дополнительная информация
    st.header("ℹ️ О дашборде")
    
    with st.expander("Как пользоваться дашбордом"):
        st.markdown("""
        ### Назначение дашборда
        
        Этот инструмент помогает аналитику:
        
        1. **Быстро оценить состояние проекта** - ключевые метрики на главной странице показывают общую картину
        2. **Найти слабые места** - воронка конверсии и анализ этапов показывают, где бот теряет клиентов
        3. **Сформулировать гипотезы** - анализ причин завершения и текста диалогов помогает понять почему
        4. **Спланировать А/Б-тесты** - рекомендации подсказывают, какие изменения стоит протестировать
        
        ### Метрики и их значение
        
        **Воронка конверсии** - показывает, сколько клиентов доходит до каждого этапа диалога. 
        Падение на каком-либо этапе указывает на проблему.
        
        **Конверсия между этапами** - показывает эффективность перехода между этапами. 
        Низкая конверсия = слабое место.
        
        **Причины завершения** - показывает, почему заканчиваются диалоги. 
        Много client_hangup? Значит клиенты не заинтересованы.
        
        **Временной анализ** - показывает, в какое время суток и дни недели конверсия выше. 
        Может помочь оптимизировать расписание звонков.
        
        **Анализ длительности** - показывает распределение диалогов по времени. 
        Короткие диалоги обычно неудачные, длинные - успешные.
        
        **Анализ текста** - помогает выявить частые темы и причины отказов.
        """)
    
    with st.expander("Методология"):
        st.markdown("""
        ### Как определяются этапы диалога
        
        В этом дашборде этапы определяются автоматически на основе:
        
        1. **Длительности диалога** - длинные диалоги обычно доходят дальше
        2. **Причины завершения** - client_hangup на ранних этапах
        3. **Анализа текста** (в реальной системе) - поиск ключевых фраз
        
        **Определение этапов:**
        - **Этап 0**: Звонок не состоялся (нет диалога)
        - **Этап 1**: Приветствие и получение согласия на разговор
        - **Этап 2**: Рассказ про оффер (предложение)
        - **Этап 3**: Договоренность о встрече
        - **Этап 4**: Квалификация клиента (вопросы по бюджету, потребностям и т.д.)
        
        ### Источники данных
        
        Дашборд может работать с:
        - Реальными данными из CSV-файла (botamin_calls.csv)
        - Синтетическими данными (для демонстрации)
        
        **Структура данных:**
        - телефон - обезличенный номер
        - дата и время - когда был звонок
        - длительность мин:сек - длительность разговора
        - статус - технический статус
        - запись аудио - ссылка на запись
        - причина завершения - кто и почему завершил
        - история диалога юзер-бот - расшифровка разговора
        """)
    
    with st.expander("Технические детали"):
        st.markdown("""
        ### Стек технологий
        
        - **Streamlit** - веб-фреймворк для создания дашбордов
        - **Pandas** - обработка данных
        - **Plotly** - интерактивные визуализации
        - **Python** - основной язык
        
        ### Как запустить
        
        ```bash
        pip install streamlit pandas plotly numpy
        streamlit run voicebot-analytics.py
        ```
        
        ### Автор
        **Исаков Сергей** | 
        Дашборд voicebot-analytics.
        """)
    
    # Подвал
    st.markdown("""
    ---
    
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>voicebot-analytics | Тестовое задание PO</p> | Автор: Исаков Сергей</p>
        <p>📊 Данных: {} диалогов | 📅 Период: {} - {}</p>
    </div>
    """.format(
        f"{len(df):,}",
        df['дата и время'].min().strftime('%d.%m.%Y'),
        df['дата и время'].max().strftime('%d.%m.%Y')
    ), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
