import logging
import os

# Указываем путь к существующей папке с логами
log_dir = "logs"
log_file = os.path.join(log_dir, "masks.log")

# Очищаем файл логов при запуске (перезаписываем)
with open(log_file, "w") as f:
    pass

# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем обработчик файла
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Создаем форматтер
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)


def get_mask_card_number(card_number: int | str | None) -> str:
    """Функция, которая выдает маску карты"""
    logger.info(f"Вызов функции get_mask_card_number с аргументом: {card_number}")

    if card_number is None:
        logger.warning("Не указан номер карты")
        return "Не указан номер карты"

    card_number_str: str = str(card_number).replace(" ", "").replace("-", "")

    if not card_number_str or card_number_str.isspace():
        logger.warning("Не указан номер карты")
        return "Не указан номер карты"

    if not card_number_str.isdigit():
        logger.error("Номер карты должен содержать исключительно цифры")
        return "Номер карты должен содержать исключительно цифры"

    if len(card_number_str) != 16:
        logger.error(f"Номер карты должен состоять из 16 цифр. Получено {len(card_number_str)}")
        return f"Номер карты должен состоять из 16 цифр. Получено {len(card_number_str)}"

    mask_card_number: str = card_number_str[:4] + " " + card_number_str[4:6] + "** **** " + card_number_str[12:]

    logger.info(f"get_mask_card_number успешно завершена. Результат: {mask_card_number}")
    return mask_card_number


def get_mask_account(account_number: str) -> str:
    """Функция, которая выдает маску номера счета"""
    logger.info(f"Вызов функции get_mask_account с аргументом: {account_number}")
    if account_number is None:
        logger.error("Номер счета не может быть None")
        raise TypeError("Номер счета не может быть None")

    if not isinstance(account_number, (str, int)):
        logger.error(f"Номер счета должен быть строкой или числом. Получен тип: {type(account_number).__name__}")
        raise TypeError(f"Номер счета должен быть строкой или числом. Получен тип: {type(account_number).__name__}")

    try:
        account_number_str: str = str(account_number).strip()  # Если передан иной тип данных, кроме строки

    except Exception as e:
        logger.error(f"Невозможно преобразовать в строку: {e}")
        raise TypeError(f"Невозможно преобразовать в строку: {e}")

    if not account_number_str:
        logger.error("Номер счета не может быть пустым")
        raise ValueError("Номер счета не может быть пустым")

    if len(account_number_str) != 20:
        logger.error(f"Номер счета должен содержать 20 символов. Получено: {len(account_number_str)}")
        raise ValueError(f"Номер счета должен содержать 20 символов. Получено: {len(account_number_str)}")

    if not account_number_str.isdigit():
        logger.error("Номер счета должен содержать только цифры")
        raise ValueError("Номер счета должен содержать только цифры")

    mask_account: str = "**" + account_number_str[-4:]

    logger.info(f"get_mask_account успешно завершена. Результат: {mask_account}")
    return mask_account
