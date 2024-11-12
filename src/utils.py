import logging
import os
import pathlib
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

file_path_log = BASE_DIR / "logs" / "utils.log"
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(file_path_log, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

load_dotenv(".env")
APILAYER_API_KEY = os.getenv("APILAYER_API_KEY")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")


def read_excel_file(file_path: pathlib.Path) -> pd.DataFrame:
    """Функция читает данные из .xlsx файла и возвращает их в формате DataFrame."""
    try:
        logger.debug(f"Чтение данных из Excel файла {file_path}")
        file_data = pd.read_excel(file_path, engine="openpyxl")
        logger.info(f"Данные из Excel файла {file_path} получены")
        return file_data
    except Exception as e:
        logger.error(f"Ошибка: {e} - файл {file_path} не найден")
        print(f"Произошла ошибка: {e}")
        return pd.DataFrame()


def get_currency_rate(cur_list: list, convert_to: str = "RUB") -> list[dict[str, Any]]:
    """Получение курсов валют с apilayer.com."""
    cur_rates_list = []
    for currency in cur_list:
        try:
            url = f"https://api.apilayer.com/exchangerates_data/convert?to={convert_to}" f"&from={currency}&amount=1"
            payload: dict[Any, Any] = {}
            headers = {"apikey": APILAYER_API_KEY}
            logger.debug(f"Отправляем API-запрос в APILAYER для конвертации {currency} в {convert_to}.")
            response = requests.request("GET", url, headers=headers, data=payload)
            logger.debug("Получен ответ от APILAYER")
            data = response.json()
            rate = data["info"]["rate"]
            cur_rates_list.append({"currency": currency, "rate": round(rate, 2)})
            logger.info(f"Обработан ответ от APILAYER на запрос конвертации {currency} в {convert_to}.")
        except Exception as e:
            cur_rates_list.append({"currency": currency, "rate": ""})
            logger.error(f"Исключение {e}. Не удалось получить курс валюты {currency}.")
            print(f"Исключение {e}. Не удалось получить курс валюты {currency}.")
    return cur_rates_list


def get_stock_prices(stock_list: list) -> list[dict[str, Any]]:
    """Получение стоимости акций с alphavantage.co."""
    stock_prices_list = []
    for symbol in stock_list:
        try:
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&"
                f"symbol={symbol}&interval=5min&apikey={ALPHAVANTAGE_API_KEY}"
            )
            logger.debug(f"Отправляем API-запрос в ALPHAVANTAGE для получения стоимости акции {symbol}.")
            r = requests.get(url)
            logger.debug("Получен ответ от ALPHAVANTAGE")
            data = r.json()
            time_series = data.get("Time Series (5min)", {})
            if time_series:
                first_timestamp = next(iter(time_series))
                first_close_value = time_series[first_timestamp]["4. close"]
                stock_prices_list.append({"stock": symbol, "price": round(float(first_close_value), 2)})
                logger.info(f"Обработан ответ от ALPHAVANTAGE на запрос стоимости акции {symbol}.")
            else:
                logger.warning(f"Нет данных в разделе 'Time Series (5min)' в ответе для акции {symbol}.")
                print(f"Нет данных в разделе 'Time Series (5min)' в ответе для акции {symbol}.")

        except Exception as e:
            stock_prices_list.append({"stock": symbol, "price": ""})
            logger.error(f"Исключение {e}. Не удалось получить стоимость акции {symbol}.")
            print(f"Исключение {e}. Не удалось получить стоимость акции {symbol}.")
    return stock_prices_list


# if __name__ == "__main__":
#     BASE_DIR = Path(__file__).resolve().parent.parent
#     file_path_xlsx = BASE_DIR / "data" / "operations.xlsx"
#     # print(file_path_xlsx)
#
#     # df = read_excel_file(file_path_xlsx)
#     # print(df)
#
#     print(get_stock_prices(['AAPL', 'AMZN']))
