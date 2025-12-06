import pytest
import pandas as pd
import json
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


# Фикстуры для тестов load_transactions_excel
@pytest.fixture
def simple_excel_data():
    """Фикстура с простыми данными Excel"""
    return pd.DataFrame({"col": [1, 2]})


@pytest.fixture
def empty_excel_data():
    """Фикстура с пустыми данными Excel"""
    return pd.DataFrame()


@pytest.fixture
def file_not_found_error():
    """Фикстура с ошибкой FileNotFoundError"""
    return FileNotFoundError()


@pytest.fixture
def corrupted_file_error():
    """Фикстура с ошибкой corrupted file"""
    return Exception("Corrupted")


# Фикстуры для тестов load_json_file
@pytest.fixture
def valid_json_content():
    """Фикстура с валидным JSON содержимым"""
    return '{"key": "value"}'


@pytest.fixture
def empty_json_content():
    """Фикстура с пустым JSON содержимым"""
    return '{}'


@pytest.fixture
def invalid_json_content():
    """Фикстура с невалидным JSON содержимым"""
    return '{invalid}'


# Фикстуры для тестов get_cards_info
@pytest.fixture
def single_card_df():
    """Фикстура с данными одной карты"""
    return pd.DataFrame({
        'Номер карты': ['1234567812345678', '1234567812345678'],
        'Сумма платежа': [-1000, -2000]
    })


@pytest.fixture
def multiple_cards_df():
    """Фикстура с данными нескольких карт"""
    return pd.DataFrame({
        'Номер карты': ['1111222233334444', '5555666677778888'],
        'Сумма платежа': [-500, -1500]
    })


@pytest.fixture
def empty_df():
    """Фикстура с пустым DataFrame"""
    return pd.DataFrame()


@pytest.fixture
def only_income_df():
    """Фикстура только с доходами"""
    return pd.DataFrame({
        'Номер карты': ['1234'],
        'Сумма платежа': [1000]
    })


# Фикстуры для тестов top_5_transactions_by_payment_amount
@pytest.fixture
def three_transactions_df():
    """Фикстура с тремя транзакциями"""
    return pd.DataFrame({
        'Дата операции': ['01.01.2024', '02.01.2024', '03.01.2024'],
        'Сумма платежа': [1000, 5000, 2000],
        'Категория': ['A', 'B', 'C'],
        'Описание': ['D1', 'D2', 'D3']
    })


@pytest.fixture
def nine_transactions_df():
    """Фикстура с девятью транзакциями (должен вернуть топ-5)"""
    return pd.DataFrame({
        'Дата операции': [f'{i:02d}.01.2024' for i in range(1, 10)],
        'Сумма платежа': range(100, 1000, 100),
        'Категория': ['Cat'] * 9,
        'Описание': ['Desc'] * 9
    })


# Фикстуры для тестов get_filtering_df_by_date
@pytest.fixture
def mixed_dates_df():
    """Фикстура с датами из разных месяцев"""
    return pd.DataFrame({
        'Дата платежа': ['01.01.2024', '15.01.2024', '01.02.2024'],
        'Сумма платежа': [100, 200, 300]
    })


@pytest.fixture
def january_dates_df():
    """Фикстура с датами января"""
    return pd.DataFrame({
        'Дата платежа': ['01.01.2024', '31.01.2024'],
        'Сумма платежа': [100, 200]
    })


@pytest.fixture
def february_dates_df():
    """Фикстура с датами февраля"""
    return pd.DataFrame({
        'Дата платежа': ['01.02.2024'],
        'Сумма платежа': [100]
    })


# Фикстуры для тестов get_currency_rates
@pytest.fixture
def usd_eur_rates_response():
    """Фикстура с ответом API для USD и EUR"""
    return {
        'Valute': {
            'USD': {'Value': 90.0},
            'EUR': {'Value': 100.0}
        }
    }


@pytest.fixture
def usd_rate_response():
    """Фикстура с ответом API только для USD"""
    return {
        'Valute': {
            'USD': {'Value': 90.0}
        }
    }


@pytest.fixture
def empty_rates_response():
    """Фикстура с пустым ответом API"""
    return {}


@pytest.fixture
def no_valute_response():
    """Фикстура с ответом API без валют"""
    return {'Valute': {}}


# Фикстуры для тестов get_stock_price_sp500
@pytest.fixture
def stock_price_response():
    """Фикстура с ответом API для акций"""
    return {
        'Global Quote': {'05. price': '150.0'}
    }


