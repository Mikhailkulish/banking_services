from src.utils import load_transactions
from src.reading_transactions import load_transactions_csv, load_transactions_excel
from src.processing import filter_by_state, sort_by_date
from src.generators import filter_by_currency, transaction_descriptions
from src.widget import get_date, mask_account_card


def main() -> None:
    """Обеспечивает работу приложения."""
    print("""Программа: Привет! Добро пожаловать в программу работы с банковскими транзакциями
          "Выберите необходимый пункт меню:
    1. Получить информацию о транзакциях из JSON-файла
    2. Получить информацию о транзакциях из CSV-файла
    3. Получить информацию о транзакциях из XLSX-файла""")

    user_request = input("Пользователь: ")

    while True:
        if user_request == "1":
            print("Программа: Для обработки выбран JSON-файл.")
            operations_data = load_transactions("data/operations.json")
            break
        elif user_request == "2":
            print("Программа: Для обработки выбран CSV-файл.")
            operations_data = load_transactions_csv("data/transactions.csv")
            break
        elif user_request == "3":
            print("Программа: Для обработки выбран XLSX-файл.")
            operations_data = load_transactions_excel("data/transactions_excel.xlsx")
            break
        else:
            print(f"Выбор {user_request} неверный! Укажите пункт меню из предложенных вариантов.")
            user_request = input("Пользователь: ")

    print("""Программа: Введите статус, по которому необходимо выполнить фильтрацию.
    Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING""")
    user_status = input("Пользователь: ").upper()

    while True:
        if user_status in ["EXECUTED", "CANCELED", "PENDING"]:
            filter_data = filter_by_state(operations_data, state=user_status)
            print(f"Программа: Операции отфильтрованы по статусу '{user_status}'")
            break
        else:
            print(f"""Программа: Статус операции {user_status} недоступен.
                    Введите статус, по которому необходимо выполнить фильтрацию.
                    Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING""")
            user_status = input("Пользователь: ").upper()

    print("Программа: Отсортировать операции по дате? Да/Нет")
    transaction_dates_user = input("Пользователь: ").lower()

    while True:
        if transaction_dates_user == "да":
            print("Отсортировать по возрастанию или по убыванию?")
            transaction_dates_user_direction = input("Пользователь: ").lower()
            if transaction_dates_user_direction == "по возрастанию":
                transaction_sorted_date = sort_by_date(filter_data, descending=False)  # Исправлено: False = по возрастанию
                break
            elif transaction_dates_user_direction == "по убыванию":
                transaction_sorted_date = sort_by_date(filter_data, descending=True)  # Исправлено: True = по убыванию
                break
            else:
                print(f'Выбор {transaction_dates_user_direction} отсутствует. Выберите направление сортировки')
                # Продолжаем цикл, не выходя из него
                continue
        elif transaction_dates_user == "нет":  # Исправлено: было transaction_dates_user_direction
            transaction_sorted_date = filter_data
            break
        else:
            print(f'Выбор {transaction_dates_user} отсутствует. Укажите необходимость сортировки по дате')
            transaction_dates_user = input("Пользователь: ").lower()

    print("Программа: Выводить только рублевые транзакции? Да/Нет")
    ruble_user = input("Пользователь: ").lower()

    while True:
        if ruble_user == "да":
            ruble_transactions = list(filter_by_currency(transaction_sorted_date, "RUB"))
            break
        elif ruble_user == "нет":
            ruble_transactions = transaction_sorted_date
            break
        else:
            print(f"Выбор {ruble_user} неверный. Укажите 'да' или 'нет'")
            ruble_user = input("Пользователь: ").lower()

    print("Программа: Отфильтровать список транзакций по определенному слову в описании? Да/нет")
    word_user = input("Пользователь: ").lower()

    # Итоговый список транзакций после всех фильтраций
    final_transactions = ruble_transactions.copy()

    while True:
        if word_user == "да":
            keyword = input("Введите слово для фильтрации описаний: ")
            # Исправлено: безопасная фильтрация без ручного вызова next()
            filtered_by_word = []
            for transaction in ruble_transactions:
                description = transaction.get("description", "")
                if keyword.lower() in description.lower():
                    filtered_by_word.append(transaction)
            final_transactions = filtered_by_word
            break
        elif word_user == "нет":
            final_transactions = ruble_transactions
            break
        else:
            print(f"Выбор {word_user} некорректен. Укажите 'да' или 'нет'")
            word_user = input("Пользователь: ").lower()

    print("Программа: Распечатываю итоговый список транзакций...")
    # Проверяем, есть ли транзакции в выборке
    if not final_transactions:
        print("Программа: Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
    else:
        print(f"Программа: \nВсего банковских операций в выборке: {len(final_transactions)}\n")

        # Выводим транзакции, используя ТОЛЬКО существующие функции
        for transaction in final_transactions:
            # Используем get_date для форматирования даты
            date_str = transaction.get("date", "")
            try:
                formatted_date = get_date(date_str)
            except (IndexError, TypeError, KeyError):
                formatted_date = date_str.split('T')[0] if 'T' in date_str else date_str

            # Получаем описание
            description = transaction.get("description", "Описание отсутствует")

            # Формируем строку перевода, используя mask_account_card
            from_to = ""
            if "from" in transaction and transaction["from"]:
                from_account = mask_account_card(transaction["from"])
                from_to = from_account

            if "to" in transaction and transaction["to"]:
                to_account = mask_account_card(transaction["to"])
                if from_to:
                    from_to += f" -> {to_account}"
                else:
                    from_to = to_account

            # Получаем сумму и валюту
            operation_amount = transaction.get("operationAmount", {})
            if operation_amount:
                amount = operation_amount.get("amount", "0")
                currency = operation_amount.get("currency", {})
                currency_code = currency.get("code", "")
                if currency_code == "RUB":
                    currency_code = "руб."
            else:
                amount = transaction.get("amount", "0")
                currency_code = transaction.get("currency", {})
                if isinstance(currency_code, dict):
                    currency_code = currency_code.get("code", "")
                if currency_code == "RUB":
                    currency_code = "руб."

            # Выводим транзакцию
            print(f"{formatted_date} {description}")
            if from_to:
                print(from_to)
            print(f"Сумма: {amount} {currency_code}")
            print("-" * 50)  # Добавлен разделитель для лучшей читаемости


if __name__ == "__main__":
    main()
