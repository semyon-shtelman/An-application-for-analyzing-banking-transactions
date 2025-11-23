from datetime import datetime

import pandas as pd


def get_cards_info(df: pd.DataFrame) -> list[dict]:
    """По каждой карте: последние 4 цифры карты;
    общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей)."""
    if df.empty:
        return []

    transactions = df[df["Сумма платежа"] < 0]

    if transactions.empty:
        return []

    cards = transactions.groupby(by="Номер карты").agg(
        last_digits=("Номер карты", lambda x: str(x.iloc[0])[-4:]),
        total_digits=("Сумма платежа", lambda x: round(abs(sum(x)), 2)),
        cashback=("Сумма платежа", lambda x: abs(sum(x) // 100)),
    )
    cards_dict = cards.to_dict(orient="records")
    return cards_dict


def top_5_transactions_by_payment_amount(df: pd.DataFrame) -> list[dict]:
    """Получаем топ-5 транзакций по сумме платежа."""
    if df.empty:
        return []

    transactions = df.sort_values(by="Сумма платежа", key=abs, ascending=False).head(5)
    transactions = transactions.to_dict(orient="records")

    top_transaction = []
    for transaction in transactions:
        top_transaction.append(
            {
                "date": transaction.get("Дата операции"),
                "amount": transaction.get("Сумма платежа"),
                "category": transaction.get("Категория"),
                "description": transaction.get("Описание"),
            },
        )
    return top_transaction


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от времени"""

    hour = datetime.now().hour

    if 4 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_filtering_df_by_date(df: pd.DataFrame, target_date: str) -> pd.DataFrame:
    """Фильтрует данные с начала месяца, на который выпадает входящая дата, по входящую дату."""

    date_dt = pd.to_datetime(target_date, format="%d.%m.%Y")
    start_of_month = date_dt.replace(day=1)

    filtered_df = df[pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y").between(start_of_month, date_dt)]
    return filtered_df
