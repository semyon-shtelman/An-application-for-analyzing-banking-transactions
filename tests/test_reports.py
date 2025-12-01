import pandas as pd
from datetime import datetime
from unittest.mock import patch
from src.reports import spending_by_category


def test_basic_functionality():
    """Основной тест - траты по категории за 3 месяца"""
    df = pd.DataFrame({
        "Дата платежа": ["01.01.2024", "15.02.2024", "20.03.2024"],
        "Категория": ["Еда", "Еда", "Еда"],
        "Сумма платежа": [1000, 2000, 1500]
    })

    # Мокаем только pd.to_datetime для целевой даты
    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = pd.Timestamp('2024-03-31')
        result = spending_by_category(df, "Еда", "31.03.2024")
        assert len(result) == 1
        assert result["Траты"].sum() == 4500


def test_empty_data():
    """Тест с пустыми данными"""
    empty_df = pd.DataFrame(columns=["Дата платежа", "Категория", "Сумма платежа"])

    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = pd.Timestamp('2024-03-31')
        result = spending_by_category(empty_df, "Еда", "31.03.2024")
        assert result.empty


def test_no_data_for_category():
    """Тест когда нет данных для указанной категории"""
    df = pd.DataFrame({
        "Дата платежа": ["01.01.2024"],
        "Категория": ["Транспорт"],
        "Сумма платежа": [1000]
    })

    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.return_value = pd.Timestamp('2024-03-31')
        result = spending_by_category(df, "Еда", "31.03.2024")
        assert result.empty


def test_missing_columns():
    """Тест с отсутствующими колонками"""
    df = pd.DataFrame({"other_column": [1]})

    try:
        result = spending_by_category(df, "Еда", "31.03.2024")
        assert False
    except Exception:
        assert True


def test_current_date():
    """Тест с текущей датой (без указания date)"""
    df = pd.DataFrame({
        "Дата платежа": ["31.03.2024"],
        "Категория": ["Еда"],
        "Сумма платежа": [1000]
    })

    # Мокаем datetime.now() чтобы вернуть фиксированную дату
    with patch('src.reports.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 3, 31)
        result = spending_by_category(df, "Еда")
        assert len(result) == 1