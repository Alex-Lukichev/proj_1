import pandas as pd

from src.reports import (save_report_to_file_no_filename_input, save_report_to_file_with_filename_input,
                         spending_by_category)


def test_spending_by_category(sample_transactions):
    """Тестирует функцию spending_by_category на корректное фильтрование."""
    result = spending_by_category(sample_transactions, "Переводы", "15.02.2022")
    assert isinstance(result, pd.DataFrame), "Результат должен быть DataFrame"
    assert len(result) == 2, "Должно быть 2 транзакции в категории 'Переводы' за последние три месяца"
    assert (result["Категория"] == "Переводы").all(), "Все транзакции должны быть в категории 'Переводы'"


def test_save_report_to_file_no_filename_input_decorator(tmp_path, sample_transactions, monkeypatch):
    """Тестирует декоратор, сохраняющий отчет в файл с автосгенерированным именем."""
    generated_files = []

    def mock_to_excel(self, path, *args, **kwargs):
        generated_files.append(path)

    monkeypatch.setattr(pd.DataFrame, "to_excel", mock_to_excel)
    decorated_function = save_report_to_file_no_filename_input(spending_by_category)
    decorated_function(sample_transactions, "Переводы", "15.02.2022")
    assert len(generated_files) == 1, "Должен быть создан один файл отчета"
    assert "spending_by_category_report_" in str(
        generated_files[0]
    ), "Имя файла должно быть сгенерировано автоматически"


def test_save_report_to_file_with_filename_input_decorator(tmp_path, sample_transactions, monkeypatch):
    """Тестирует декоратор, сохраняющий отчет в файл с указанным именем файла."""
    report_file = tmp_path / "custom_report.xlsx"
    generated_files = []

    def mock_to_excel(self, path, *args, **kwargs):
        generated_files.append(path)

    monkeypatch.setattr(pd.DataFrame, "to_excel", mock_to_excel)
    save_report_decorator = save_report_to_file_with_filename_input(report_file)
    decorated_function = save_report_decorator(spending_by_category)
    decorated_function(sample_transactions, "Переводы", "15.02.2022")
    assert len(generated_files) == 1, "Должен быть создан один файл отчета"
    assert generated_files[0] == report_file, f"Файл отчета должен быть сохранен как {report_file}"
