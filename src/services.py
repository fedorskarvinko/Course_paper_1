import json
import logging
from pathlib import Path

from src.utils import read_transactions_xlsx

MODULE_DIR = Path(__file__).resolve().parent
LOG_DIR = MODULE_DIR.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
log_file = LOG_DIR / "services.log"
file_handler = logging.FileHandler(log_file, mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def simple_search(search_string: str, file_path: str) -> str:
    """
    Возвращает результат поиска по категориям и описанию
    """

    data = read_transactions_xlsx(file_path)

    new_data = list()

    search_string_pattern = search_string.lower()
    for item in data:
        if (
            search_string_pattern in str(item.get("Описание")).lower()
            or search_string_pattern in str(item.get("Категория")).lower()
        ):
            new_data.append(item)
    logger.info("Search is done")

    json_string = json.dumps(new_data, ensure_ascii=False, indent=2)
    return json_string
