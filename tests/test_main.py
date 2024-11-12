import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.main import main


@pytest.fixture
def mock_user_settings(tmp_path):
    """Создание временного файла с пользовательскими настройками."""
    user_settings_path = tmp_path / "user_settings.json"
    user_settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]}
    with open(user_settings_path, "w") as file:
        json.dump(user_settings, file)
    return user_settings_path


@pytest.fixture
def mock_excel_file(tmp_path):
    """Создание временного Excel-файла с тестовыми данными."""
    file_path_xlsx = tmp_path / "operations.xlsx"
    df = pd.DataFrame(
        {
            "Дата операции": ["01.01.2018 12:00:00", "05.01.2018 14:00:00"],
            "Сумма операции с округлением": [1000.0, 500.0],
            "Категория": ["Категория1", "Категория2"],
            "Описание": ["Описание1", "Описание2"],
            "Номер карты": ["1234567890123456", "1234567890123457"],
            "Статус": ["OK", "OK"],
        }
    )
    df.to_excel(file_path_xlsx, index=False)
    return file_path_xlsx


@patch("src.main.get_currency_rate")
@patch("src.main.get_stock_prices")
@patch("src.main.read_excel_file")
def test_main(mock_read_excel, mock_get_stock_prices, mock_get_currency_rate, mock_user_settings, mock_excel_file):
    datetime_str = "2018-01-10 23:59:59"

    # Mocking the return values of external dependencies
    mock_read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": [datetime(2018, 1, 1, 12, 0), datetime(2018, 1, 5, 14, 0)],
            "Сумма операции с округлением": [1000.0, 500.0],
            "Категория": ["Категория1", "Категория2"],
            "Описание": ["Описание1", "Описание2"],
            "Номер карты": ["1234567890123456", "1234567890123457"],
            "Статус": ["OK", "OK"],
        }
    )
    mock_get_currency_rate.return_value = [{"currency": "USD", "rate": 74.85}, {"currency": "EUR", "rate": 89.12}]
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.25}, {"stock": "TSLA", "price": 725.50}]

    # Переопределяем путь к файлам
    with patch("src.main.user_settings_path", mock_user_settings):
        with patch("src.main.file_path_xlsx", mock_excel_file):
            # Вызов функции main и проверка результата
            response_json = main(datetime_str)
            response = json.loads(response_json)

            # Проверяем, что приветствие корректное
            assert response["greeting"] == "Доброй ночи"

            # Проверяем, что данные по картам корректны
            assert response["cards"] == [
                {"last_digits": "3456", "total_spent": 1000.0, "cashback": 10.0},
                {"last_digits": "3457", "total_spent": 500.0, "cashback": 5.0},
            ]

            # Проверяем, что топовые транзакции корректны
            assert response["top_transactions"] == [
                {"date": "01.01.2018", "amount": 1000.0, "category": "Категория1", "description": "Описание1"},
                {"date": "05.01.2018", "amount": 500.0, "category": "Категория2", "description": "Описание2"},
            ]

            # Проверяем, что курсы валют корректны
            assert response["currency_rates"] == [
                {"currency": "USD", "rate": 74.85},
                {"currency": "EUR", "rate": 89.12},
            ]

            # Проверяем, что данные по акциям корректны
            assert response["stock_prices"] == [{"stock": "AAPL", "price": 150.25}, {"stock": "TSLA", "price": 725.50}]
