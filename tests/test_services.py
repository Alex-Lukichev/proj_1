# tests/test_services.py
import json

import pandas as pd
import pytest

from src.services import get_transactions_with_phone_num


@pytest.mark.parametrize(
    "data, expected_result",
    [
        (
            # Тест с телефонными номерами
            {
                "Описание": ["Я МТС +7 921 11-22-33", "Тинькофф Мобайл +7 995 555-55-55", "Без номера"],
                "Сумма": [1000, 2000, 1500],
            },
            json.dumps(
                [
                    {"Описание": "Я МТС +7 921 11-22-33", "Сумма": 1000},
                    {"Описание": "Тинькофф Мобайл +7 995 555-55-55", "Сумма": 2000},
                ],
                ensure_ascii=False,
            ),
        ),
        (
            # Тест без телефонных номеров
            {"Описание": ["Без номера 1", "Без номера 2", "Нет мобильного номера"], "Сумма": [500, 700, 900]},
            json.dumps([], ensure_ascii=False),
        ),
        (
            # Пустой DataFrame
            {"Описание": [], "Сумма": []},
            json.dumps([], ensure_ascii=False),
        ),
        (
            # Номера в неправильном формате и один правильный
            {
                "Описание": ["МТС +7 (921) 11-22-33", "Тинькофф +79555555555", "Я МТС +7 921 11-22-33"],
                "Сумма": [1500, 2000, 2500],
            },
            json.dumps([{"Описание": "Я МТС +7 921 11-22-33", "Сумма": 2500}], ensure_ascii=False),
        ),
    ],
)
def test_get_transactions_with_phone_num(data, expected_result):
    """Параметризованный тест функции get_transactions_with_phone_num с различными входными данными."""
    df = pd.DataFrame(data)
    result = get_transactions_with_phone_num(df)
    result_data = json.loads(result)
    expected_data = json.loads(expected_result)
    assert result_data == expected_data, "Функция вернула неожиданный JSON результат."
