import pandas as pd
from unittest.mock import patch
from src.services import anylize_cashback


def test_anylize_cashback_basic_functionality():
    """Основной тест - несколько категорий за указанный месяц"""
    df = pd.DataFrame({
        "Дата платежа": ["01.01.2025", "15.01.2025", "20.01.2025"],
        "Категория": ["Еда", "Транспорт", "Еда"],
        "Кэшбэк": [100, 150, 50]
    })

    with patch('pandas.to_datetime') as mock_to_datetime:
        # Мокаем преобразование дат
        mock_to_datetime.return_value = pd.Series([
            pd.Timestamp('2025-01-01'),
            pd.Timestamp('2025-01-15'),
            pd.Timestamp('2025-01-20')
        ])

        result = anylize_cashback(df, 2025, 1)
        assert result == {"Транспорт": 150.0, "Еда": 150.0}


def test_anylize_cashback_empty_data():
    """Тест с пустыми данными"""
    empty_df = pd.DataFrame(columns=["Дата платежа", "Категория", "Кэшбэк"])

    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = pd.Series([])

        result = anylize_cashback(empty_df, 2025, 1)
        assert result == {}


def test_anylize_cashback_no_data_for_period():
    """Тест когда нет данных за указанный период"""
    df = pd.DataFrame({
        "Дата платежа": ["01.01.2023"],
        "Категория": ["Еда"],
        "Кэшбэк": [100]
    })

    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = pd.Series([pd.Timestamp('2023-01-01')])

        result = anylize_cashback(df, 2024, 1)
        assert result == {}


def test_anylize_cashback_missing_columns():
    """Тест с отсутствующими колонками"""
    df = pd.DataFrame({"other_column": [1]})

    # Мокаем pd.to_datetime чтобы проверить обработку ошибок
    with patch('pandas.to_datetime') as mock_to_datetime:
        # Симулируем KeyError при отсутствии колонки
        mock_to_datetime.side_effect = KeyError("Column not found")

        result = anylize_cashback(df, 2024, 1)
        assert result == {}