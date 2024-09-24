import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import os

def save_data(df):
    df.to_csv('fiscal_data.csv', index=False)

def load_data(file=None):
    if os.path.exists('fiscal_data.csv'):
        try:
            df = pd.read_csv('fiscal_data.csv', parse_dates=['Дата последнего документа', 'Срок замены ФН'])
            st.success("Данные успешно загружены из fiscal_data.csv")
            return df
        except Exception as e:
            st.error(f"Ошибка при загрузке данных из fiscal_data.csv: {str(e)}")
    
    if file is not None:
        try:
            df = pd.read_excel(file)
            required_columns = ['Заводской номер ККТ', 'Название ККТ', 'Заводской номер ФН', 'Дата последнего документа', 'Срок замены ФН', 'КПП']
            if not all(col in df.columns for col in required_columns):
                st.error("Ошибка: В загруженном файле отсутствуют необходимые столбцы.")
                return None
            df['Дата последнего документа'] = pd.to_datetime(df['Дата последнего документа'], format='%d.%m.%Y %H:%M', errors='coerce')
            df['Срок замены ФН'] = pd.to_datetime(df['Срок замены ФН'], format='%d.%m.%Y', errors='coerce')
            save_data(df)
            st.success("Данные успешно загружены из Excel-файла и сохранены в fiscal_data.csv")
            return df
        except Exception as e:
            st.error(f"Ошибка при загрузке файла: {str(e)}")
    
    return None

def process_data(df):
    if df['Дата последнего документа'].dtype != 'datetime64[ns]':
        df['Дата последнего документа'] = pd.to_datetime(df['Дата последнего документа'], format='%d.%m.%Y %H:%M', errors='coerce')
    if df['Срок замены ФН'].dtype != 'datetime64[ns]':
        df['Срок замены ФН'] = pd.to_datetime(df['Срок замены ФН'], format='%d.%m.%Y', errors='coerce')
    
    if df['Дата последнего документа'].isna().any() or df['Срок замены ФН'].isna().any():
        st.warning("Некоторые даты не удалось распознать. Пожалуйста, проверьте формат дат в исходном файле.")
        df = df.dropna(subset=['Дата последнего документа', 'Срок замены ФН'])
    
    df['Осталось дней'] = (df['Срок замены ФН'] - pd.Timestamp.now()).dt.days
    df['Осталось дней'] = df['Осталось дней'].apply(lambda x: max(x, 0))
    
    df['Статус'] = df['Осталось дней'].apply(lambda x: 
        'Пр.' if x == 0 else 
        ('Кр.' if 1 <= x <= 7 else 
        ('Пред.' if 8 <= x <= 30 else 'Норм.')))
    
    df['Срок замены ФН'] = df['Срок замены ФН'].dt.strftime('%d.%m.%Y')
    
    # Форматирование 'Заводской номер ККТ' (13 цифр)
    df['Заводской номер ККТ'] = df['Заводской номер ККТ'].apply(lambda x: f'{int(x):013d}')
    
    # Форматирование 'КПП' (9 цифр)
    df['КПП'] = df['КПП'].apply(lambda x: f'{int(x):09d}')
    
    # Форматирование других числовых столбцов без разделителей тысяч
    df['Рег. номер ККТ'] = df['Рег. номер ККТ'].apply(lambda x: f'{int(x):016d}')
    df['Заводской номер ФН'] = df['Заводской номер ФН'].apply(lambda x: f'{int(x):016d}')
    
    return df

def update_data(update_file):
    try:
        # Load the new data from the update file
        update_df = pd.read_excel(update_file)
        
        # Check if the required columns are present
        required_columns = ['Заводской номер ККТ', 'Название ККТ', 'Заводской номер ФН', 'Дата последнего документа', 'Срок замены ФН', 'КПП']
        if not all(col in update_df.columns for col in required_columns):
            st.error("Ошибка: В загруженном файле отсутствуют необходимые столбцы.")
            return None
        
        # Convert date columns
        update_df['Дата последнего документа'] = pd.to_datetime(update_df['Дата последнего документа'], format='%d.%m.%Y %H:%M', errors='coerce')
        update_df['Срок замены ФН'] = pd.to_datetime(update_df['Срок замены ФН'], format='%d.%m.%Y', errors='coerce')
        
        # Check if any dates couldn't be parsed
        if update_df['Дата последнего документа'].isna().any() or update_df['Срок замены ФН'].isna().any():
            st.warning("Некоторые даты не удалось распознать. Эти записи будут пропущены.")
            update_df = update_df.dropna(subset=['Дата последнего документа', 'Срок замены ФН'])
        
        # Process the new data
        processed_df = process_data(update_df)
        
        # Save the new data, completely replacing the old data
        save_data(processed_df)
        
        st.success("Данные успешно обновлены и сохранены в fiscal_data.csv")
        st.info(f"Обновлено {len(processed_df)} записей.")
        
        # Update the session state
        st.session_state['df'] = processed_df
        
        return processed_df
    except Exception as e:
        st.error(f"Ошибка при обновлении данных: {str(e)}")
        return None
