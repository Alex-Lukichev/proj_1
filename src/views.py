import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
file_path_log = BASE_DIR / "logs" / "views.log"

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(file_path_log, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_greeting(hour: int) -> str:
    """Возвращает приветствие в зависимости от часа."""
    logger.debug(f"Вывод приветствия в зависимости от часа: {hour}")
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def parse_datetime(datetime_str: str) -> datetime:
    """Парсит строку с датой и временем в формате YYYY-MM-DD HH:MM:SS в объект datetime."""
    logger.debug(f"Получаем объект datetime из строки {datetime_str}")
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def filter_df_by_date(df: pd.DataFrame, input_date: datetime) -> pd.DataFrame:
    """Фильтрует DataFrame по дате, возвращая данные за текущий месяц."""
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    start_of_month = input_date.replace(day=1, hour=0, minute=0, second=0)
    logger.debug(
        f"Определен диапазон дат для фильтрации dataframe: "
        f"{start_of_month.strftime('%d.%m.%Y')} - {input_date.strftime('%d.%m.%Y')}"
    )
    filtered_df = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= input_date)]
    logger.info(
        f"Данные отобраны за текущий месяц: "
        f"{start_of_month.strftime('%d.%m.%Y')} - {input_date.strftime('%d.%m.%Y')}"
    )
    return filtered_df


def get_card_sum_cashback(df: pd.DataFrame) -> pd.DataFrame:
    """Подсчет общей суммы расходов и кешбэка по каждой карте."""
    df = df.dropna(subset=["Номер карты"]).copy()
    df = df[df["Статус"] == "OK"]
    df.loc[:, "last_digits"] = df["Номер карты"].astype(str).str[-4:]
    logger.debug("DataFrame подготовлен для подсчета общей суммы расходов и кешбэка.")
    summary_df = (
        df.groupby("last_digits")
        .agg(
            total_spent=("Сумма операции с округлением", "sum"),
            cashback=("Сумма операции с округлением", lambda x: round(x.sum() / 100, 2)),
        )
        .reset_index()
    )
    logger.info("Общая сумма расходов и кешбэка по каждой карте посчитаны.")
    return summary_df


def get_topfive_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Топ-5 транзакций по сумме платежа."""
    filtered_df = df[df["Статус"] == "OK"]
    sorted_df = filtered_df.sort_values(by="Сумма операции с округлением", ascending=False)
    logger.info("Топ-5 транзакций по сумме платежа определены.")
    return sorted_df.head()


# if __name__ == "__main__":
#     BASE_DIR = Path(__file__).resolve().parent.parent
#     file_path_xlsx = BASE_DIR / "data" / "operations_2.xlsx"
#     file_data = read_excel_file(file_path_xlsx)
#
#     datetime_str = "2021-09-27 16:00:00"
#     parsed_date = parse_datetime(datetime_str)
#     df_filtered_by_date = filter_df_by_date(file_data, parsed_date)
#
#     # summary = get_card_sum_cashback(df_filtered_by_date)
#     # print(summary)
#
#     top5 = get_topfive_transactions(df_filtered_by_date)
#     print(top5)
#
#     # print(df_filtered_by_date)
