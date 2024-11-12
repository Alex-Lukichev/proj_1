import json
import logging
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

file_path_log = BASE_DIR / "logs" / "services.log"
logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(file_path_log, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_with_phone_num(df: pd.DataFrame) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера."""
    if "Описание" not in df or df["Описание"].dtype != "O":
        return json.dumps([], ensure_ascii=False, indent=4)
    mobile_pattern = re.compile(r"\+7 \d{3} \d{2,3}-\d{2}-\d{2}")
    transactions_with_mobile = df[df["Описание"].str.contains(mobile_pattern, na=False)].copy()
    result_json = transactions_with_mobile.to_json(orient="records", force_ascii=False, indent=4)
    logger.info("Транзакции, содержащие в описании мобильные номера, определены.")
    return result_json


# if __name__ == "__main__":
#     BASE_DIR = Path(__file__).resolve().parent.parent
#     file_path_xlsx = BASE_DIR / "data" / "operations.xlsx"
#     file_data = read_excel_file(file_path_xlsx)
#
#
#     # df = pd.DataFrame({'Описание': ["Я МТС +7 921 11-22-33", "Тинькофф Мобайл +7 995 555-55-55", "Без номера"]})
#     print(get_transactions_with_phone_num(file_data))
