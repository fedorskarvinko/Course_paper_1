import json
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.utils import (filter_by_date, filter_by_state, get_card_infos, get_cashback, get_current_exchange_rate,
                       get_date, get_greeting, get_last_four, get_stock, get_top_transactions, load_json_data,
                       read_transactions_xlsx)


@pytest.mark.parametrize(
    "hour,expected",
    [
        (0, "Доброй ночи"),
        (1, "Доброй ночи"),
        (2, "Доброй ночи"),
        (3, "Доброй ночи"),
        (4, "Доброй ночи"),
        (5, "Доброй ночи"),
        (6, "Доброе утро"),
        (7, "Доброе утро"),
        (8, "Доброе утро"),
        (9, "Доброе утро"),
        (10, "Доброе утро"),
        (11, "Доброе утро"),
        (12, "Добрый день"),
        (13, "Добрый день"),
        (14, "Добрый день"),
        (15, "Добрый день"),
        (16, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),
        (19, "Добрый вечер"),
        (20, "Добрый вечер"),
        (21, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Добрый вечер"),
    ],
)
def test_get_greeting_all_hours(hour, expected):
    """Тестируем все возможные значения часов"""
    assert get_greeting(hour) == expected


def test_get_greeting_boundary_values():
    """Тестируем граничные значения"""
    assert get_greeting(0) == "Доброй ночи"
    assert get_greeting(5) == "Доброй ночи"
    assert get_greeting(6) == "Доброе утро"
    assert get_greeting(11) == "Доброе утро"
    assert get_greeting(12) == "Добрый день"
    assert get_greeting(17) == "Добрый день"
    assert get_greeting(18) == "Добрый вечер"
    assert get_greeting(23) == "Добрый вечер"


def test_read_transactions_xlsx_file_not_found(tmp_path):
    """Тест когда файл не существует"""
    non_existent_file = tmp_path / "nonexistent.xlsx"
    result = read_transactions_xlsx(str(non_existent_file))
    assert result == []


def test_empty_file(tmp_path):
    """Тест когда файл пустой"""
    empty_file = tmp_path / "empty.xlsx"
    empty_file.write_bytes(b"")  # Создаем пустой файл

    result = read_transactions_xlsx(str(empty_file))
    assert result == []


@patch("src.utils.pd.read_excel")
def test_successful_read(mock_read_excel, tmp_path):
    """Тест успешного чтения файла"""
    # Создаем тестовый файл
    test_file = tmp_path / "test.xlsx"
    test_file.write_bytes(b"test data")

    # Мокаем возвращаемые данные
    mock_data = pd.DataFrame(
        [
            {"Дата платежа": "01.01.2023", "Сумма": 1000, "Категория": "Еда"},
            {"Дата платежа": "02.01.2023", "Сумма": 2000, "Категория": "Транспорт"},
        ]
    )
    mock_read_excel.return_value = mock_data

    result = read_transactions_xlsx(str(test_file))

    assert len(result) == 2
    assert result[0]["Дата платежа"] == "01.01.2023"
    assert result[1]["Сумма"] == 2000
    mock_read_excel.assert_called_once_with(str(test_file))


@patch("src.utils.pd.read_excel")
def test_empty_dataframe(mock_read_excel, tmp_path):
    """Тест когда Excel файл пустой"""
    test_file = tmp_path / "test.xlsx"
    test_file.write_bytes(b"test data")

    mock_read_excel.return_value = pd.DataFrame()  # Пустой DataFrame

    result = read_transactions_xlsx(str(test_file))
    assert result == []


@patch("src.utils.pd.read_excel")
def test_to_dict_returns_non_list(mock_read_excel, tmp_path):
    """Тест когда to_dict возвращает не список"""
    test_file = tmp_path / "test.xlsx"
    test_file.write_bytes(b"test data")

    # Мокаем DataFrame который возвращает не список при to_dict
    mock_df = pd.DataFrame([{"test": "data"}])
    mock_read_excel.return_value = mock_df

    # Мокаем to_dict чтобы возвращал не список
    with patch.object(mock_df, "to_dict") as mock_to_dict:
        mock_to_dict.return_value = {"not": "a list"}

        result = read_transactions_xlsx(str(test_file))
        assert result == []


def test_load_json_data_file_not_found(tmp_path):
    """Тест когда файл не существует"""
    non_existent_file = tmp_path / "nonexistent.json"
    result = load_json_data(str(non_existent_file))
    assert result == {}


def test_load_json_data_empty_file(tmp_path):
    """Тест когда файл пустой"""
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("")  # Создаем пустой файл

    result = load_json_data(str(empty_file))
    assert result == {}


def test_successful_read_dict(tmp_path):
    """Тест успешного чтения JSON с словарем"""
    test_data = {"key": "value", "number": 123, "list": [1, 2, 3]}
    test_file = tmp_path / "test.json"
    test_file.write_text(json.dumps(test_data))

    result = load_json_data(str(test_file))
    assert result == test_data
    assert isinstance(result, dict)


def test_json_with_list_returns_empty_dict(tmp_path):
    """Тест когда JSON содержит список вместо словаря"""
    test_data = [1, 2, 3, 4, 5]
    test_file = tmp_path / "test.json"
    test_file.write_text(json.dumps(test_data))

    result = load_json_data(str(test_file))
    assert result == {}  # Должен вернуть пустой словарь


def test_invalid_json_format(tmp_path):
    """Тест когда файл содержит невалидный JSON"""
    test_file = tmp_path / "test.json"
    test_file.write_text('{"invalid": json, missing quotes}')

    result = load_json_data(str(test_file))
    assert result == {}


def test_nested_dict_structure(tmp_path):
    """Тест со сложной вложенной структурой"""
    test_data = {
        "user": {"name": "John", "age": 30, "preferences": {"theme": "dark", "language": "ru"}},
        "settings": {"currency": "USD", "notifications": True},
    }
    test_file = tmp_path / "test.json"
    test_file.write_text(json.dumps(test_data))

    result = load_json_data(str(test_file))
    assert result == test_data
    assert result["user"]["name"] == "John"


def test_normal_string():
    """Тест обычной строки достаточной длины"""
    assert get_last_four("123456789") == "6789"
    assert get_last_four("hello world") == "orld"


def test_exactly_four_chars():
    """Тест строки длиной ровно 4 символа"""
    assert get_last_four("1234") == "1234"
    assert get_last_four("abcd") == "abcd"


def test_less_than_four_chars():
    """Тест строки менее 4 символов"""
    assert get_last_four("123") == "123"
    assert get_last_four("ab") == "ab"
    assert get_last_four("x") == "x"


def test_empty_string():
    """Тест пустой строки"""
    assert get_last_four("") == "None"


def test_positive_amounts():
    """Тест положительных сумм"""
    assert get_cashback(100.0) == 1.0
    assert get_cashback(1000.0) == 10.0
    assert get_cashback(500.0) == 5.0


def test_rounding():
    """Тест округления"""
    assert get_cashback(123.45) == 1.23
    assert get_cashback(99.99) == 1.0  # 0.9999 → 1.0
    assert get_cashback(1234.56) == 12.35  # 12.3456 → 12.35


def test_zero_amount():
    """Тест нулевой суммы"""
    assert get_cashback(0.0) == 0.0
    assert get_cashback(0) == 0.0


def test_small_amounts():
    """Тест маленьких сумм"""
    assert get_cashback(1.0) == 0.01
    assert get_cashback(0.5) == 0.01  # 0.005 → 0.01
    assert get_cashback(0.1) == 0.0  # 0.001 → 0.0


def test_negative_amounts():
    """Тест отрицательных сумм"""
    assert get_cashback(-100.0) == -1.0
    assert get_cashback(-500.0) == -5.0
    assert get_cashback(-123.45) == -1.23


def test_filter_ok_status():
    """Тест фильтрации по статусу 'OK' (по умолчанию)"""
    data = [
        {"Статус": "OK", "Сумма": 100},
        {"Статус": "PENDING", "Сумма": 200},
        {"Статус": "OK", "Сумма": 300},
        {"Статус": "FAILED", "Сумма": 400},
    ]

    result = filter_by_state(data)
    expected = [
        {"Статус": "OK", "Сумма": 100},
        {"Статус": "OK", "Сумма": 300},
    ]

    assert result == expected


def test_filter_custom_status():
    """Тест фильтрации по кастомному статусу"""
    data = [
        {"Статус": "PENDING", "Сумма": 100},
        {"Статус": "OK", "Сумма": 200},
        {"Статус": "PENDING", "Сумма": 300},
    ]

    result = filter_by_state(data, "PENDING")
    expected = [
        {"Статус": "PENDING", "Сумма": 100},
        {"Статус": "PENDING", "Сумма": 300},
    ]

    assert result == expected


def test_empty_result():
    """Тест когда нет подходящих записей"""
    data = [
        {"Статус": "PENDING", "Сумма": 100},
        {"Статус": "FAILED", "Сумма": 200},
    ]

    result = filter_by_state(data, "OK")
    assert result == []


def test_all_match():
    """Тест когда все записи подходят"""
    data = [
        {"Статус": "OK", "Сумма": 100},
        {"Статус": "OK", "Сумма": 200},
    ]

    result = filter_by_state(data, "OK")
    assert result == data


def test_empty_input_list():
    """Тест с пустым входным списком"""
    with pytest.raises(ValueError, match="Пустой список"):
        filter_by_state([])


def test_basic_functionality():
    """Тест основной функциональности"""
    transactions = [
        {"Номер карты": "1234567812345678", "Сумма платежа": -1000.0},
        {"Номер карты": "1234567812345678", "Сумма платежа": -500.0},
        {"Номер карты": "8765432187654321", "Сумма платежа": -2000.0},
        {"Номер карты": "1234567812345678", "Сумма платежа": 300.0},  # Положительная - игнорируется
    ]

    result = get_card_infos(transactions)

    expected = [
        {"last_digits": "5678", "total_spent": 1500.0, "cashback": 15.0},
        {"last_digits": "4321", "total_spent": 2000.0, "cashback": 20.0},
    ]

    assert result == expected


def test_empty_transactions():
    """Тест с пустым списком транзакций"""
    result = get_card_infos([])
    assert result == []


def test_only_positive_transactions():
    """Тест когда все транзакции положительные"""
    transactions = [
        {"Номер карты": "1234567812345678", "Сумма платежа": 1000.0},
        {"Номер карты": "8765432187654321", "Сумма платежа": 500.0},
    ]

    result = get_card_infos(transactions)
    assert result == []


def test_single_card_multiple_transactions():
    """Тест одной карты с несколькими транзакциями"""
    transactions = [
        {"Номер карты": "1111222233334444", "Сумма платежа": -100.0},
        {"Номер карты": "1111222233334444", "Сумма платежа": -200.0},
        {"Номер карты": "1111222233334444", "Сумма платежа": -300.0},
    ]

    result = get_card_infos(transactions)

    expected = [{"last_digits": "4444", "total_spent": 600.0, "cashback": 6.0}]

    assert result == expected


def test_get_top_transactions_basic_functionality():
    """Тест основной функциональности - топ-5 по абсолютной сумме"""
    transactions = [
        {"Дата платежа": "2023-01-01", "Сумма платежа": -1000.0, "Категория": "Еда", "Описание": "Ресторан"},
        {"Дата платежа": "2023-01-02", "Сумма платежа": -500.0, "Категория": "Транспорт", "Описание": "Такси"},
        {"Дата платежа": "2023-01-03", "Сумма платежа": -2000.0, "Категория": "ЖКХ", "Описание": "Квартплата"},
        {"Дата платежа": "2023-01-04", "Сумма платежа": -300.0, "Категория": "Развлечения", "Описание": "Кино"},
        {"Дата платежа": "2023-01-05", "Сумма платежа": -1500.0, "Категория": "Магазин", "Описание": "Продукты"},
        {"Дата платежа": "2023-01-06", "Сумма платежа": -800.0, "Категория": "Связь", "Описание": "Интернет"},
    ]

    result = get_top_transactions(transactions)

    # Должны вернуться 5 самых больших по абсолютной сумме
    expected_order = [-2000.0, -1500.0, -1000.0, -800.0, -500.0]
    assert len(result) == 5
    assert [t["amount"] for t in result] == expected_order


def test_less_than_five_transactions():
    """Тест когда транзакций меньше 5"""
    transactions = [
        {"Дата платежа": "2023-01-01", "Сумма платежа": -1000.0, "Категория": "Еда", "Описание": "Ресторан"},
        {"Дата платежа": "2023-01-02", "Сумма платежа": -500.0, "Категория": "Транспорт", "Описание": "Такси"},
    ]

    result = get_top_transactions(transactions)

    assert len(result) == 2
    assert [t["amount"] for t in result] == [-1000.0, -500.0]


def test_get_top_transactions_empty_transactions():
    """Тест с пустым списком транзакций"""
    result = get_top_transactions([])
    assert result == []


def test_positive_and_negative_amounts():
    """Тест с положительными и отрицательными суммами"""
    transactions = [
        {"Дата платежа": "2023-01-01", "Сумма платежа": -2000.0, "Категория": "Расход", "Описание": "Большой расход"},
        {"Дата платежа": "2023-01-02", "Сумма платежа": 1500.0, "Категория": "Доход", "Описание": "Зарплата"},
        {"Дата платежа": "2023-01-03", "Сумма платежа": -1000.0, "Категория": "Расход", "Описание": "Средний расход"},
        {"Дата платежа": "2023-01-04", "Сумма платежа": 800.0, "Категория": "Доход", "Описание": "Премия"},
    ]

    result = get_top_transactions(transactions)

    # Сортировка по абсолютному значению: 2000, 1500, 1000, 800
    expected_order = [-2000.0, 1500.0, -1000.0, 800.0]
    assert [t["amount"] for t in result] == expected_order


@patch("src.utils.requests.get")
def test_single_currency(mock_get):
    """Тест для одной валюты"""
    # Мокаем ответ API
    mock_response = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 91.23456}, "success": True}
    mock_get.return_value = mock_response

    result = get_current_exchange_rate(["USD"])

    expected = [{"currency": "USD", "rate": 91.23}]
    assert result == expected

    # Проверяем вызов API
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args[1]["params"]["base"] == "USD"
    assert call_args[1]["params"]["symbols"] == "RUB"


