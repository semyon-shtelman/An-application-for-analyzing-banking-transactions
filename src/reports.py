import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца"""
    logger.info(f"Начало обработки категории '{category}'")
    logger.debug(f"Размер входных данных: {len(transactions)} строк")

    if date is None:
        target_date = datetime.now()
        logger.info(f"Дата не указана, используется текущая дата: {target_date}")
    else:
        target_date = pd.to_datetime(date)
        logger.info(f"Используется указанная дата: {target_date}")

    df = transactions.copy()
    logger.debug("Создана копия DataFrame")

    # Преобразование даты
    try:
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
        logger.debug("Даты платежа успешно преобразованы")
    except Exception as e:
        logger.error(f"Ошибка при преобразовании дат: {e}")
        raise

    # Расчет начальной даты
    start_date = target_date - timedelta(days=90)
    start_date = start_date.replace(day=1)
    logger.info(f"Период анализа: с {start_date.date()} по {target_date.date()}")

    # Фильтрация данных
    initial_count = len(df)
    filtered_data = df[
        (df["Категория"] == category) & (df["Дата платежа"] >= start_date) & (df["Дата платежа"] <= target_date)
    ]
    filtered_count = len(filtered_data)
    logger.info(
        f"После фильтрации осталось {filtered_count} транзакций " f"(отфильтровано {initial_count - filtered_count})"
    )

    if filtered_count == 0:
        logger.warning(f"Не найдено транзакций для категории '{category}' " f"в указанном периоде")
        return pd.DataFrame(columns=["Год месяц", "Категория", "Траты"])

    # Группировка по месяцам
    filtered_data = filtered_data.copy()
    filtered_data["Год месяц"] = filtered_data["Дата платежа"].dt.to_period("M")
    logger.debug("Добавлен столбец 'Год месяц'")

    # Агрегация данных
    try:
        result_df = (
            filtered_data.groupby(["Год месяц", "Категория"], as_index=False)
            .agg(Траты=("Сумма платежа", "sum"))
            .round(2)
        )

        logger.info(f"Сгруппировано данных по {len(result_df)} месяцам")
        logger.debug(f"Суммарные траты: {result_df['Траты'].sum():.2f}")

    except Exception as e:
        logger.error(f"Ошибка при группировке данных: {e}")
        raise

    # Сортировка результатов
    result_df = result_df.sort_values("Год месяц")
    result_df = result_df.sort_index(ascending=False).reset_index(drop=True)
    result_df["Год месяц"] = result_df["Год месяц"].astype(str)
    logger.debug("Данные отсортированы и отформатированы")

    logger.info(f"Обработка категории '{category}' завершена успешно. " f"Возвращено {len(result_df)} строк")

    return result_df
