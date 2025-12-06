import logging

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def anylize_cashback(data: pd.DataFrame, year: int, month: int) -> dict:
    """Анализирует кешбэк по категориям за указанный месяц и год"""
    logger.info(f"Начало анализа кешбэка за {month}.{year}")
    logger.info(f"Размер входных данных: {len(data)} записей")

    try:
        # Конвертируем дату
        logger.debug("Конвертация даты платежа")
        data["Дата платежа"] = pd.to_datetime(data["Дата платежа"], dayfirst=True)

        # Фильтруем данные по году и месяцу
        logger.debug(f"Фильтрация данных за {year}-{month:02d}")
        filtered_data = data[(data["Дата платежа"].dt.year == year) & (data["Дата платежа"].dt.month == month)]

        logger.info(f"После фильтрации: {len(filtered_data)} записей")

        if filtered_data.empty:
            logger.warning(f"Нет данных за указанный период {year}-{month:02d}")
            return {}

        # Группируем по категориям и суммируем кешбэк
        logger.debug("Группировка данных по категориям")
        cashback_by_category = filtered_data.groupby("Категория")["Кэшбэк"].sum().round(2)

        # Сортируем и конвертируем в словарь
        logger.debug("Сортировка результатов")
        result = cashback_by_category.sort_values(ascending=False).to_dict()

        # Логируем результаты
        total_cashback = sum(result.values())
        top_category = next(iter(result)) if result else "нет данных"
        top_amount = result[top_category] if result else 0

        logger.info(f"Анализ завершен. Категорий: {len(result)}, Общий кэшбэк: {total_cashback:.2f}")
        logger.info(f"Топ категория: '{top_category}' - {top_amount:.2f} руб.")
        logger.debug(f"Детальные результаты: {result}")

        return result

    except KeyError as e:
        logger.error(f"Отсутствует необходимая колонка в данных: {e}")
        return {}
    except Exception as e:
        logger.error(f"Ошибка при анализе кэшбэка: {e}")
        return {}
