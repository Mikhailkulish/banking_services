card_number = int(input("Введите номер карты: "))


def get_mask_card_number(card_number: int) -> str:
    """Функция, которая выдает маску карты"""
    card_number_str: str = str(card_number)
    mask_card_number: str = (card_number_str[:4] + " " + card_number_str[4:6] + "** **** " +
                             card_number_str[12:])

    return mask_card_number


account_number = int(input("Введите номер счета: "))


def get_mask_account(account_number: str) -> str:
    """Функция, которая выдает маску номера счета"""
    account_number_str: str = str(account_number)
    mask_account: str = "**" + account_number_str[-4:]

    return mask_account
