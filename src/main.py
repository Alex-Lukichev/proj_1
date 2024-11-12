import json
from pathlib import Path

from utils import get_currency_rate, get_stock_prices, read_excel_file
from views import filter_df_by_date, get_card_sum_cashback, get_greeting, get_topfive_transactions, parse_datetime

BASE_DIR = Path(__file__).resolve().parent.parent
file_path_xlsx = BASE_DIR / "data" / "operations.xlsx"
user_settings_path = BASE_DIR / "user_settings.json"


def main(date_time_str: str) -> str:
    """Главная функция, возвращающая JSON-ответ с приветствием и исходной датой."""
    # приветствие пользователя
    dt = parse_datetime(date_time_str)
    greeting = get_greeting(dt.hour)

    # извлечение отфильтрованной по датам информации из файла
    df = read_excel_file(file_path_xlsx)
    date_filtered_df = filter_df_by_date(df, dt)

    # суммирование операций и кешбэка по картам
    summary_df = get_card_sum_cashback(date_filtered_df)
    cards_data = [
        {
            "last_digits": row["last_digits"],
            "total_spent": round(row["total_spent"], 2),
            "cashback": round(row["cashback"], 2),
        }
        for index, row in summary_df.iterrows()
    ]

    # топ 5 операций по сумме
    topfive_df = get_topfive_transactions(date_filtered_df)
    topfive_transactions = [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": round(row["Сумма операции с округлением"], 2),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for index, row in topfive_df.iterrows()
    ]

    # чтение пользовательских установок валют и акций
    with open(user_settings_path, "r") as file:
        parsed_user_settings = json.load(file)
    user_currencies = parsed_user_settings["user_currencies"]
    user_stocks = parsed_user_settings["user_stocks"]

    # получение курсов валют
    currency_rates = get_currency_rate(user_currencies)

    # получение стоимости акций из S&P500
    stock_prices = get_stock_prices(user_stocks)

    # формирование ответа
    response = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": topfive_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(response, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    datetime_str = "2018-01-20 18:59:59"
    print(main(datetime_str))
