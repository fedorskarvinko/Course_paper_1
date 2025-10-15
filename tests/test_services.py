import json
from unittest.mock import patch

from src.services import simple_search


@patch("src.services.read_transactions_xlsx")
def test_search_returns_valid_json_string(mock_read_xlsx):
    """Тест что функция возвращает валидную JSON строку"""
    # Мокаем данные
    mock_data = [
        {"Описание": "Покупка в магазине", "Категория": "Еда", "Сумма": -100},
        {"Описание": "Оплата такси", "Категория": "Транспорт", "Сумма": -50},
    ]
    mock_read_xlsx.return_value = mock_data

    result = simple_search("магазин", "test.xlsx")

    # Проверяем что это строка
    assert isinstance(result, str)

    # Проверяем что это валидный JSON
    parsed_result = json.loads(result)
    assert len(parsed_result) == 1
    assert parsed_result[0]["Описание"] == "Покупка в магазине"


@patch("src.services.read_transactions_xlsx")
def test_search_by_description(mock_read_xlsx):
    """Тест поиска по описанию"""
    mock_data = [
        {"Описание": "Покупка в магазине", "Категория": "Еда", "Сумма": -100},
        {"Описание": "Оплата такси", "Категория": "Транспорт", "Сумма": -50},
    ]
    mock_read_xlsx.return_value = mock_data

    result = simple_search("такси", "test.xlsx")
    parsed_result = json.loads(result)

    assert len(parsed_result) == 1
    assert parsed_result[0]["Описание"] == "Оплата такси"
    assert parsed_result[0]["Категория"] == "Транспорт"


@patch("src.services.read_transactions_xlsx")
def test_search_by_category(mock_read_xlsx):
    """Тест поиска по категории"""
    mock_data = [
        {"Описание": "Покупка в магазине", "Категория": "Еда", "Сумма": -100},
        {"Описание": "Оплата такси", "Категория": "Транспорт", "Сумма": -50},
    ]
    mock_read_xlsx.return_value = mock_data

    result = simple_search("еда", "test.xlsx")
    parsed_result = json.loads(result)

    assert len(parsed_result) == 1
    assert parsed_result[0]["Категория"] == "Еда"


@patch("src.services.read_transactions_xlsx")
def test_case_insensitive_search(mock_read_xlsx):
    """Тест поиска без учета регистра"""
    mock_data = [
        {"Описание": "Покупка в Магазине", "Категория": "Еда", "Сумма": -100},
        {"Описание": "Оплата Такси", "Категория": "Транспорт", "Сумма": -50},
    ]
    mock_read_xlsx.return_value = mock_data

    # Поиск в разном регистре
    result1 = simple_search("магазин", "test.xlsx")
    result2 = simple_search("МАГАЗИН", "test.xlsx")

    parsed1 = json.loads(result1)
    parsed2 = json.loads(result2)

    assert len(parsed1) == 1
    assert len(parsed2) == 1
    assert parsed1[0]["Описание"] == "Покупка в Магазине"
