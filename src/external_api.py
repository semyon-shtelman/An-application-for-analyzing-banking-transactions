import requests
import json

def get_currency_rate(currencies):
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    currency_rates = []
    if not currencies:
        return []

    for currency in currencies:
        try:
            response = requests.get(url, params='USD')
            data = response.json()
            currency_rates.append({
                "currency": currency,
                "rate": data.get("Valute", {}).get(currency, {}).get("Value", 0)
            })
        except requests.exceptions.RequestException:
            return []
    return json.dumps(currency_rates, indent=4)


def get_stock_price_sp500(symbols):
    url = "https://www.alphavantage.co/query"

    stock_prices = []

    if not symbols:
        return []

    for symbol in symbols:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": "YOUR_API_KEY"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            stock_prices.append({
                "stock": symbol,
                "price": data.get("Global Quote", {}).get("05. price", 0)
            })
        except requests.exceptions.RequestException:
            return []

    return stock_prices

print(get_currency_rate([]))