@patch("src.utils.requests.get")
def test_multiple_currencies(mock_get):
    """Тест для нескольких валют"""

    # Мокаем разные ответы для разных валют
    def side_effect(*args, **kwargs):
        mock_response = Mock()
        base_currency = kwargs["params"]["base"]
        rates = {"USD": 91.23, "EUR": 98.45, "GBP": 115.67}
        mock_response.json.return_value = {"rates": {"RUB": rates[base_currency]}, "success": True}
        return mock_response

    mock_get.side_effect = side_effect

    result = get_current_exchange_rate(["USD", "EUR", "GBP"])

    expected = [
        {"currency": "USD", "rate": 91.23},
        {"currency": "EUR", "rate": 98.45},
        {"currency": "GBP", "rate": 115.67},
    ]
    assert result == expected
    assert mock_get.call_count == 3


@patch("src.utils.requests.get")
def test_get_current_exchange_rate_rounding(mock_get):
    """Тест округления курса"""
    mock_response = Mock()
    mock_response.json.return_value = {"rates": {"RUB": 91.23456}, "success": True}
    mock_get.return_value = mock_response

    result = get_current_exchange_rate(["USD"])

    # Проверяем округление до 2 знаков
    assert result[0]["rate"] == 91.23
    assert isinstance(result[0]["rate"], float)


