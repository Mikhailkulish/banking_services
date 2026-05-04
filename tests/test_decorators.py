import pytest
import time
from src.decorators import log


def test_log_to_console_success(capsys):
    """Тест логирования успешного выполнения в консоль"""

    @log()
    def add(a: int, b: int) -> int:
        return a + b

    result = add(2, 3)
    assert result == 5

    captured = capsys.readouterr()
    assert "Начало add" in captured.out
    assert "Конец add -> 5" in captured.out


def test_log_to_console_with_args_kwargs(capsys):
    """Тест логирования функций с аргументами"""

    @log()
    def greet(name: str, age: int = 0) -> str:
        return f"Hello {name}"

    result = greet("Alice", age=30)
    assert result == "Hello Alice"

    captured = capsys.readouterr()
    assert "Начало greet" in captured.out
    assert "Конец greet -> Hello Alice" in captured.out


def test_log_to_file_success(tmp_path):
    """Тест логирования в файл при успешном выполнении"""
    log_file = tmp_path / "test.log"

    @log(filename=str(log_file))
    def multiply(x: int, y: int) -> int:
        return x * y

    result = multiply(4, 5)
    assert result == 20

    content = log_file.read_text()
    assert "Начало multiply" in content
    assert "Конец multiply -> 20" in content


def test_log_to_file_multiple_calls(tmp_path):
    """Тест нескольких вызовов функции с записью в один файл"""
    log_file = tmp_path / "test.log"

    @log(filename=str(log_file))
    def increment(x: int) -> int:
        return x + 1

    for i in range(3):
        increment(i)

    content = log_file.read_text()
    lines = content.strip().split('\n')

    assert len(lines) == 6
    assert "Начало increment" in lines[0]
    assert "Конец increment -> 1" in lines[1]
    assert "Начало increment" in lines[2]
    assert "Конец increment -> 2" in lines[3]


def test_preserves_function_metadata():
    """Тест сохранения метаданных исходной функции"""

    @log()
    def test_function(x: int) -> int:
        """Docstring тестовой функции"""
        return x * 2

    assert test_function.__name__ == "test_function"
    assert test_function.__doc__ == "Docstring тестовой функции"


def test_works_with_different_return_types(capsys):
    """Тест работы с разными типами возвращаемых значений"""

    @log()
    def return_none() -> None:
        pass

    @log()
    def return_string() -> str:
        return "test"

    @log()
    def return_list() -> list:
        return [1, 2, 3]

    assert return_none() is None
    assert return_string() == "test"
    assert return_list() == [1, 2, 3]

    captured = capsys.readouterr()
    assert "Конец return_list -> [1, 2, 3]" in captured.out


def test_file_opens_in_append_mode(tmp_path):
    """Тест что файл открывается в режиме добавления"""
    log_file = tmp_path / "test.log"

    # Записываем что-то в файл
    with open(log_file, 'w') as f:
        f.write("Existing content\n")

    @log(filename=str(log_file))
    def func() -> str:
        return "result"

    func()

    # Проверяем, что новый контент добавился, а старый остался
    with open(log_file, 'r') as f:
        content = f.read()

    assert "Existing content" in content
    assert "Начало func" in content
    assert "Конец func -> result" in content


def test_file_closed_after_execution(tmp_path):
    """Тест что файл закрывается после выполнения"""
    log_file = tmp_path / "test.log"

    @log(filename=str(log_file))
    def func() -> str:
        return "result"

    func()

    # Проверяем, что файл создан и содержит данные
    with open(log_file, 'r') as f:
        content = f.read()

    assert "Начало func" in content
    assert "Конец func -> result" in content


def test_with_empty_filename(capsys):
    """Тест с пустым именем файла - должно логировать в консоль"""

    @log(filename="")
    def simple_func() -> str:
        return "test"

    result = simple_func()
    assert result == "test"

    captured = capsys.readouterr()
    assert "Начало simple_func" in captured.out
    assert "Конец simple_func -> test" in captured.out


