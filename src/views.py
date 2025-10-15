import json
from datetime import datetime
from typing import Any, Dict

from src.utils import (filter_by_date, filter_by_state, get_card_infos, get_current_exchange_rate, get_date,
                       get_greeting, get_stock, get_top_transactions, load_json_data, read_transactions_xlsx)


def main_page(date_string: str) -> str:
    """
    Возвращает информацию для главной страницы
    """

    date_end_of_month = get_date(date_string)

    date_pars = datetime.strptime(date_end_of_month, "%d.%m.%Y")
    start_of_month_pars = datetime(date_pars.year, date_pars.month, 1)
    start_of_month_str = datetime.strftime(start_of_month_pars, "%Y-%m-%d %H:%M:%S")
    date_start_of_month = get_date(start_of_month_str)

    transaction = read_transactions_xlsx("../data/operations.xlsx")

    filtered_transactions = filter_by_date(transaction, date_start_of_month, date_end_of_month)
    filtered_transactions = filter_by_state(filtered_transactions)

    user_settings = load_json_data("../user_settings.json")
    user_currencies = user_settings.get("user_currencies", [])
    user_stocks = user_settings.get("user_stocks", [])

    now_hour = datetime.now().hour
    data: Dict[str, Any] = {
        "greeting": get_greeting(now_hour),
        "cards": get_card_infos(filtered_transactions),
        "top_transactions": get_top_transactions(filtered_transactions),
        "currency_rates": get_current_exchange_rate(user_currencies),
        "stock_prices": get_stock(user_stocks),
    }
    result = json.dumps(data, ensure_ascii=False, indent=2)
    return result