@pytest.fixture
def empty_stock_response():
    """Фикстура с пустым ответом API для акций"""
    return {}


@pytest.fixture
def no_quote_response():
    """Фикстура с ответом API без котировок"""
    return {'Global Quote': {}}


# Тесты для load_transactions_excel
@pytest.mark.parametrize("file_path, mock_data, expected", [
    ("exists.xlsx", "simple_excel_data", pd.DataFrame({"col": [1, 2]})),
    ("empty.xlsx", "empty_excel_data", pd.DataFrame()),
    ("nonexistent.xlsx", "file_not_found_error", []),
    ("corrupted.xlsx", "corrupted_file_error", []),
])
def test_load_transactions_excel(file_path, mock_data, expected, request):
    data_fixture = request.getfixturevalue(mock_data)

    with patch('pandas.read_excel') as mock_read:
        if isinstance(data_fixture, Exception):
            mock_read.side_effect = data_fixture
        else:
            mock_read.return_value = data_fixture

        result = load_transactions_excel(file_path)
        if isinstance(expected, pd.DataFrame):
            assert len(result) == len(expected)
        else:
            assert result == expected


# Тесты для load_json_file
@pytest.mark.parametrize("file_path, mock_content, expected", [
    ("data.json", "valid_json_content", {"key": "value"}),
    ("empty.json", "empty_json_content", {}),
    ("nonexistent.json", "file_not_found_error", {}),
    ("invalid.json", "invalid_json_content", {}),
])
def test_load_json_file(file_path, mock_content, expected, request):
    content_fixture = request.getfixturevalue(mock_content)

    with patch('builtins.open') as mock_file:
        if isinstance(content_fixture, Exception):
            mock_file.side_effect = content_fixture
        else:
            mock_file.return_value = mock_open(read_data=content_fixture).return_value

        result = load_json_file(file_path)
        assert result == expected


# Тесты для get_cards_info
@pytest.mark.parametrize("input_data, expected_count", [
    ("single_card_df", 1),
    ("multiple_cards_df", 2),
    ("empty_df", 0),
    ("only_income_df", 0),
])
def test_get_cards_info(input_data, expected_count, request):
    df_fixture = request.getfixturevalue(input_data)
    result = get_cards_info(df_fixture)
    assert len(result) == expected_count


# Тесты для top_5_transactions_by_payment_amount
@pytest.mark.parametrize("input_data, expected_count, expected_max_amount", [
    ("three_transactions_df", 3, 5000),
    ("nine_transactions_df", 5, 900),
    ("empty_df", 0, 0),
])
def test_top_5_transactions_by_payment_amount(input_data, expected_count, expected_max_amount, request):
    df_fixture = request.getfixturevalue(input_data)
    result = top_5_transactions_by_payment_amount(df_fixture)
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
    ("mixed_dates_df", '2024-01-20 00:00:00', 2),
    ("january_dates_df", '2024-01-15 00:00:00', 1),
    ("empty_df", '2024-01-20 00:00:00', 0),
    ("february_dates_df", '2024-01-20 00:00:00', 0),
])
def test_get_filtering_df_by_date(input_data, target_date, expected_count, request):
    df_fixture = request.getfixturevalue(input_data)
    result = get_filtering_df_by_date(df_fixture, target_date)
    assert len(result) == expected_count


# Тесты для get_currency_rates
@pytest.mark.parametrize("currencies, mock_response, expected_count", [
    (['USD', 'EUR'], "usd_eur_rates_response", 2),
    (['USD'], "usd_rate_response", 1),
    ([], "empty_rates_response", 0),
    (['INVALID'], "no_valute_response", 0),
])
def test_get_currency_rates(currencies, mock_response, expected_count, request):
    response_fixture = request.getfixturevalue(mock_response)

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = response_fixture
        mock_get.return_value.raise_for_status.return_value = None

        result = get_currency_rates(currencies)
        assert len(result) == expected_count


# Тесты для get_stock_price_sp500
@pytest.mark.parametrize("symbols, mock_response, expected_count", [
    (['AAPL', 'GOOGL'], "stock_price_response", 2),
    (['AAPL'], "stock_price_response", 1),
    ([], "empty_stock_response", 0),
    (['INVALID'], "no_quote_response", 0),
])
def test_get_stock_price_sp500(symbols, mock_response, expected_count, request):
    response_fixture = request.getfixturevalue(mock_response)

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = response_fixture
        mock_get.return_value.raise_for_status.return_value = None

        result = get_stock_price_sp500(symbols)
        assert len(result) == expected_count