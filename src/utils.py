import requests
import datetime
import json
import pandas as pd
import os
from typing import Dict, List
import pprint
from dotenv import load_dotenv


load_dotenv("../.env")


API_KEY_FOR_CURRENT_EXCHANGE_RATE = os.getenv("API_KEY_FOR_CURRENT_EXCHANGE_RATE")
API_KEY_ALPHA_VANTAGE= os.getenv("API_KEY_ALPHA_VANTAGE")


def get_greeting() -> str:

    massage = ""

    now_hour = datetime.datetime.now().hour
    if 6 <= now_hour <=12:
        print("Доброе утро!")
    elif 12 < now_hour <= 18:
        print("Добрый день!")
    elif 18 < now_hour <= 24:
        print("Добрый вечер!")
    else:
        print("Доброй ночи!")
        return massege


def read_transactions_xlsx(file_path:str) -> list[dict]:
    xlsx_data = pd.read_excel(file_path)
    return xlsx_data.to_dict(orient="records")


def get_last_four(input_string:str) -> str:
    if input_string:
        return input_string[-4:]
    return "None"


def get_cashback(total_spent:float) -> float:
    return round(total_spent/100, 2)


def filter_by_state(data: list[dict], state: str = "OK") -> list[dict]:
    if not data:
        raise ValueError("Пустой список")

    new_data = list()

    for item in data:
        if item.get("Статус") == state:
            new_data.append(item)

    return new_data


def get_top_transactions(transactions: list[dict]) -> list[dict]:
    data = sorted(transactions, key=lambda x: abs(x['Сумма платежа']), reverse=True)[:5]
    result = []
    for i, transaction in enumerate(data, 1):
        transaction_info = dict(
            date=transaction['Дата платежа'],
            amount=transaction['Сумма платежа'],
            category=transaction['Категория'],
            description=transaction['Описание'],
        )
        result.append(transaction_info)
    return result


def get_current_exchange_rate(currency_code: str) -> float:
    """
    Функция, которая возвращает текущий курс
    """

    url = "https://api.apilayer.com/exchangerates_data/latest"

    headers = {"apikey": API_KEY_FOR_CURRENT_EXCHANGE_RATE}
    params = {"symbols": "RUB", "base": {currency_code}}

    response = requests.get(url, headers=headers, params=params)

    response_to_float = float(response.json()["rates"]["RUB"])
    return round(response_to_float, 2)


def get_stocs(stock: str) -> float:

    url = "https://www.alphavantage.co/query"

    params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": API_KEY_ALPHA_VANTAGE}
    response = requests.get(url, params=params)

    response_to_float = float(response.json()["Global Quote"]["05.      price"])
    return round(response_to_float, 2)


print(get_stocs("AMZN"))
# print(get_current_exchange_rate("USD"))
# data_temp = read_transactions_xlsx("../data/operations.xlsx")
# filter_date = filter_by_state(data_temp, "OK")
# pprint.pprint(get_top_transactions(filter_date))