@patch("src.utils.requests.get")
def test_single_stock_success(mock_get):
    """Тест для одной успешной акции"""
    # Мокаем ответ API
    mock_response = Mock()
    mock_response.json.return_value = {
        "Global Quote": {
            "05. price": "255.4600",
            "01. symbol": "AAPL",
            "02. open": "254.1000",
            "03. high": "256.5000",
            "04. low": "253.0800",
        }
    }
    mock_get.return_value = mock_response

    result = get_stock(["AAPL"])

    expected = [{"stock": "AAPL", "price": 255.46}]
    assert result == expected

    # Проверяем вызов API
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args[1]["params"]["symbol"] == "AAPL"
    assert call_args[1]["params"]["function"] == "GLOBAL_QUOTE"


@patch("src.utils.requests.get")
def test_multiple_stocks_success(mock_get):
    """Тест для нескольких успешных акций"""

    # Мокаем разные ответы для разных акций
    def side_effect(*args, **kwargs):
        mock_response = Mock()
        symbol = kwargs["params"]["symbol"]
        prices = {"AAPL": "255.4600", "GOOGL": "246.5400", "TSLA": "440.4000"}
        mock_response.json.return_value = {"Global Quote": {"05. price": prices[symbol], "01. symbol": symbol}}
        return mock_response

    mock_get.side_effect = side_effect

    result = get_stock(["AAPL", "GOOGL", "TSLA"])

    expected = [
        {"stock": "AAPL", "price": 255.46},
        {"stock": "GOOGL", "price": 246.54},
        {"stock": "TSLA", "price": 440.40},
    ]
    assert result == expected
    assert mock_get.call_count == 3


