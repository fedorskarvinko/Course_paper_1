import json
from unittest.mock import Mock, patch

from src.views import main_page


@patch("src.views.datetime")
@patch("src.views.get_date")
@patch("src.views.read_transactions_xlsx")
@patch("src.views.filter_by_date")
@patch("src.views.filter_by_state")
@patch("src.views.load_json_data")
@patch("src.views.get_greeting")
@patch("src.views.get_card_infos")
@patch("src.views.get_top_transactions")
@patch("src.views.get_current_exchange_rate")
@patch("src.views.get_stock")
def test_main_page_returns_json_string(
    mock_get_stock,
    mock_get_exchange_rate,
    mock_get_top_transactions,
    mock_get_card_infos,
    mock_get_greeting,
    mock_load_json_data,
    mock_filter_by_state,
    mock_filter_by_date,
    mock_read_transactions_xlsx,
    mock_get_date,
    mock_datetime,
):
    """Тест что функция возвращает JSON строку"""
    # Мокаем datetime
    mock_now = Mock()
    mock_now.hour = 14
    mock_datetime.now.return_value = mock_now

    mock_date_pars = Mock()
    mock_date_pars.year = 2023
    mock_date_pars.month = 1
    mock_datetime.strptime.return_value = mock_date_pars

    mock_start_of_month_pars = Mock()
    mock_datetime.return_value = mock_start_of_month_pars
    mock_datetime.strftime.return_value = "2023-01-01 00:00:00"

    # Мокаем функции
    mock_get_date.side_effect = lambda x: {"2021-01-20 15:25:13": "20.01.2021", "2023-01-01 00:00:00": "01.01.2023"}[x]

    mock_read_transactions_xlsx.return_value = [{"test": "data"}]
    mock_filter_by_date.return_value = [{"filtered": "data"}]
    mock_filter_by_state.return_value = [{"filtered_ok": "data"}]

    mock_load_json_data.return_value = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}

    mock_get_greeting.return_value = "Добрый день"
    mock_get_card_infos.return_value = [{"last_digits": "1234", "total_spent": 1000.0}]
    mock_get_top_transactions.return_value = [{"date": "01.01.2023", "amount": -100.0}]
    mock_get_exchange_rate.return_value = [{"currency": "USD", "rate": 91.23}]
    mock_get_stock.return_value = [{"stock": "AAPL", "price": 255.46}]

    # Вызываем функцию
    result = main_page("2021-01-20 15:25:13")

    # Проверяем что возвращается строка JSON
    assert isinstance(result, str)

    # Парсим JSON для проверки структуры
    parsed_result = json.loads(result)

    assert "greeting" in parsed_result
    assert "cards" in parsed_result
    assert "top_transactions" in parsed_result
    assert "currency_rates" in parsed_result
    assert "stock_prices" in parsed_result


@patch("src.views.datetime")
@patch("src.views.get_date")
@patch("src.views.read_transactions_xlsx")
@patch("src.views.filter_by_date")
@patch("src.views.filter_by_state")
@patch("src.views.load_json_data")
@patch("src.views.get_greeting")
@patch("src.views.get_card_infos")
@patch("src.views.get_top_transactions")
@patch("src.views.get_current_exchange_rate")
@patch("src.views.get_stock")
def test_json_structure_and_content(
    mock_get_stock,
    mock_get_exchange_rate,
    mock_get_top_transactions,
    mock_get_card_infos,
    mock_get_greeting,
    mock_load_json_data,
    mock_filter_by_state,
    mock_filter_by_date,
    mock_read_transactions_xlsx,
    mock_get_date,
    mock_datetime,
):
    """Тест структуры и содержимого JSON"""
    # Настраиваем моки
    mock_now = Mock()
    mock_now.hour = 10
    mock_datetime.now.return_value = mock_now
    mock_datetime.strptime.return_value = Mock(year=2023, month=1)
    mock_datetime.return_value = Mock()
    mock_datetime.strftime.return_value = "2023-01-01 00:00:00"

    mock_get_date.side_effect = lambda x: "01.01.2023" if "2023-01-01" in x else "20.01.2021"

    # Мокаем данные
    mock_read_transactions_xlsx.return_value = [{"transaction": "data"}]
    mock_filter_by_date.return_value = [{"filtered": "transaction"}]
    mock_filter_by_state.return_value = [{"ok_transaction": "data"}]

    mock_load_json_data.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

    mock_get_greeting.return_value = "Доброе утро"
    mock_get_card_infos.return_value = [{"last_digits": "5678", "total_spent": 500.0}]
    mock_get_top_transactions.return_value = [{"date": "15.01.2023", "amount": -200.0}]
    mock_get_exchange_rate.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_get_stock.return_value = [{"stock": "AAPL", "price": 250.0}]

    # Вызываем функцию
    result = main_page("2021-01-20 15:25:13")
    parsed_result = json.loads(result)

    # Проверяем содержимое
    assert parsed_result["greeting"] == "Доброе утро"
    assert len(parsed_result["cards"]) == 1
    assert parsed_result["cards"][0]["last_digits"] == "5678"
    assert parsed_result["currency_rates"][0]["currency"] == "USD"
    assert parsed_result["stock_prices"][0]["stock"] == "AAPL"
