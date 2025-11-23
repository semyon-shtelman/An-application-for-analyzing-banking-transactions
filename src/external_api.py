import requests


def get_currency_rates(currencies: list[str]) -> list:
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    currency_rates = []
    if not currencies:
        return []

    for currency in currencies:
        try:
            response = requests.get(url, params="USD")
            data = response.json()
            currency_rates.append(
                {"currency": currency, "rate": data.get("Valute", {}).get(currency, {}).get("Value")}
            )
        except requests.exceptions.RequestException:
            return []
    return currency_rates


def get_stock_price_sp500(symbols: list[str]) -> list:
    url = "https://www.alphavantage.co/query"

    stock_prices = []

    if not symbols:
        return []

    for symbol in symbols:
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": "YOUR_API_KEY"}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            stock_prices.append({"stock": symbol, "price": data.get("Global Quote", {}).get("05. price")})
        except requests.exceptions.RequestException:
            return []

    return stock_prices
