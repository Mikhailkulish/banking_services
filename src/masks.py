def get_mask_card_number(card_number: int | str | None) -> str:
    """Функция, которая выдает маску карты"""
    if card_number is None:
        return "Не указан номер карты"

    card_number_str: str = str(card_number).replace(" ", "").replace("-", "")

    if not card_number_str or card_number_str.isspace():
        return "Не указан номер карты"

    if not card_number_str.isdigit():
        return "Номер карты должен содержать исключительно цифры"

    if len(card_number_str) != 16:
        return f"Номер карты должен состоять из 16 цифр. Получено {len(card_number_str)}"

    mask_card_number: str = card_number_str[:4] + " " + card_number_str[4:6] + "** **** " + card_number_str[12:]

    return mask_card_number


def get_mask_account(account_number: str) -> str:
    """Функция, которая выдает маску номера счета"""
    if account_number is None:
        raise TypeError("Номер счета не может быть None")

    if not isinstance(account_number, (str, int)):
        raise TypeError(f"Номер счета должен быть строкой или числом. Получен тип: {type(account_number).__name__}")

    try:
        account_number_str: str = str(account_number).strip()  # Если передан иной тип данных, кроме строки

    except Exception as e:
        raise TypeError(f"Невозможно преобразовать в строку: {e}")

    if not account_number_str:
        raise ValueError("Номер счета не может быть пустым")

    if len(account_number_str) != 20:
        raise ValueError(f"Номер счета должен содержать 20 символов. Получено: {len(account_number_str)}")

    if not account_number_str.isdigit():
        raise ValueError("Номер счета должен содержать только цифры")

    mask_account: str = "**" + account_number_str[-4:]

    return mask_account
