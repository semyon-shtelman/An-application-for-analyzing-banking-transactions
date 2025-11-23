import json

from src.external_api import get_currency_rates, get_stock_price_sp500
from src.utils import load_json_file, load_transactions_excel
from src.views import get_cards_info, get_filtering_df_by_date, get_greeting, top_5_transactions_by_payment_amount


def generate_financial_report(time_str: str) -> dict:
    """Главная функция - генерирует полный финансовый отчет"""

    # Загружаем dataframe из файла
    df = load_transactions_excel("../data/operations.xlsx")

    # Приветствие
    greeting = get_greeting()

    # фильтруем df по дате
    filtered_df_by_date = get_filtering_df_by_date(df, time_str)

    cards = get_cards_info(filtered_df_by_date)
    top_5_transactions = top_5_transactions_by_payment_amount(filtered_df_by_date)

    # Загружаем пользовательские настройки
    user_settings = load_json_file("../user_settings.json")

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    currency_rates = get_currency_rates(user_currencies)
    stock_prices = get_stock_price_sp500(user_stocks)

    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_5_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return response


test_time = "20.05.2020"
print(generate_financial_report(test_time))
