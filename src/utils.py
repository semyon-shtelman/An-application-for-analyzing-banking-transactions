import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def load_transactions_excel(excel_file_patch: str) -> pd.DataFrame | list:
    """Загружает транзакции из Excel файла"""
    logger.info(f"Начало загрузки файла: {excel_file_patch}")
    try:
        df = pd.read_excel(excel_file_patch)
        logger.info(f"Файл успешно загружен. Записей: {len(df)}")
        return df
    except FileNotFoundError:
        logger.error(f"Файл не найден: {excel_file_patch}")
        return []
    except Exception as e:
        logger.error(f"Ошибка чтения Excel файла: {e}")
        return []


def load_json_file(json_file_patch: str) -> dict:
    """Загружает JSON файл"""
    logger.info(f"Загрузка JSON файла: {json_file_patch}")
    try:
        with open(json_file_patch, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            logger.info(f"JSON файл успешно загружен. Ключи: {list(data.keys())}")
            return data
    except FileNotFoundError:
        logger.error(f"JSON файл не найден: {json_file_patch}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки JSON файла: {e}")
        return {}


def get_cards_info(df: pd.DataFrame) -> list[dict]:
    """По каждой карте: последние 4 цифры карты; общая сумма расходов; кешбэк"""
    logger.info("Начало расчета информации по картам")

    if df.empty:
        logger.warning("DataFrame пуст для расчета информации по картам")
        return []

    transactions = df[df["Сумма платежа"] < 0]

    if transactions.empty:
        logger.info("Нет транзакций с отрицательной суммой (расходов)")
        return []


    try:
        cards_info = []

        for card_number, group in transactions.groupby("Номер карты"):
            total_spent = abs(group["Сумма платежа"].sum())
            total_spent_rounded = round(total_spent, 2)
            cashback = round(total_spent / 100, 2)

            cards_info.append({
                "last_digits": card_number,
                "total_spent": total_spent_rounded,
                "cashback": cashback
            })
        logger.info(f"Рассчитана информация по {len(cards_info)} картам")
        return cards_info
    except Exception as e:
        logger.error(f"Ошибка при расчете информации по картам: {e}")
        return []


def top_5_transactions_by_payment_amount(df: pd.DataFrame) -> list[dict]:
    """Получаем топ-5 транзакций по сумме платежа."""
    logger.info("Начало формирования топ-5 транзакций")

    if df.empty:
        logger.warning("DataFrame пуст для формирования топ-5 транзакций")
        return []

    try:
        transactions = df.sort_values(by="Сумма платежа", key=abs, ascending=False).head(5)
        transactions_dict = transactions.to_dict(orient="records")

        top_transaction = []
        for transaction in transactions_dict:
            top_transaction.append(
                {
                    "date": transaction.get("Дата операции"),
                    "amount": transaction.get("Сумма платежа"),
                    "category": transaction.get("Категория"),
                    "description": transaction.get("Описание"),
                },
            )
        logger.info(f"Сформирован топ-5 транзакций. Суммы: {[t['amount'] for t in top_transaction]}")
        return top_transaction
    except Exception as e:
        logger.error(f"Ошибка при формировании топ-5 транзакций: {e}")
        return []


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от времени"""
    hour = datetime.now().hour
    logger.info(f"Текущий час: {hour}")

    if 4 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    elif 18 <= hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    logger.info(f"Сгенерировано приветствие: '{greeting}'")
    return greeting


def get_filtering_df_by_date(df: pd.DataFrame, target_date: str) -> pd.DataFrame:
    """Фильтрует данные с начала месяца, на который выпадает входящая дата, по входящую дату."""
    logger.info(f"Фильтрация данных по дате: {target_date}")

    if df.empty:
        logger.warning("DataFrame пуст для фильтрации по дате")
        return df

    try:
        date_dt = pd.to_datetime(target_date, format="%Y-%m-%d %H:%M:%S")
        start_of_month = date_dt.replace(day=1)

        df_dates = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y")
        filtered_df = df[df_dates.between(start_of_month, date_dt)]
        logger.info(f"Данные отфильтрованы. Записей до: {len(df)}, после: {len(filtered_df)}")
        return filtered_df
    except Exception as e:
        logger.error(f"Ошибка при фильтрации данных по дате: {e}")
        return pd.DataFrame()


def get_currency_rates(currencies: list[str]) -> list:
    """Получает курсы валют с ЦБ РФ"""
    logger.info(f"Запрос курсов валют: {currencies}")

    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    currency_rates = []

    if not currencies:
        logger.info("Список валют пуст")
        return []

    for currency in currencies:
        try:
            logger.debug(f"Запрос курса для валюты: {currency}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            rate = data.get("Valute", {}).get(currency, {}).get("Value")
            if rate:
                currency_rates.append({"currency": currency, "rate": round(float(rate), 2)})
                logger.debug(f"Получен курс для {currency}: {rate}")
            else:
                logger.warning(f"Курс для валюты {currency} не найден в ответе")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса курса валюты {currency}: {e}")
            continue
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении курса {currency}: {e}")
            continue

    logger.info(f"Получены курсы для {len(currency_rates)} валют из {len(currencies)} запрошенных")
    return currency_rates


def get_stock_price_sp500(symbols: list[str]) -> list:
    """Получает цены акций из S&P500"""
    logger.info(f"Запрос цен акций: {symbols}")

    api_key = os.getenv("API_KEY")
    url = "https://www.alphavantage.co/query"
    stock_prices = []

    if not symbols:
        logger.info("Список акций пуст")
        return []

    for symbol in symbols:
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}
        try:
            logger.debug(f"Запрос цены для акции: {symbol}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            price = data.get("Global Quote", {}).get("05. price")
            if price:
                stock_prices.append({"stock": symbol, "price": round(float(price), 2)})
                logger.debug(f"Получена цена для {symbol}: {price}")
            else:
                logger.warning(f"Цена для акции {symbol} не найдена в ответе")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса цены акции {symbol}: {e}")
            continue
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении цены акции {symbol}: {e}")
            continue

    logger.info(f"Получены цены для {len(stock_prices)} акций из {len(symbols)} запрошенных")
    return stock_prices
