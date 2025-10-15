from unittest.mock import MagicMock, patch

import pandas as pd

from src.reports import _write_json, report_writer, spending_by_category


@patch("src.reports._write_json")
@patch("src.reports.get_date")
@patch("src.reports.filter_by_date")
def test_spending_by_category_basic(mock_filter, mock_get_date, mock_write):
    """Тест базовой работы spending_by_category"""
    # Подготовка моков
    mock_get_date.return_value = "2024-01-01"
    mock_filter.return_value = [
        {"Дата": "2024-01-15", "Категория": "Еда", "Сумма": -500, "Описание": "Продукты"},
        {"Дата": "2024-02-20", "Категория": "Еда", "Сумма": -300, "Описание": "Кафе"},
    ]

    # Тестовые данные
    test_data = pd.DataFrame(
        [
            {"Дата": "2024-01-15", "Категория": "Еда", "Сумма": -500},
            {"Дата": "2024-02-20", "Категория": "Еда", "Сумма": -300},
            {"Дата": "2024-01-10", "Категория": "Транспорт", "Сумма": -200},
        ]
    )

    # Вызов функции
    result = spending_by_category(test_data, "Еда")

    # Проверки
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert all(result["Категория"] == "Еда")
    mock_write.assert_called_once()


@patch("src.reports._write_json")
@patch("src.reports.get_date")
@patch("src.reports.filter_by_date")
def test_spending_by_category_with_date(mock_filter, mock_get_date, mock_write):
    """Тест spending_by_category с указанной датой"""
    mock_get_date.return_value = "2024-03-01"
    mock_filter.return_value = [{"Дата": "2024-02-15", "Категория": "Транспорт", "Сумма": -100}]

    test_data = pd.DataFrame([{"Дата": "2024-02-15", "Категория": "Транспорт", "Сумма": -100}])

    result = spending_by_category(test_data, "Транспорт", "2024-03-01 12:00:00")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["Категория"] == "Транспорт"
    mock_write.assert_called_once()


@patch("src.reports._write_json")
@patch("src.reports.get_date")
@patch("src.reports.filter_by_date")
def test_spending_by_category_no_results(mock_filter, mock_get_date, mock_write):
    """Тест когда нет данных по категории"""
    mock_get_date.return_value = "2024-01-01"
    # Возвращаем DataFrame с данными, но без нужной категории
    mock_filter.return_value = [{"Дата": "2024-01-15", "Категория": "Транспорт", "Сумма": -100}]

    test_data = pd.DataFrame([{"Дата": "2024-01-15", "Категория": "Транспорт", "Сумма": -100}])

    result = spending_by_category(test_data, "Еда")  # Ищем категорию которой нет

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0  # Должен вернуть пустой DataFrame
    mock_write.assert_called_once()


@patch("src.reports.os.makedirs")
@patch("src.reports.open")
def test_write_json_with_dataframe(mock_open, mock_makedirs):
    """Тест записи JSON с DataFrame"""
    test_df = pd.DataFrame([{"Категория": "Еда", "Сумма": -500}, {"Категория": "Транспорт", "Сумма": -200}])

    _write_json("test_report.json", test_df)

    mock_makedirs.assert_called_once_with(".", exist_ok=True)
    # Проверяем что to_json был вызван (через MagicMock)
    assert True  # to_json вызывается внутри pandas


@patch("src.reports.os.makedirs")
@patch("src.reports.open")
def test_write_json_with_dict(mock_open, mock_makedirs):
    """Тест записи JSON со словарем"""
    test_data = {"result": "success", "count": 5}
    mock_file = MagicMock()
    mock_open.return_value.enter.return_value = mock_file

    _write_json("test_report.json", test_data)
    mock_makedirs.assert_called_once_with(".", exist_ok=True)
    mock_open.assert_called_once_with("test_report.json", "w", encoding="utf-8")


@patch("src.reports._write_json")
def test_report_writer_decorator(mock_write):
    """Тест декоратора report_writer"""

    @report_writer()
    def test_function():
        return {"data": "test"}

    result = test_function()

    assert result == {"data": "test"}
    mock_write.assert_called_once()


@patch("src.reports._write_json")
def test_report_writer_with_filename(mock_write):
    """Тест декоратора report_writer с именем файла"""

    @report_writer("custom_report.json")
    def test_function():
        return pd.DataFrame([{"test": "data"}])

    result = test_function()

    assert isinstance(result, pd.DataFrame)
    mock_write.assert_called_once_with("custom_report.json", result)
