import utils


def generate_main_response(time_str: str) -> dict:
    """Главная функция - для генерации данных для страницы главная"""

    # Загружаем dataframe из файла
    df = utils.load_transactions_excel("../data/operations.xlsx")

    # Приветствие
    greeting = utils.get_greeting()

    # фильтруем df по дате
    filtered_df_by_date = utils.get_filtering_df_by_date(df, time_str)

    cards = utils.get_cards_info(filtered_df_by_date)
    top_5_transactions = utils.top_5_transactions_by_payment_amount(filtered_df_by_date)

    # Загружаем пользовательские настройки
    user_settings = utils.load_json_file("../user_settings.json")

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    currency_rates = utils.get_currency_rates(user_currencies)
    stock_prices = utils.get_stock_price_sp500(user_stocks)

    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_5_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return response
