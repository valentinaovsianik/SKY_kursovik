# Приложение SkyBank
Приложение для анализа транзакций, которые находятся в Excel-файле. Приложение должно генерировать JSON-данные для веб-страниц, формировать Excel-отчеты, а также предоставлять другие сервисы.

## Основные функции:

### `get_exchange_rates`
Получает данных о курсах валют с использованием API.

### `get_stock_prices`
Получает цены на акции на определенную дату.

### `get_greeting`
Функция приветствия в зависимости от времени суток.
.
### `analyze_transactions`
Анализирует транзакции из excel-файла и возвращает JSON-ответ.

### `get_top_transactions`
Возвращает топ-5 транзакций по сумме платежа в формате JSON от начала месяца до указанной даты.

### `main`
Главная функция, которая возвращает JSON-ответ с необходимыми параметрами (объединяет предыдущие функции).


### `search_transactions`
Функция простого поиска: ищет транзакции по строке запроса в описании или категории и возвращает результат в формате JSON.

### `report_to_file`
Декоратор для записи результата функции spending_by_category в файл.



## Логирование:
Проект использует библиотеку logging для записи логов.

## Установка:
Клонируйте репозиторий:
git clone git@github.com:valentinaovsianik/SKY_kursovik.git


## Документация:
Более подробная документация доступна в комментариях к функциям в коде.


## Покрытие тестами:

|Name                       |Stmts  | Miss| Cover|
|---------------------------|-------|-----|------|
|src\__init__.py            |    0  |   0 | 100% |
|src\main.py                |   27  |   3 |  89% |
|src\read_excel.py          |    7  |   0 | 100% |
|src\reports.py             |   43  |   7 |  84% |
|src\services.py            |   31  |   0 | 100% |
|src\utils.py               |   79  |  19 |  76% |
|src\views.py               |   72  |   6 |  92% |
|tests\__init__.py          |    0  |   0 | 100% |
|tests\test_main.py         |   22  |   0 | 100% |
|tests\test_read_excel.py   |   24  |   0 | 100% |
|tests\test_reports.py      |   22  |   0 | 100% |
|tests\test_services.py     |   34  |   0 | 100% |
|tests\test_utils.py        |  101  |   0 | 100% |
|tests\test_views.py        |   42  |   0 | 100% |
|---------------------------|-------|-----|------|
|TOTAL                      | 504   |  35 |  93% |


## Лицензия:
На проект распространяется [лицензия MIT](LICENSE).