import pytest
import pandas as pd
from unittest.mock import patch, mock_open
from src.utils import (
load_transactions_excel,
load_json_file,
get_greeting,
get_cards_info,
top_5_transactions_by_payment_amount,
get_filtering_df_by_date,
get_currency_rates,
get_stock_price_sp500

)


# Тесты для load_transactions_excel
@pytest.mark.parametrize("file_path, mock_data, expected", [
    ("exists.xlsx", pd.DataFrame({"col": [1, 2]}), pd.DataFrame({"col": [1, 2]})),
    ("empty.xlsx", pd.DataFrame(), pd.DataFrame()),
    ("nonexistent.xlsx", FileNotFoundError(), []),
    ("corrupted.xlsx", Exception("Corrupted"), []),
])
def test_load_transactions_excel(file_path, mock_data, expected):
    with patch('pandas.read_excel') as mock_read:
        if isinstance(mock_data, Exception):
            mock_read.side_effect = mock_data
        else:
            mock_read.return_value = mock_data

        result = load_transactions_excel(file_path)
        if isinstance(expected, pd.DataFrame):
            assert len(result) == len(expected)
        else:
            assert result == expected


# Тесты для load_json_file
@pytest.mark.parametrize("file_path, mock_content, expected", [
    ("data.json", '{"key": "value"}', {"key": "value"}),
    ("empty.json", '{}', {}),
    ("nonexistent.json", FileNotFoundError(), {}),
    ("invalid.json", '{invalid}', {}),
])
def test_load_json_file(file_path, mock_content, expected):
    with patch('builtins.open') as mock_file:
        if isinstance(mock_content, Exception):
            mock_file.side_effect = mock_content
        else:
            mock_file.return_value = mock_open(read_data=mock_content).return_value

        result = load_json_file(file_path)
        assert result == expected


# Тесты для get_cards_info
@pytest.mark.parametrize("input_data, expected_count", [
    (pd.DataFrame({
        'Номер карты': ['1234567812345678', '1234567812345678'],
        'Сумма платежа': [-1000, -2000]
    }), 1),
    (pd.DataFrame({
        'Номер карты': ['1111222233334444', '5555666677778888'],
        'Сумма платежа': [-500, -1500]
    }), 2),
    (pd.DataFrame(), 0),
    (pd.DataFrame({'Номер карты': ['1234'], 'Сумма платежа': [1000]}), 0),  # только доходы
])
def test_get_cards_info(input_data, expected_count):
    result = get_cards_info(input_data)
    assert len(result) == expected_count


# Тесты для top_5_transactions_by_payment_amount
@pytest.mark.parametrize("input_data, expected_count, expected_max_amount", [
    (pd.DataFrame({
        'Дата операции': ['01.01.2024', '02.01.2024', '03.01.2024'],
        'Сумма платежа': [1000, 5000, 2000],
        'Категория': ['A', 'B', 'C'],
        'Описание': ['D1', 'D2', 'D3']
    }), 3, 5000),
    (pd.DataFrame({
        'Дата операции': [f'{i:02d}.01.2024' for i in range(1, 10)],
        'Сумма платежа': range(100, 1000, 100),
        'Категория': ['Cat'] * 9,
        'Описание': ['Desc'] * 9
    }), 5, 900),  # должен вернуть только 5 самых больших
    (pd.DataFrame(), 0, 0),
])
def test_top_5_transactions_by_payment_amount(input_data, expected_count, expected_max_amount):
    result = top_5_transactions_by_payment_amount(input_data)
    assert len(result) == expected_count
    if result:
        assert max(t['amount'] for t in result) == expected_max_amount


# Тесты для get_greeting
@pytest.mark.parametrize("hour, expected_greeting", [
    (4, "Доброе утро"),
    (11, "Доброе утро"),
    (12, "Добрый день"),
    (15, "Добрый день"),
    (18, "Добрый вечер"),
    (22, "Добрый вечер"),
    (23, "Доброй ночи"),
    (3, "Доброй ночи"),
    (0, "Доброй ночи"),
])

def test_get_greeting(hour, expected_greeting):
    with patch('src.utils.datetime') as mock_datetime:
        mock_now = mock_datetime.now.return_value
        mock_now.hour = hour
        result = get_greeting()
        assert result == expected_greeting

# Тесты для get_filtering_df_by_date
@pytest.mark.parametrize("input_data, target_date, expected_count", [
    (pd.DataFrame({
        'Дата платежа': ['01.01.2024', '15.01.2024', '01.02.2024'],
        'Сумма платежа': [100, 200, 300]
    }), '20-01-2024', 2),  # 2 транзакции в январе до 20-го
    (pd.DataFrame({
        'Дата платежа': ['01.01.2024', '31.01.2024'],
        'Сумма платежа': [100, 200]
    }), '15-01-2024', 1),  # только 1 транзакция до 15-го января
    (pd.DataFrame(), '20-01-2024', 0),
    (pd.DataFrame({
        'Дата платежа': ['01.02.2024'],
        'Сумма платежа': [100]
    }), '20-01-2024', 0),  # февральская транзакция не попадает в январь
])
def test_get_filtering_df_by_date(input_data, target_date, expected_count):
    result = get_filtering_df_by_date(input_data, target_date)
    assert len(result) == expected_count

# Тесты для get_currency_rates
@pytest.mark.parametrize("currencies, mock_response, expected_count", [
    (['USD', 'EUR'], {
        'Valute': {
            'USD': {'Value': 90.0},
            'EUR': {'Value': 100.0}
        }
    }, 2),
    (['USD'], {
        'Valute': {
            'USD': {'Value': 90.0}
        }
    }, 1),
    ([], {}, 0),
    (['INVALID'], {'Valute': {}}, 0),
])
def test_get_currency_rates(currencies, mock_response, expected_count):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        result = get_currency_rates(currencies)
        assert len(result) == expected_count


# Тесты для get_stock_price_sp500
@pytest.mark.parametrize("symbols, mock_response, expected_count", [
    (['AAPL', 'GOOGL'], {
        'Global Quote': {'05. price': '150.0'}
    }, 2),  # будет вызвано 2 раза, каждый раз вернет цену
    (['AAPL'], {
        'Global Quote': {'05. price': '150.0'}
    }, 1),
    ([], {}, 0),
    (['INVALID'], {'Global Quote': {}}, 0),
])
def test_get_stock_price_sp500(symbols, mock_response, expected_count):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        result = get_stock_price_sp500(symbols)
        assert len(result) == expected_count