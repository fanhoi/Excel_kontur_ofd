import streamlit as st
import pandas as pd
from data_processor import load_data, process_data, update_data
from visualizer import create_expiration_chart
from datetime import datetime
import io

st.set_page_config(page_title="Мониторинг фискальных накопителей", layout="wide")

def main():
    if 'df' not in st.session_state:
        st.session_state['df'] = None

    st.title("Мониторинг сроков истечения фискальных накопителей")

    # Загрузка данных
    if st.session_state['df'] is None:
        st.session_state['df'] = load_data()

    if st.session_state['df'] is None:
        st.warning("Данные не найдены. Пожалуйста, загрузите файл Excel с данными о фискальных накопителях.")
        uploaded_file = st.file_uploader("Загрузите файл Excel с данными о фискальных накопителях", type=["xlsx"])
        if uploaded_file is not None:
            st.session_state['df'] = load_data(uploaded_file)

    if st.session_state['df'] is not None:
        # Обработка данных
        df_processed = process_data(st.session_state['df'])

        # Отображение данных
        st.subheader("Данные о фискальных накопителях")
        
        # Добавляем фильтры
        st.sidebar.header("Фильтры")
        statuses = st.sidebar.multiselect("Выберите статусы", options=df_processed['Статус'].unique(), default=df_processed['Статус'].unique())
        
        # Обновляем порядок колонок и настройки по умолчанию
        st.sidebar.header("Выбор колонок")
        columns = ['Название ККТ', 'Заводской номер ККТ', 'Рег. номер ККТ', 'Заводской номер ФН', 'КПП', 'Модель ККТ', 'ФФД', 'Оплата', 'Срок замены ФН', 'Осталось дней', 'Статус']
        default_columns = ['Название ККТ', 'Осталось дней', 'Статус']
        selected_columns = []
        for col in columns:
            if st.sidebar.checkbox(col, value=col in default_columns):
                selected_columns.append(col)
        
        # Применяем фильтры
        filtered_df = df_processed[df_processed['Статус'].isin(statuses)]
        
        # Отображаем отфильтрованные данные с правильной нумерацией и выбранными колонками
        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df.index = filtered_df.index + 1  # Начинаем нумерацию с 1
        st.dataframe(filtered_df[selected_columns], use_container_width=True)

        # Создание и отображение графика
        st.subheader("Сроки истечения фискальных накопителей")
        fig_bar = create_expiration_chart(filtered_df)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Обновление данных
        st.subheader("Обновление данных")
        update_file = st.file_uploader("Загрузите файл Excel с обновленными данными", type=["xlsx"])
        if st.button("Обновить данные"):
            if update_file is not None:
                updated_df = update_data(update_file)
                if updated_df is not None:
                    st.success("Данные успешно обновлены!")
                    st.session_state['df'] = updated_df  # Replace current DataFrame with updated one

                    # Экспорт обновленных данных
                    csv = updated_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Скачать обновленные данные (CSV)",
                        data=csv,
                        file_name=f"updated_fiscal_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                    )
                    st.rerun()  # Rerun the app to update displayed data and chart
            else:
                st.warning("Пожалуйста, загрузите файл Excel для обновления данных.")

    st.sidebar.info("Это приложение помогает отслеживать сроки истечения фискальных накопителей.")

if __name__ == "__main__":
    main()
