from datetime import datetime

import pandas as pd
import pytest

from src.views import filter_df_by_date, get_card_sum_cashback, get_greeting, get_topfive_transactions, parse_datetime


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (23, "Доброй ночи"),
        (4, "Доброй ночи"),
    ],
)
def test_get_greeting(hour, expected_greeting):
    assert get_greeting(hour) == expected_greeting


def test_parse_datetime():
    datetime_str = "2021-09-27 16:00:00"
    expected_datetime = datetime(2021, 9, 27, 16, 0, 0)
    assert parse_datetime(datetime_str) == expected_datetime


def test_filter_df_by_date():
    df = pd.DataFrame(
        {
            "Дата операции": [
                "01.09.2021 10:00:00",
                "15.09.2021 12:00:00",
                "30.09.2021 14:00:00",
                "01.10.2021 16:00:00",
            ],
        }
    )
    input_date = datetime(2021, 9, 30, 23, 59, 59)
    result_df = filter_df_by_date(df, input_date)
    expected_dates = ["01.09.2021 10:00:00", "15.09.2021 12:00:00", "30.09.2021 14:00:00"]
    assert list(result_df["Дата операции"].dt.strftime("%d.%m.%Y %H:%M:%S")) == expected_dates


def test_get_card_sum_cashback():
    df = pd.DataFrame(
        {
            "Номер карты": ["1234567890123456", "1234567890123456", "6543210987654321"],
            "Статус": ["OK", "OK", "OK"],
            "Сумма операции с округлением": [1000, 2000, 3000],
        }
    )
    result_df = get_card_sum_cashback(df)
    expected_df = pd.DataFrame(
        {
            "last_digits": ["3456", "4321"],
            "total_spent": [3000, 3000],
            "cashback": [30.0, 30.0],
        }
    )
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_get_topfive_transactions():
    df = pd.DataFrame(
        {
            "Статус": ["OK", "OK", "OK", "FAILED", "OK", "OK", "FAILED", "OK"],
            "Сумма операции с округлением": [500, 2000, 1500, 1000, 3000, 1700, 800, 1200],
        }
    )
    result_df = get_topfive_transactions(df)
    expected_df = pd.DataFrame(
        {
            "Статус": ["OK", "OK", "OK", "OK", "OK"],
            "Сумма операции с округлением": [3000, 2000, 1700, 1500, 1200],
        }
    )
    pd.testing.assert_frame_equal(
        result_df[["Статус", "Сумма операции с округлением"]].reset_index(drop=True),
        expected_df.reset_index(drop=True),
    )