@patch("src.utils.requests.get")
def test_get_stock_rounding(mock_get):
    """Тест округления цены"""
    mock_response = Mock()
    mock_response.json.return_value = {"Global Quote": {"05. price": "255.46789", "01. symbol": "AAPL"}}
    mock_get.return_value = mock_response

    result = get_stock(["AAPL"])

    # Проверяем округление до 2 знаков
    assert result[0]["price"] == 255.47
    assert isinstance(result[0]["price"], float)


def test_valid_date_conversion():
    """Тест корректного преобразования даты"""
    assert get_date("2023-12-31") == "31.12.2023"
    assert get_date("2024-01-01") == "01.01.2024"
    assert get_date("1999-12-31") == "31.12.1999"


def test_single_digit_dates():
    """Тест дат с однозначными числами"""
    assert get_date("2023-01-01") == "01.01.2023"
    assert get_date("2023-1-1") == "2023-1-1"  # Неправильный формат - вернется как есть
    assert get_date("2023-09-05") == "05.09.2023"


def test_invalid_dates():
    """Тест невалидных дат"""
    # Несуществующие даты
    assert get_date("2023-02-30") == "2023-02-30"  # 30 февраля не существует
    assert get_date("2023-13-01") == "2023-13-01"  # 13 месяца не существует
    assert get_date("2023-00-01") == "2023-00-01"  # 0 месяца не существует


