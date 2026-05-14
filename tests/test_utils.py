import pytest
import json
from unittest.mock import mock_open, patch
from src.utils import load_transactions  # замените your_module на имя вашего модуля


# Фикстуры
@pytest.fixture
def valid_transactions():
    """Фикстура с валидными данными транзакций"""
    return [
        {"id": 1, "amount": 100, "description": "Purchase"},
        {"id": 2, "amount": 250.5, "description": "Withdrawal"},
        {"id": 3, "amount": 50, "description": "Transfer"},
    ]


@pytest.fixture
def temp_json_file(tmp_path, valid_transactions):
    """Фикстура, создающая временный JSON-файл с данными"""
    file_path = tmp_path / "test_operations.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(valid_transactions, f)
    return str(file_path)


@pytest.fixture
def empty_file(tmp_path):
    """Фикстура, создающая пустой файл"""
    file_path = tmp_path / "empty_file.json"
    with open(file_path, "w", encoding="utf-8") as f:
        pass  # создаем пустой файл
    return str(file_path)


# Тесты
def test_successful_load(temp_json_file, valid_transactions):
    """Тест успешной загрузки валидного JSON-файла"""
    result = load_transactions(temp_json_file)
    assert result == valid_transactions
    assert isinstance(result, list)
    assert len(result) == 3


def test_empty_file(empty_file):
    """Тест загрузки пустого файла"""
    result = load_transactions(empty_file)
    assert result == []
    assert isinstance(result, list)


def test_file_not_found():
    """Тест при отсутствии файла"""
    result = load_transactions("non_existent_file.json")
    assert result == []
    assert isinstance(result, list)


def test_invalid_json(tmp_path):
    """Тест загрузки файла с невалидным JSON"""
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{invalid json content")

    result = load_transactions(str(file_path))
    assert result == []
    assert isinstance(result, list)


def test_data_is_not_list(tmp_path):
    """Тест, когда JSON содержит не список, а словарь"""
    file_path = tmp_path / "dict_data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"key": "value", "data": [1, 2, 3]}, f)

    result = load_transactions(str(file_path))
    assert result == []
    assert isinstance(result, list)


def test_empty_list_in_file(tmp_path):
    """Тест, когда JSON содержит пустой список"""
    file_path = tmp_path / "empty_list.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([], f)

    result = load_transactions(str(file_path))
    assert result == []
    assert isinstance(result, list)


# Параметризованные тесты
@pytest.mark.parametrize(
    "test_data",
    [
        [{"id": 1}],
        [{"id": 1, "amount": 100}, {"id": 2}],
        [],
        [{"transaction": "value"}],
        [{"id": 1, "amount": 100, "category": "food"}],
    ],
)
def test_various_valid_lists(tmp_path, test_data):
    """Параметризованный тест для различных валидных списков"""
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    result = load_transactions(str(file_path))
    assert result == test_data
    assert isinstance(result, list)


def test_unicode_content(tmp_path):
    """Тест загрузки файла с Unicode символами"""
    test_data = [{"id": 1, "description": "Покупка продуктов"}, {"id": 2, "description": "Снятие наличных €100"}]
    file_path = tmp_path / "unicode.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False)

    result = load_transactions(str(file_path))
    assert result == test_data
    assert result[0]["description"] == "Покупка продуктов"


def test_large_file(tmp_path):
    """Тест загрузки большого файла"""
    test_data = [{"id": i, "amount": i * 100} for i in range(1000)]
    file_path = tmp_path / "large.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    result = load_transactions(str(file_path))
    assert len(result) == 1000
    assert result[0]["id"] == 0
    assert result[-1]["id"] == 999


# Тесты с моками (без использования реальных файлов)
def test_file_with_permission_error():
    """Тест при ошибке доступа к файлу"""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = PermissionError("Access denied")
        result = load_transactions("any_path.json")
        assert result == []


def test_json_decode_error_with_mock():
    """Тест ошибки JSONDecodeError"""
    with patch("os.path.getsize", return_value=100):
        with patch("json.load", side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            result = load_transactions("any_path.json")
            assert result == []


def test_io_error_with_mock():
    """Тест ошибки IOError"""
    with patch("os.path.getsize", return_value=100):
        with patch("builtins.open", side_effect=IOError("Cannot read file")):
            result = load_transactions("any_path.json")
            assert result == []
