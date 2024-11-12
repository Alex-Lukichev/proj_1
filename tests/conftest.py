import sys
from pathlib import Path

import pandas as pd
import pytest

# путь к src для тестов
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture
def sample_transactions():
    """Пример данных о транзакциях для тестов."""
    data = {
        "Дата операции": [
            "15.01.2022 10:15:00",
            "20.01.2022 12:30:00",
            "25.02.2022 14:45:00",
            "05.02.2022 10:15:00",
            "15.03.2022 12:30:00",
        ],
        "Категория": ["Переводы", "Покупки", "Переводы", "Переводы", "Переводы"],
        "Сумма": [1500, 2000, 500, 800, 1200],
    }
    return pd.DataFrame(data)
