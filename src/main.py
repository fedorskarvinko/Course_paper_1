import pandas as pd

from src.reports import spending_by_category
from src.services import simple_search
from src.utils import read_transactions_xlsx
from src.views import main_page

# проверка работы модуля views
print("проверка работы модуля views")
print(main_page("2021-10-30 15:12:30"))

# проверка работы модуля services
print("проверка работы модуля services")
print(simple_search("продукты", "../data/operations.xlsx"))

# проверка работы модуля reports
print("проверка работы модуля reports")

df = pd.DataFrame(read_transactions_xlsx("../data/operations.xlsx"))
print(spending_by_category(df, "Супермаркеты", "2021-10-30 15:12:30"))
