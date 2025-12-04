import pandas as pd
from unittest.mock import patch
from src.services import anylize_cashback
import pytest


@pytest.fixture
def basic_cashback_df():
    """Фикстура с базовыми данными по кэшбэку"""
    return pd.DataFrame({
        "Дата платежа": ["01.01.2025", "15.01.2025", "20.01.2025"],
        "Категория": ["Еда", "Транспорт", "Еда"],
        "Кэшбэк": [100, 150, 50]
    })


@pytest.fixture
def basic_cashback_dates():
    """Фикстура с соответствующими датами для базового DataFrame"""
    return pd.Series([
        pd.Timestamp('2025-01-01'),
        pd.Timestamp('2025-01-15'),
        pd.Timestamp('2025-01-20')
    ])


@pytest.fixture
def empty_cashback_df():
    """Фикстура с пустыми данными"""
    return pd.DataFrame(columns=["Дата платежа", "Категория", "Кэшбэк"])


@pytest.fixture
def empty_cashback_dates():
    """Фикстура с пустыми датами"""
    return pd.Series([])


@pytest.fixture
def old_data_cashback_df():
    """Фикстура с данными за старый период"""
    return pd.DataFrame({
        "Дата платежа": ["01.01.2023"],
        "Категория": ["Еда"],
        "Кэшбэк": [100]
    })


@pytest.fixture
def old_data_cashback_dates():
    """Фикстура с датами за старый период"""
    return pd.Series([pd.Timestamp('2023-01-01')])


def test_anylize_cashback_basic_functionality(
    basic_cashback_df, basic_cashback_dates
):
    """Основной тест - несколько категорий за указанный месяц"""
    with patch('pandas.to_datetime') as mock_to_datetime:
        # Мокаем преобразование дат
        mock_to_datetime.return_value = basic_cashback_dates

        result = anylize_cashback(basic_cashback_df, 2025, 1)
        assert result == {"Транспорт": 150.0, "Еда": 150.0}


def test_anylize_cashback_empty_data(
    empty_cashback_df, empty_cashback_dates
):
    """Тест с пустыми данными"""
    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = empty_cashback_dates

        result = anylize_cashback(empty_cashback_df, 2025, 1)
        assert result == {}


def test_anylize_cashback_no_data_for_period(
    old_data_cashback_df, old_data_cashback_dates
):
    """Тест когда нет данных за указанный период"""
    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = old_data_cashback_dates

        result = anylize_cashback(old_data_cashback_df, 2024, 1)
        assert result == {}


def test_anylize_cashback_missing_columns():
    """Тест с отсутствующими колонками"""
    df = pd.DataFrame({"other_column": [1]})

    # Мокаем pd.to_datetime чтобы проверить обработку ошибок
    with patch('pandas.to_datetime') as mock_to_datetime:
        # Симулируем KeyError при отсутствии колонки
        mock_to_datetime.side_effect = KeyError("Column not found")

        result = anylize_cashback(df, 2024, 1)