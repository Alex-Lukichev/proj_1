import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

BASE_DIR = Path(__file__).resolve().parent.parent

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
file_rep_name = BASE_DIR / f"report_3month_category_{current_time}.xlsx"

file_path_log = BASE_DIR / "logs" / "reports.log"
logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(file_path_log, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def save_report_to_file_no_filename_input(func: Callable[..., pd.DataFrame]) -> Callable:
    """Декоратор для сохранения отчета в файл с автоматически сгенерированным именем."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
        result = func(*args, **kwargs)
        current_time_auto = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"{func.__name__}_report_{current_time_auto}.xlsx"
        result.to_excel(report_file, index=False)
        logger.debug(f"Отчет сохранен в файл: {report_file}")
        print(f"Отчет сохранен в файл: {report_file}")
        return result

    return wrapper


def save_report_to_file_with_filename_input(file_name: Path) -> Callable:
    """Параметризуемый декоратор для сохранения отчета в файл, получает на вход имя файла."""

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = func(*args, **kwargs)
            result.to_excel(file_name, index=False)
            logger.debug(f"Отчет сохранен в файл: {file_name}")
            print(f"Отчет сохранен в файл: {file_name}")
            return result

        return wrapper

    return decorator


# @save_report_to_file_no_filename_input # применение декоратора без параметра с автогенерацией имени файла
# @save_report_to_file_with_filename_input(file_rep_name) # применение декоратора с параметром - имя файла для отчета
def spending_by_category(transactions: pd.DataFrame, category: str, input_date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    df_copy = transactions.copy()
    df_copy["Дата операции"] = pd.to_datetime(df_copy["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    if input_date is None:
        use_date = datetime.now()
    else:
        use_date = datetime.strptime(input_date, "%d.%m.%Y")
    start_date = use_date - relativedelta(months=3)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    logger.debug(
        f"Определен диапазон дат {start_date.strftime('%d.%m.%Y')} - {use_date.strftime('%d.%m.%Y')} "
        f"для фильтрации по категории {category}"
    )
    filtered_transactions = df_copy[
        (df_copy["Дата операции"] >= start_date)
        & (df_copy["Дата операции"] <= use_date)
        & (df_copy["Категория"] == category)
    ]
    logger.info(
        f"DataFrame отфильтрован по датам {start_date.strftime('%d.%m.%Y')} - {use_date.strftime('%d.%m.%Y')}"
        f"и категории {category}"
    )
    return filtered_transactions


# if __name__ == "__main__":
#     file_path_xlsx = BASE_DIR / "data" / "operations_2.xlsx"
#     file_data = read_excel_file(file_path_xlsx)
#
#     # df = pd.DataFrame({'Описание': ["Я МТС +7 921 11-22-33", "Тинькофф Мобайл +7 995 555-55-55", "Без номера"]})
#     print(spending_by_category(file_data, 'Переводы', '15.02.2022'))
