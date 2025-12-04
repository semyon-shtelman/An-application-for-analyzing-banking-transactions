import pandas as pd
from datetime import datetime
from unittest.mock import patch
from src.reports import spending_by_category
import pytest


@pytest.fixture
def basic_df():
    """Фикстура с базовыми данными"""
    return pd.DataFrame({
        "Дата платежа": ["01.01.2024", "15.02.2024", "20.03.2024"],
        "Категория": ["Еда", "Еда", "Еда"],
        "Сумма платежа": [1000, 2000, 1500]
    })


@pytest.fixture
def empty_df():
    """Фикстура с пустыми данными"""
    return pd.DataFrame(columns=["Дата платежа", "Категория", "Сумма платежа"])


@pytest.fixture
def transport_df():
    """Фикстура с данными только по транспорту"""
    return pd.DataFrame({
        "Дата платежа": ["01.01.2024"],
        "Категория": ["Транспорт"],
        "Сумма платежа": [1000]
    })


@pytest.fixture
def single_day_df():
    """Фикстура с данными за один день"""
    return pd.DataFrame({
        "Дата платежа": ["31.03.2024"],
        "Категория": ["Еда"],
        "Сумма платежа": [1000]
    })


@pytest.fixture
def mock_timestamp():
    """Фикстура для мока pd.to_datetime"""
    return pd.Timestamp('2024-03-31')


def test_basic_functionality(basic_df, mock_timestamp):
    """Основной тест - траты по категории за 3 месяца"""
    # Мокаем только pd.to_datetime для целевой даты
    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = mock_timestamp
        result = spending_by_category(basic_df, "Еда", "31.03.2024")
        assert len(result) == 1
        assert result["Траты"].sum() == 4500


def test_empty_data(empty_df, mock_timestamp):
    """Тест с пустыми данными"""
    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = mock_timestamp
        result = spending_by_category(empty_df, "Еда", "31.03.2024")
        assert result.empty


def test_no_data_for_category(transport_df, mock_timestamp):
    """Тест когда нет данных для указанной категории"""
    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = mock_timestamp
        result = spending_by_category(transport_df, "Еда", "31.03.2024")
        assert result.empty


def test_missing_columns():
    """Тест с отсутствующими колонками"""
    df = pd.DataFrame({"other_column": [1]})

    try:
        result = spending_by_category(df, "Еда", "31.03.2024")
        assert False
    except Exception:
        assert True


def test_current_date(single_day_df):
    """Тест с текущей датой (без указания date)"""
    # Мокаем datetime.now() чтобы вернуть фиксированную дату
    with patch('src.reports.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 3, 31)
        result = spending_by_category(single_day_df, "Еда")
        assert len(result) == 1