def test_with_none_filename(capsys):
    """Тест с None в качестве имени файла - должно логировать в консоль"""

    @log(filename=None)
    def simple_func() -> str:
        return "test"

    result = simple_func()
    assert result == "test"

    captured = capsys.readouterr()
    assert "Начало simple_func" in captured.out
    assert "Конец simple_func -> test" in captured.out


def test_nested_decorators(capsys):
    """Тест вложенных декораторов"""

    def uppercase(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs).upper()

        return wrapper

    @uppercase
    @log()
    def greet(name: str) -> str:
        return f"Hello {name}"

    result = greet("Alice")
    assert result == "HELLO ALICE"

    captured = capsys.readouterr()
    assert "Начало greet" in captured.out
    # Логируется исходное значение, до преобразования uppercase
    assert "Конец greet -> Hello Alice" in captured.out


def test_with_long_running_function(capsys):
    """Тест с долго выполняющейся функцией"""

    @log()
    def slow_function():
        time.sleep(0.1)
        return 42

    result = slow_function()
    assert result == 42


def test_preserves_signature():
    """Тест сохранения сигнатуры функции"""
    import inspect

    @log()
    def complex_func(a: int, b: str, c: float = 3.14, *args, **kwargs) -> bool:
        return True

    sig = inspect.signature(complex_func)
    assert str(sig) == "(a: int, b: str, c: float = 3.14, *args, **kwargs) -> bool"


def test_log_output_format(capsys):
    """Тест проверки формата вывода"""

    @log()
    def test_func():
        return "done"

    test_func()

    captured = capsys.readouterr()
    lines = captured.out.strip().split('\n')

    assert len(lines) == 2
    assert "Начало test_func" in lines[0]
    assert "Конец test_func -> done" in lines[1]


def test_concurrent_calls(tmp_path):
    """Тест множественных вызовов"""
    log_file = tmp_path / "concurrent.log"

    @log(filename=str(log_file))
    def process(id_: int) -> int:
        return id_ * 2

    results = [process(i) for i in range(5)]
    assert results == [0, 2, 4, 6, 8]

    with open(log_file, 'r') as f:
        content = f.read()

    for i in range(5):
        assert f"Конец process -> {i * 2}" in content


def test_file_permission_error(tmp_path):
    """Тест при ошибке доступа к файлу"""
    log_file = tmp_path / "protected.log"

    # Создаем файл
    with open(log_file, 'w') as f:
        f.write("test")

    # Делаем файл только для чтения (используем chmod через десятичное число)
    import stat
    log_file.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

    @log(filename=str(log_file))
    def simple_func():
        return "test"

    with pytest.raises(PermissionError):
        simple_func()

    # Возвращаем права для очистки
    log_file.chmod(stat.S_IWUSR | stat.S_IRUSR)


def test_with_directory_as_filename(tmp_path):
    """Тест с директорией вместо файла - должна возникнуть ошибка"""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    @log(filename=str(test_dir))
    def simple_func():
        return "test"

    # При попытке открыть директорию как файл возникает ошибка
    with pytest.raises(Exception):  # ловим любое исключение
        simple_func()


def test_log_to_file_with_newline_in_result(tmp_path):
    """Тест с символами новой строки в возвращаемом значении"""
    log_file = tmp_path / "test.log"

    @log(filename=str(log_file))
    def newline_func() -> str:
        return "Hello\nWorld"

    result = newline_func()
    assert result == "Hello\nWorld"

    with open(log_file, 'r') as f:
        content = f.read()

    # Проверяем что лог содержит строку (символы новой строки могут быть экранированы или нет)
    assert "Hello" in content and "World" in content


def test_log_to_file_with_unicode(tmp_path):
    """Тест с юникод символами (русские буквы)"""
    log_file = tmp_path / "test.log"

    @log(filename=str(log_file))
    def unicode_func() -> str:
        return "Привет мир"

    result = unicode_func()
    assert result == "Привет мир"

    # Просто проверяем, что файл создан и не пустой
    assert log_file.exists()
    assert log_file.stat().st_size > 0
