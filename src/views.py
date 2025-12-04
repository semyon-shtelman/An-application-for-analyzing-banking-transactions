import json
from typing import Any

from src.utils import (get_cards_info, get_currency_rates, get_filtering_df_by_date, get_greeting,
                       get_stock_price_sp500, load_json_file, load_transactions_excel,
                       top_5_transactions_by_payment_amount)


def generate_main_response(time_str: str) -> str:
    """Главная функция - для генерации данных для страницы главная"""

    # Загружаем dataframe из файла
    df = load_transactions_excel("../data/operations.xlsx")

    # 1. Приветствие
    greeting = get_greeting()

    # фильтруем df по дате
    filtered_df_by_date = get_filtering_df_by_date(df, time_str)

    # 2. По каждой карте
    cards = get_cards_info(filtered_df_by_date)

    # 3. Топ-5 транзакций по сумме платежа.
    top_5_transactions = top_5_transactions_by_payment_amount(filtered_df_by_date)

    # Загружаем пользовательские настройки
    user_settings = load_json_file("../user_settings.json")

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    # 4. Курс валют.
    currency_rates = get_currency_rates(user_currencies)

    # 5. Стоимость акций из S&P500
    stock_prices = get_stock_price_sp500(user_stocks)

    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_5_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(response, ensure_ascii=False, indent=4)
