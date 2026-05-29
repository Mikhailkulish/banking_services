import os
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.reading_transactions import load_transactions_csv, load_transactions_excel

# Тестирование функции load_transactions_csv


@patch("os.path.exists")
def test_file_not_found(mock_exists: Mock) -> None:
    """Тест: файл не найден"""
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError) as exc_info:
        load_transactions_csv("/nonexistent/path.csv")

    assert "Файл не найден" in str(exc_info.value)


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_successful_load_with_default_path(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест успешной загрузки с путем по умолчанию"""
    mock_exists.return_value = True

    # Создаем мок для DictReader
    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "description", "amount", "currency", "category"]

    # Настройка итерации
    data = [
        {
            "date": "2024-01-15",
            "description": "Покупка продуктов",
            "amount": "1500.50",
            "currency": "RUB",
            "category": "Еда",
        },
        {
            "date": "2024-01-16",
            "description": "Оплата интернета",
            "amount": "890.00",
            "currency": "RUB",
            "category": "Услуги",
        },
    ]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert len(result) == 2
    assert result[0]["amount"] == 1500.50
    assert result[0]["currency"] == "RUB"
    assert result[1]["description"] == "Оплата интернета"


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_custom_path_handling(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: корректная обработка пользовательского пути"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date"]
    mock_reader.__iter__ = Mock(return_value=iter([]))
    mock_dict_reader.return_value = mock_reader

    custom_path: str = "/custom/path/transactions.csv"
    load_transactions_csv(custom_path)

    mock_open_file.assert_called_once_with(custom_path, "r", encoding="utf-8")


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_amount_conversion_to_float(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: преобразование amount в число с плавающей точкой"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "amount"]
    data = [
        {"date": "2024-01-15", "amount": "1500.50"},
        {"date": "2024-01-16", "amount": "890.00"},
        {"date": "2024-01-17", "amount": "0.00"},
    ]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert isinstance(result[0]["amount"], float)
    assert result[0]["amount"] == 1500.50
    assert result[1]["amount"] == 890.00
    assert result[2]["amount"] == 0.00


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_invalid_amount_handling(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: обработка некорректного значения amount (остается строкой)"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "amount"]
    data = [{"date": "2024-01-15", "amount": "invalid_amount"}, {"date": "2024-01-16", "amount": "890.00"}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert isinstance(result[0]["amount"], str)
    assert result[0]["amount"] == "invalid_amount"
    assert isinstance(result[1]["amount"], float)


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_string_stripping(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: удаление пробелов из ключей и значений"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = [" date ", " description ", " amount "]
    data = [{" date ": " 2024-01-15 ", " description ": " Покупка ", " amount ": " 1500.50 "}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert "date" in result[0]
    assert "description" in result[0]
    assert "amount" in result[0]
    assert result[0]["date"] == "2024-01-15"
    assert result[0]["description"] == "Покупка"
    assert result[0]["amount"] == 1500.50


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_empty_values_handling(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: обработка пустых значений"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "description", "amount"]
    data = [{"date": "2024-01-15", "description": "", "amount": ""}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert result[0]["description"] == ""
    assert result[0]["amount"] == ""


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_returns_list_of_dicts(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: функция возвращает список словарей"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "amount"]
    data = [{"date": "2024-01-15", "amount": "100"}, {"date": "2024-01-16", "amount": "200"}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)


@patch("os.path.dirname")
@patch("os.path.abspath")
@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_default_path_construction(
    mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock, mock_abspath: Mock, mock_dirname: Mock
) -> None:
    """Тест: правильное построение пути по умолчанию"""
    mock_exists.return_value = True

    mock_abspath.return_value = "/project/src/reading_transactions.py"
    mock_dirname.side_effect = ["/project/src", "/project"]

    mock_reader = Mock()
    mock_reader.fieldnames = ["date"]
    mock_reader.__iter__ = Mock(return_value=iter([]))
    mock_dict_reader.return_value = mock_reader

    load_transactions_csv()

    expected_path: str = os.path.join("/project", "data", "transactions.csv")
    mock_open_file.assert_called_once_with(expected_path, "r", encoding="utf-8")


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_missing_amount_field(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: отсутствие поля amount в строке"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "description", "currency"]
    data = [{"date": "2024-01-15", "description": "Покупка", "currency": "RUB"}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert "amount" not in result[0]
    assert result[0]["date"] == "2024-01-15"


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_numeric_values_other_than_amount(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: числовые значения в других полях не преобразуются"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "quantity", "price", "amount"]
    data = [{"date": "2024-01-15", "quantity": "5", "price": "100.50", "amount": "500.00"}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert isinstance(result[0]["quantity"], str)
    assert isinstance(result[0]["price"], str)
    assert isinstance(result[0]["amount"], float)


@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_empty_file_with_only_headers(mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock) -> None:
    """Тест: пустой файл (только заголовки)"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "amount"]
    mock_reader.__iter__ = Mock(return_value=iter([]))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert result == []


# ============== Параметризованные тесты ==============


@pytest.mark.parametrize(
    "amount_value,expected_type",
    [
        ("100.50", float),
        ("invalid", str),
        ("", str),
        ("0", float),
        ("1000", float),
        ("-50.75", float),
    ],
)
@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_amount_conversion_various_formats(
    mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock, amount_value: str, expected_type: type
) -> None:
    """Параметризованный тест различных форматов amount"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = ["date", "amount"]
    data = [{"date": "2024-01-15", "amount": amount_value}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert isinstance(result[0]["amount"], expected_type)


@pytest.mark.parametrize(
    "input_key,expected_key",
    [
        (" date ", "date"),
        ("description ", "description"),
        (" amount", "amount"),
        ("  currency  ", "currency"),
    ],
)
@patch("os.path.exists")
@patch("builtins.open")
@patch("csv.DictReader")
def test_key_stripping_variations(
    mock_dict_reader: Mock, mock_open_file: Mock, mock_exists: Mock, input_key: str, expected_key: str
) -> None:
    """Параметризованный тест удаления пробелов из ключей"""
    mock_exists.return_value = True

    mock_reader = Mock()
    mock_reader.fieldnames = [input_key]
    data = [{input_key: "test_value"}]
    mock_reader.__iter__ = Mock(return_value=iter(data))
    mock_dict_reader.return_value = mock_reader

    result: List[Dict[str, Any]] = load_transactions_csv()

    assert expected_key in result[0]
    assert result[0][expected_key] == "test_value"


# Тестирование функции load_transactions_excel


@patch("os.path.exists")
def test_not_found(mock_exists: Mock) -> None:
    """Тест: файл не найден"""
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError) as exc_info:
        load_transactions_excel("/nonexistent/path")

    assert "Файл не найден" in str(exc_info.value)


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_success_default_path(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест успешной загрузки с путем по умолчанию"""

    def exists_side_effect(path):
        return path.endswith(".xlsx")

    mock_exists.side_effect = exists_side_effect

    test_data = {
        "date": ["2024-01-15", "2024-01-16"],
        "description": ["Покупка продуктов", "Оплата интернета"],
        "amount": [1500.50, 890.00],
        "currency": ["RUB", "RUB"],
    }
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert len(result) == 2
    assert result[0]["amount"] == 1500.50
    assert result[0]["currency"] == "RUB"
    assert result[1]["description"] == "Оплата интернета"


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_load_with_xls_extension(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: загрузка файла с расширением .xls"""

    def exists_side_effect(path):
        return path.endswith(".xls")

    mock_exists.side_effect = exists_side_effect

    test_data = {"date": ["2024-01-15"], "amount": [100.50]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert len(result) == 1
    assert result[0]["amount"] == 100.50


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_load_with_xlsm_extension(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: загрузка файла с расширением .xlsm"""

    def exists_side_effect(path):
        return path.endswith(".xlsm")

    mock_exists.side_effect = exists_side_effect

    test_data = {"date": ["2024-01-15"], "amount": [100.50]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert len(result) == 1


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_custom_path_without_extension(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: пользовательский путь без указания расширения"""

    def exists_side_effect(path):
        return path == "/custom/path/file.xlsx"

    mock_exists.side_effect = exists_side_effect

    test_data = {"date": ["2024-01-15"], "amount": [100.50]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel("/custom/path/file")

    assert len(result) == 1


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_custom_path_with_extension(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: пользовательский путь с указанием расширения"""

    mock_exists.return_value = True

    test_data = {"date": ["2024-01-15"], "amount": [100.50]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel("/custom/path/file.xlsx")

    assert len(result) == 1
    mock_read_excel.assert_called_once_with("/custom/path/file.xlsx")


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_file_found_without_extension_direct(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: файл найден без расширения (прямая проверка)"""

    def exists_side_effect(path):
        if path == "/custom/path/file":
            return True
        return False

    mock_exists.side_effect = exists_side_effect

    test_data = {"date": ["2024-01-15"], "amount": [100.50]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel("/custom/path/file")

    assert len(result) == 1


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_nan_values_handling(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: обработка NaN значений"""

    mock_exists.return_value = True

    test_data = {"date": ["2024-01-15", "2024-01-16"], "description": ["Покупка", None], "amount": [1500.50, None]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert result[0]["description"] == "Покупка"
    assert result[1]["description"] is None
    assert result[1]["amount"] is None


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_timestamp_conversion(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: преобразование Timestamp в строку"""

    mock_exists.return_value = True

    test_data = {"date": [pd.Timestamp("2024-01-15"), pd.Timestamp("2024-01-16")], "amount": [100.50, 200.50]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert result[0]["date"] == "2024-01-15"
    assert result[1]["date"] == "2024-01-16"
    assert isinstance(result[0]["date"], str)


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_numeric_values_preserved(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: числовые значения остаются числами"""

    mock_exists.return_value = True

    test_data = {"integer": [100], "float": [100.50], "amount": [500.75]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    # Проверяем, что значения являются числами (int или float)
    assert isinstance(result[0]["integer"], (int, float))
    assert isinstance(result[0]["float"], (int, float))
    assert isinstance(result[0]["amount"], (int, float))

    # Проверяем сами значения
    assert float(result[0]["integer"]) == 100.0
    assert float(result[0]["float"]) == 100.50
    assert float(result[0]["amount"]) == 500.75


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_string_values_stripped(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: удаление пробелов из строковых значений"""

    mock_exists.return_value = True

    test_data = {"description": ["  Покупка  ", "  Оплата  "], "category": ["  Еда  ", None]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert result[0]["description"] == "Покупка"
    assert result[1]["description"] == "Оплата"
    assert result[0]["category"] == "Еда"


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_empty_string_values(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: обработка пустых строк"""

    mock_exists.return_value = True

    test_data = {"description": ["", "Текст"], "amount": [100, 200]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert result[0]["description"] == ""


@patch("os.path.exists")
def test_excel_read_error(mock_exists: Mock) -> None:
    """Тест: ошибка при чтении Excel файла"""

    mock_exists.return_value = True

    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.side_effect = Exception("Excel parsing error")

        with pytest.raises(Exception) as exc_info:
            load_transactions_excel()

        assert "Ошибка при чтении Excel файла" in str(exc_info.value)


@patch("os.path.dirname")
@patch("os.path.abspath")
@patch("os.path.exists")
@patch("pandas.read_excel")
def test_default_path_constr(mock_read_excel: Mock, mock_exists: Mock, mock_abspath: Mock, mock_dirname: Mock) -> None:
    """Тест: правильное построение пути по умолчанию"""

    # Просто говорим, что файл существует для любого пути
    mock_exists.return_value = True

    mock_abspath.return_value = "/project/src/reading_transactions.py"
    mock_dirname.side_effect = ["/project/src", "/project"]

    test_data = {"date": ["2024-01-15"], "amount": [100]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert len(result) == 1
    assert result[0]["date"] == "2024-01-15"
    assert result[0]["amount"] == 100


@patch("os.path.exists")
def test_no_valid_extension_found(mock_exists: Mock) -> None:
    """Тест: ни одно расширение не подошло"""

    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError) as exc_info:
        load_transactions_excel("/custom/path/file")

    assert "Файл не найден" in str(exc_info.value)
    assert ".xlsx" in str(exc_info.value)


# ============== Параметризованные тесты ==============


@pytest.mark.parametrize("extension", [".xlsx", ".xls", ".xlsm"])
@patch("os.path.exists")
@patch("pandas.read_excel")
def test_all_extensions(mock_read_excel: Mock, mock_exists: Mock, extension: str) -> None:
    """Параметризованный тест для всех поддерживаемых расширений"""

    def exists_side_effect(path):
        return path.endswith(extension)

    mock_exists.side_effect = exists_side_effect

    test_data = {"date": ["2024-01-15"], "amount": [100]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert len(result) == 1


@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        (pd.Timestamp("2024-01-15"), "2024-01-15"),
        (100.50, 100.50),
        (100, 100.0),
        ("  text  ", "text"),
        (None, None),
    ],
)
@patch("os.path.exists")
@patch("pandas.read_excel")
def test_value_conversions(mock_read_excel: Mock, mock_exists: Mock, input_value: Any, expected_output: Any) -> None:
    """Параметризованный тест преобразования различных типов значений"""

    mock_exists.return_value = True

    test_data = {"value": [input_value]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    if expected_output is None:
        assert result[0]["value"] is None
    else:
        # Сравниваем с приведением к float для чисел
        if isinstance(expected_output, float):
            assert float(result[0]["value"]) == expected_output
        else:
            assert result[0]["value"] == expected_output


@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        ("", ""),  # Пустая строка остается пустой
        ("  ", ""),  # Строка из пробелов становится пустой
        ("  text  ", "text"),  # Обрезаются пробелы по краям
        ("text", "text"),  # Обычная строка не меняется
        ("text with spaces", "text with spaces"),  # Внутренние пробелы сохраняются
    ],
)
@patch("os.path.exists")
@patch("pandas.read_excel")
def test_string_variations(mock_read_excel: Mock, mock_exists: Mock, input_value: str, expected_output: str) -> None:
    """Параметризованный тест различных строковых значений"""

    mock_exists.return_value = True

    test_data = {"description": [input_value]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert result[0]["description"] == expected_output


@patch("os.path.exists")
@patch("pandas.read_excel")
def test_multiple_rows_loading(mock_read_excel: Mock, mock_exists: Mock) -> None:
    """Тест: загрузка множества строк"""

    mock_exists.return_value = True

    test_data = {"date": [f"2024-01-{i:02d}" for i in range(1, 11)], "amount": [i * 100 for i in range(1, 11)]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df

    result: List[Dict[str, Any]] = load_transactions_excel()

    assert len(result) == 10
    assert result[0]["date"] == "2024-01-01"
    assert result[9]["amount"] == 1000
