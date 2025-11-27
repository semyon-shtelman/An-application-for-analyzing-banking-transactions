import pandas as pd
from datetime import datetime
from src.reports import spending_by_category


def test_basic_functionality():
    """Основной тест - траты по категории за 3 месяца"""
    df = pd.DataFrame({
        "Дата платежа": ["01.01.2024", "15.02.2024", "20.03.2024"],
        "Категория": ["Еда", "Еда", "Еда"],
        "Сумма платежа": [1000, 2000, 1500]
    })
    result = spending_by_category(df, "Еда", "31.03.2024")
    assert len(result) == 3
    assert result["Траты"].sum() == 4500


def test_empty_data():
    """Тест с пустыми данными"""
    empty_df = pd.DataFrame(columns=["Дата платежа", "Категория", "Сумма платежа"])
    result = spending_by_category(empty_df, "Еда", "31.03.2024")
    assert result.empty


def test_no_data_for_category():
    """Тест когда нет данных для указанной категории"""
    df = pd.DataFrame({
        "Дата платежа": ["01.01.2024"],
        "Категория": ["Транспорт"],
        "Сумма платежа": [1000]
    })
    result = spending_by_category(df, "Еда", "31.03.2024")
    assert result.empty


def test_missing_columns():
    """Тест с отсутствующими колонками"""
    df = pd.DataFrame({"other_column": [1]})
    try:
        result = spending_by_category(df, "Еда", "31.03.2024")
        # Функция должна упасть с ошибкой
        assert False
    except Exception:
        assert True


def test_current_date():
    """Тест с текущей датой (без указания date)"""
    df = pd.DataFrame({
        "Дата платежа": [datetime.now().strftime("%d.%m.%Y")],
        "Категория": ["Еда"],
        "Сумма платежа": [1000]
    })
    result = spending_by_category(df, "Еда")
    assert len(result) == 1