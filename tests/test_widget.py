import pytest

from src.widget import get_date, mask_account_card


# Тестирование функции mask_account_card
# Параметризация данных для проверки карт и счетов, включая граничные случаи
@pytest.mark.parametrize(
    "input_str,expected",
    [
        # Карты
        ("Visa Platinum 1234567890123456", "Visa Platinum 1234 56** **** 3456"),
        ("Maestro 5432109876543210", "Maestro 5432 10** **** 3210"),
        ("Мир 2200123456789012", "Мир 2200 12** **** 9012"),
        ("MasterCard 5555666677778888", "MasterCard 5555 66** **** 8888"),
        ("Visa 1234 5678 9012 3456", "Visa 1234 56** **** 3456"),
        # Счета
        ("Счет 12345678901234567890", "Счет **7890"),
        ("счёт 98765432109876543210", "счёт **3210"),
        ("Расчетный счет 12345678901234567890", "Расчетный счет **7890"),
        # Граничные случаи
        ("", ""),
        ("Visa Platinum", "Visa Platinum"),
        ("1234567890123456", "1234 56** **** 3456"),
        (None, ""),
    ],
)
def test_mask_account_card(input_str: str, expected: str) -> None:
    """Тестирует данные по картам и счетам"""
    result = mask_account_card(input_str)
    assert result.strip() == expected


# Тестирование функции get_date
def test_get_date() -> None:
    """Тестирует корректность преобразования даты"""
    input_date: str = "2024-03-11T02:26:18.671407"
    expected_output: str = "11.03.2024"

    assert get_date(input_date) == expected_output
