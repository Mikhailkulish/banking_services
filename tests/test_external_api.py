import pytest
from unittest.mock import Mock, patch
import requests
from src.external_api import convert_to_rub
import src.external_api  # импортируем модуль целиком для patch.object


@pytest.fixture(autouse=True)
def clear_cache():
    src.external_api._cache.clear()
    yield
    src.external_api._cache.clear()


# Тесты для RUB (без конвертации)
def test_rub_returns_same_amount():
    """RUB транзакции возвращают исходную сумму без изменений"""
    transaction = {"amount": 1000.50, "currency": "RUB"}
    result = convert_to_rub(transaction)
    assert result == 1000.50
    assert isinstance(result, float)


def test_rub_default_currency():
    """Если валюта не указана, считается что это RUB"""
    transaction = {"amount": 500}
    result = convert_to_rub(transaction)
    assert result == 500.0


def test_invalid_amount_type():
    """Проверка TypeError при нечисловом amount"""
    transaction = {"amount": "1000", "currency": "USD"}
    with pytest.raises(TypeError, match="Поле 'amount' должно быть числом"):
        convert_to_rub(transaction)


def test_negative_amount():
    """Проверка ValueError при отрицательной сумме"""
    transaction = {"amount": -100, "currency": "USD"}
    with pytest.raises(ValueError, match="Сумма транзакции не может быть отрицательной"):
        convert_to_rub(transaction)


def test_unsupported_currency():
    """Проверка ValueError при неподдерживаемой валюте"""
    transaction = {"amount": 100, "currency": "GBP"}
    with pytest.raises(ValueError, match="Неподдерживаемая валюта: GBP"):
        convert_to_rub(transaction)


# Тесты для конвертации USD
def test_usd_conversion_success():
    """Успешная конвертация USD в RUB"""
    # Настройка мока
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "rates": {"RUB": 75.50}
    }
    mock_response.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', return_value=mock_response) as mock_get:
        transaction = {"amount": 100, "currency": "USD"}
        result = convert_to_rub(transaction)

        assert result == 7550.0  # 100 * 75.50
        mock_get.assert_called_once()

        # Проверяем параметры запроса
        call_args = mock_get.call_args
        assert call_args[1]['params']['base'] == 'USD'
        assert call_args[1]['params']['symbols'] == 'RUB'


def test_eur_conversion_success():
    """Успешная конвертация EUR в RUB"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "rates": {"RUB": 90.25}
    }
    mock_response.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', return_value=mock_response) as mock_get:
        transaction = {"amount": 200, "currency": "EUR"}
        result = convert_to_rub(transaction)

        assert result == 18050.0  # 200 * 90.25
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['base'] == 'EUR'


# Тесты для кэширования
def test_cache_prevents_duplicate_api_calls():
    """Кэш предотвращает повторные API запросы"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "rates": {"RUB": 75.00}
    }
    mock_response.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', return_value=mock_response) as mock_get:
        # Первый вызов
        transaction1 = {"amount": 100, "currency": "USD"}
        result1 = convert_to_rub(transaction1)

        # Второй вызов с той же валютой
        transaction2 = {"amount": 200, "currency": "USD"}
        result2 = convert_to_rub(transaction2)

        assert result1 == 7500.0
        assert result2 == 15000.0
        # API должен быть вызван только один раз
        mock_get.assert_called_once()


def test_cache_separate_for_different_currencies():
    """Кэш раздельный для разных валют"""
    mock_response_usd = Mock()
    mock_response_usd.json.return_value = {
        "success": True,
        "rates": {"RUB": 75.00}
    }
    mock_response_usd.raise_for_status = Mock()

    mock_response_eur = Mock()
    mock_response_eur.json.return_value = {
        "success": True,
        "rates": {"RUB": 90.00}
    }
    mock_response_eur.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', side_effect=[mock_response_usd, mock_response_eur]) as mock_get:
        # Конвертация USD
        result_usd = convert_to_rub({"amount": 100, "currency": "USD"})
        # Конвертация EUR
        result_eur = convert_to_rub({"amount": 100, "currency": "EUR"})

        assert result_usd == 7500.0
        assert result_eur == 9000.0
        # API должен быть вызван дважды (по разу для каждой валюты)
        assert mock_get.call_count == 2


# Тесты для обработки ошибок API
def test_api_returns_error():
    """Обработка ошибки от API"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": False,
        "error": "Invalid API key"
    }
    mock_response.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', return_value=mock_response):
        transaction = {"amount": 100, "currency": "USD"}
        with pytest.raises(ValueError, match="API вернул ошибку: Invalid API key"):
            convert_to_rub(transaction)


def test_connection_error():
    """Обработка ошибки соединения"""
    with patch.object(src.external_api.requests, 'get', side_effect=requests.exceptions.ConnectionError("Connection failed")):
        transaction = {"amount": 100, "currency": "USD"}
        with pytest.raises(ConnectionError, match="Не удалось получить курс валюты USD"):
            convert_to_rub(transaction)


def test_timeout_error():
    """Обработка таймаута"""
    with patch.object(src.external_api.requests, 'get', side_effect=requests.exceptions.Timeout("Request timed out")):
        transaction = {"amount": 100, "currency": "EUR"}
        with pytest.raises(ConnectionError, match="Не удалось получить курс валюты EUR"):
            convert_to_rub(transaction)


def test_http_error():
    """Обработка HTTP ошибки"""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

    with patch.object(src.external_api.requests, 'get', return_value=mock_response):
        transaction = {"amount": 100, "currency": "USD"}
        with pytest.raises(ConnectionError, match="Не удалось получить курс валюты USD"):
            convert_to_rub(transaction)


# Тесты для типов данных и граничных случаев
def test_zero_amount():
    """Проверка нулевой суммы"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "rates": {"RUB": 75.00}
    }
    mock_response.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', return_value=mock_response):
        transaction = {"amount": 0, "currency": "USD"}
        result = convert_to_rub(transaction)
        assert result == 0.0


def test_integer_amount():
    """Проверка целочисленного amount"""
    transaction = {"amount": 100, "currency": "RUB"}
    result = convert_to_rub(transaction)
    assert result == 100.0
    assert isinstance(result, float)


def test_float_amount():
    """Проверка дробного amount"""
    transaction = {"amount": 100.55, "currency": "RUB"}
    result = convert_to_rub(transaction)
    assert result == 100.55


def test_currency_case_insensitive():
    """Валюта не чувствительна к регистру"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "rates": {"RUB": 75.00}
    }
    mock_response.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', return_value=mock_response):
        # Проверяем разные регистры
        result_usd = convert_to_rub({"amount": 100, "currency": "usd"})
        result_usd_upper = convert_to_rub({"amount": 100, "currency": "USD"})

        assert result_usd == result_usd_upper == 7500.0


def test_api_called_with_correct_headers():
    """Проверка правильности заголовков запроса"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "rates": {"RUB": 75.00}
    }
    mock_response.raise_for_status = Mock()

    with patch.object(src.external_api.requests, 'get', return_value=mock_response) as mock_get:
        convert_to_rub({"amount": 100, "currency": "USD"})

        # Проверяем заголовки
        call_kwargs = mock_get.call_args[1]
        assert 'headers' in call_kwargs
        assert 'apikey' in call_kwargs['headers']
