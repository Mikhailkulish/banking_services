
from masks import get_mask_account, get_mask_card_number # type: ignore

str_bank_details = input("Введите данные о банковской карте или счете: ")


def mask_account_card(str_bank_details: str) -> str:
    """Функция обрабатывает информацию о картах и счетах"""
    list_bank_details = str_bank_details.split()
    list_name = []
    list_number = []
    for el in list_bank_details:
        if el.isdigit():
            list_number.append(el)
        else:
            list_name.append(el)

    str_name = " ".join(list_name)
    str_number = "".join(list_number)

    if "счет" in str_name.lower() or "счёт" in str_name.lower():
        result = get_mask_account(str_number)
    else:
        result = get_mask_card_number(str_number)

    return f"{str_name} {result}"


str_date = input("Введите дату в формате по стандарту ISO 8601: ")


def get_date(str_date: str) -> str:
    """Функция преобразует дату по стандарту ISO 8601 в формат "ДД.ММ.ГГГГ" """
    result = f"{str_date[8:10]}.{str_date[5:7]}.{str_date[:4]}"

    return result
