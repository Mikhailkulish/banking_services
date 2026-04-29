from typing import Any, Dict, List

import pytest

from src.masks import get_mask_account, get_mask_card_number


# Тестирование функции get_mask_card_number
# Фикстура стандартного номера карты
@pytest.fixture
def standart_card_number() -> int:
    return 1234567890123456


# Параметризация для корректных 16-значных номеров
@pytest.mark.parametrize(
    "card_number, expected_mask",
    [
        (1234567890123456, "1234 56** **** 3456"),
        (1111222233334444, "1111 22** **** 4444"),
        (9876543210987654, "9876 54** **** 7654"),
        ("0000111122223333", "0000 11** **** 3333"),
        (9999999999999999, "9999 99** **** 9999"),
        (1234123412341234, "1234 12** **** 1234"),
    ],
)
def test_valid_card_masking(card_number: str, expected_mask: str) -> None:
    """Тестирует корректное маскирование валидных 16-значных номеров карт"""
    assert get_mask_card_number(card_number) == expected_mask


# Параметризация для строкового ввода (с пробелами, дефисами)
@pytest.mark.parametrize(
    "card_number_str, expected_mask",
    [
        ("1234567890123456", "1234 56** **** 3456"),
        (" 1234567890123456 ", "1234 56** **** 3456"),  # с пробелами по краям
        ("1234 5678 9012 3456", "1234 56** **** 3456"),  # с пробелами внутри
        ("1234-5678-9012-3456", "1234 56** **** 3456"),  # с дефисами
        ("1234 56-7890-123456", "1234 56** **** 3456"),  # смешанный формат
    ],
)
def test_string_input_with_valid_card(card_number_str: str, expected_mask: str) -> None:
    """Тестирует обработку строкового ввода с валидным номером карты"""
    assert get_mask_card_number(card_number_str) == expected_mask


# Параметризация теста на отсутствие номера карты
@pytest.mark.parametrize("invalid_input", [None, "", "   ", "\t\n"])
def test_missing_card_number(invalid_input: str) -> None:
    """Тестирует обработку случая, когда номер карты отсутствует"""
    result = get_mask_card_number(invalid_input)
    assert "Не указан номер карты" == result


# Параметризация теста на неправильную длину
@pytest.mark.parametrize(
    "card_number, expected_length",
    [
        (123456789012, 12),  # 12 цифр
        (1234567890123, 13),  # 13 цифр
        (123456789012345, 15),  # 15 цифр
        (12345678901234567, 17),  # 17 цифр
        (123456789012345678, 18),  # 18 цифр
        (1234567890123456789, 19),  # 19 цифр
        (1, 1),  # 1 цифра
        (0, 1),  # 0
    ],
)
def test_invalid_length(card_number: str, expected_length: int) -> None:
    """Тестирует обработку номеров с неправильной длиной"""
    result = get_mask_card_number(card_number)
    expected_message = f"Номер карты должен состоять из 16 цифр. Получено {expected_length}"
    assert result == expected_message


# Параметризация теста на некорректные символы
@pytest.mark.parametrize(
    "invalid_input",
    [
        "abcd1234efgh5678",
        "1234abcd5678efgh",
        "1234 5678 9012 345O",  # буква O вместо 0
        "123456789012345a",
        "12.34567890123456",
        "1234-5678-9012-345X",
    ],
)
def test_non_digit_input(invalid_input: str) -> None:
    """Тестирует обработку ввода, содержащего нецифровые символы"""
    result = get_mask_card_number(invalid_input)
    assert result == "Номер карты должен содержать исключительно цифры"


# Тестирование функции get_mask_account
# Фикстуры для тестовых данных
@pytest.fixture
def valid_account_numbers() -> Dict[str, str]:
    """Фикстура с валидными номерами счетов"""
    return {
        "12345678901234567890": "**7890",
        "73654108430135874305": "**4305",
        "12341234123412341234": "**1234",
        "12340000000000000000": "**0000",
    }


@pytest.fixture
def invalid_account_numbers() -> List[str]:
    """Фикстура с невалидными номерами счетов"""
    return ["", "   ", "123", "12", "abc", "12ab34", "12 34"]


# Параметризация теста для валидных номеров счетов
@pytest.mark.parametrize(
    "account_number, expected",
    [
        ("12345678901234567890", "**7890"),
        ("73654108430135874305", "**4305"),
        ("12341234123412341234", "**1234"),
        ("00000000000000000000", "**0000"),
    ],
)
def test_get_mask_account_valid(account_number: str, expected: str) -> None:
    """Тестирует валидные номера счетов"""
    assert get_mask_account(account_number) == expected


# Параметризация теста для невалидных номеров счетов
@pytest.mark.parametrize(
    "account_number, expected_exception",
    [
        ("", ValueError),
        ("   ", ValueError),
        ("123", ValueError),
        ("12", ValueError),
        ("abc", ValueError),
        ("12ab34", ValueError),
        ("12 34", ValueError),
        ("1" * 1000, ValueError),
    ],
)
def test_get_mask_account_invalid(account_number: str, expected_exception: type[Exception]) -> None:
    """Тестирует невалидные номера счетов"""
    with pytest.raises(expected_exception):
        get_mask_account(account_number)


# Параметризация теста по обработке числовых данных
@pytest.mark.parametrize(
    "account_number, expected",
    [
        (12345678901234567890, "**7890"),  # целое число
        ("00000000000000001234", "**1234"),  # 20 символов с ведущими нулями
        ("73654108430135874305", "**4305"),  # 20 символов
    ],
)
def test_get_mask_account_numeric_input(account_number: str, expected: str) -> None:
    """Тестирует обработку числовых входных данных"""
    assert get_mask_account(account_number) == expected


# Параметризация теста по обработке неподдерживаемых типов данных
@pytest.mark.parametrize(
    "account_number",
    [
        None,
        [1, 2, 3, 4],
        {"number": "1234"},
    ],
)
def test_get_mask_account_wrong_type(account_number: Any) -> None:
    """Тестирует обработку неподдерживаемых типов данных"""
    with pytest.raises(TypeError):
        get_mask_account(account_number)


def test_get_mask_account_with_fixture(valid_account_numbers: Dict[str, str]) -> None:
    """Тестирует маскировку номера счета с использованием фикстуры"""
    for account, expected_mask in valid_account_numbers.items():
        assert get_mask_account(account) == expected_mask


def test_get_mask_account_edge_cases() -> None:
    """Тестирует обработку граничных случаев"""
    # Номер с ведущими нулями
    assert get_mask_account("00001234123412341234") == "**1234"

    # Номер только из нулей
    assert get_mask_account("00000000000000000000") == "**0000"