def test_basic_date_filtering():
    """Тест базовой фильтрации по датам"""
    data = [
        {"Дата платежа": "01.01.2023", "Сумма": 100},
        {"Дата платежа": "15.01.2023", "Сумма": 200},
        {"Дата платежа": "31.01.2023", "Сумма": 300},
        {"Дата платежа": "01.02.2023", "Сумма": 400},
    ]

    result = filter_by_date(data, "01.01.2023", "31.01.2023")

    expected = [
        {"Дата платежа": "01.01.2023", "Сумма": 100},
        {"Дата платежа": "15.01.2023", "Сумма": 200},
        {"Дата платежа": "31.01.2023", "Сумма": 300},
    ]

    assert result == expected


def test_filter_by_date_empty_result():
    """Тест когда нет данных в указанном диапазоне"""
    data = [
        {"Дата платежа": "01.01.2023", "Сумма": 100},
        {"Дата платежа": "01.02.2023", "Сумма": 200},
    ]

    result = filter_by_date(data, "15.01.2023", "20.01.2023")
    assert result == []


def test_boundary_dates():
    """Тест граничных дат"""
    data = [
        {"Дата платежа": "01.01.2023", "Сумма": 100},
        {"Дата платежа": "15.01.2023", "Сумма": 200},
        {"Дата платежа": "31.01.2023", "Сумма": 300},
    ]

    # Включая границы
    result = filter_by_date(data, "01.01.2023", "31.01.2023")
    assert len(result) == 3

    # Исключая границы
    result = filter_by_date(data, "02.01.2023", "30.01.2023")
    assert len(result) == 1
    assert result[0]["Сумма"] == 200
