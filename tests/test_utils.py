import pathlib
from unittest.mock import MagicMock, patch

import pandas as pd

from src import utils
from src.utils import get_currency_rate, get_stock_prices, read_excel_file


def test_read_excel_file(tmp_path):
    file_path = tmp_path / "test_file.xlsx"
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df.to_excel(file_path, index=False)

    result_df = read_excel_file(file_path)
    pd.testing.assert_frame_equal(result_df, df)


def test_read_excel_file_exception_handling(capfd):
    non_existent_file_path = pathlib.Path("non_existent_file.xlsx")

    result_df = read_excel_file(non_existent_file_path)
    assert result_df is None or result_df.empty
    captured = capfd.readouterr()
    assert "Произошла ошибка:" in captured.out


@patch("utils.requests.request")
def test_get_currency_rate(mock_request):
    original_api_key = utils.APILAYER_API_KEY
    utils.APILAYER_API_KEY = "test_api_key"

    try:
        mock_response = MagicMock()
        mock_response.json.return_value = {"info": {"rate": 75.5}}
        mock_request.return_value = mock_response

        currency_list = ["USD"]
        result = utils.get_currency_rate(currency_list, "RUB")
        assert result == [{"currency": "USD", "rate": 75.5}]
        mock_request.assert_called_once_with(
            "GET",
            "https://api.apilayer.com/exchangerates_data/convert?to=RUB&from=USD&amount=1",
            headers={"apikey": "test_api_key"},
            data={},
        )
    finally:
        utils.APILAYER_API_KEY = original_api_key


def test_get_currency_rate_exception_handling(capfd):
    cur_list = ["USD", "EUR"]

    with patch("src.utils.requests.request", side_effect=Exception("API request failed")):
        result = get_currency_rate(cur_list, "RUB")

    expected_result = [{"currency": "USD", "rate": ""}, {"currency": "EUR", "rate": ""}]
    assert result == expected_result

    captured = capfd.readouterr()
    assert "Исключение API request failed. Не удалось получить курс валюты USD." in captured.out
    assert "Исключение API request failed. Не удалось получить курс валюты EUR." in captured.out


@patch("utils.requests.get")
def test_get_stock_prices(mock_get):
    original_api_key = utils.ALPHAVANTAGE_API_KEY
    utils.ALPHAVANTAGE_API_KEY = "test_api_key"

    try:
        mock_response = MagicMock()
        mock_response.json.return_value = {"Time Series (5min)": {"2023-10-30 09:35:00": {"4. close": "150.00"}}}
        mock_get.return_value = mock_response

        stock_list = ["AAPL"]
        result = get_stock_prices(stock_list)
        assert result == [{"stock": "AAPL", "price": 150.0}]
        mock_get.assert_called_once_with(
            "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&"
            "symbol=AAPL&interval=5min&apikey=test_api_key"
        )

    finally:
        utils.ALPHAVANTAGE_API_KEY = original_api_key


def test_get_stock_prices_exception_handling(capfd):
    stock_list = ["AAPL", "TSLA"]

    with patch("src.utils.requests.get", side_effect=Exception("API request failed")):
        result = get_stock_prices(stock_list)

    expected_result = [{"stock": "AAPL", "price": ""}, {"stock": "TSLA", "price": ""}]
    assert result == expected_result

    captured = capfd.readouterr()
    assert "Исключение API request failed. Не удалось получить стоимость акции AAPL." in captured.out
    assert "Исключение API request failed. Не удалось получить стоимость акции TSLA." in captured.out
