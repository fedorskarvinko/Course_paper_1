import json
import os
from datetime import datetime
from functools import wraps
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import filter_by_date, get_date


def _default_name(func):
    return f"../reports/report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


def report_writer(arg=None):
    if callable(arg):  # @report_writer
        func = arg

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            _write_json(_default_name(func), result)
            return result

        return wrapper

    filename = None if arg is None else str(arg)

    def decorator(func):  # @report_writer("file.json") или @report_writer()
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            _write_json(filename or _default_name(func), result)
            return result

        return wrapper

    return decorator


def _write_json(filename, result):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    if pd is not None and isinstance(result, pd.DataFrame):
        result.to_json(filename, orient="records", force_ascii=False, indent=2)  # [web:46]
    else:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


@report_writer()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    end_date = datetime.now()
    if date is not None:
        end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()

    start_date = end_date - relativedelta(months=3)

    start_date_formated = datetime.strftime(start_date, "%Y-%m-%d %H:%M:%S")
    end_date_formated = datetime.strftime(end_date, "%Y-%m-%d %H:%M:%S")

    start_date_str = get_date(start_date_formated)
    end_date_str = get_date(end_date_formated)

    transactions_list = transactions.to_dict(orient="records")
    data_filtered = filter_by_date(transactions_list, start_date_str, end_date_str)

    data = pd.DataFrame(data_filtered)

    category_data = data[data["Категория"] == category]
    result = pd.DataFrame(category_data)
    return result
