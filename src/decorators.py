import functools
import time
from typing import Any, Callable, Optional, TypeVar, cast

# Объявляем тип для оборачиваемой функции
F = TypeVar("F", bound=Callable[..., Any])


def log(filename: Optional[str] = None) -> Callable[[F], F]:
    """Декоратор для логирования вызовов функций"""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Открываем файл, если указано имя
            out = open(filename, "a") if filename else None

            try:
                # Логируем начало выполнения
                msg: str = f"{time.ctime()} Начало {func.__name__}"
                if out is None:
                    print(msg)
                else:
                    print(msg, file=out)

                # Вызываем оригинальную функцию
                res: Any = func(*args, **kwargs)

                # Логируем успешное завершение
                msg = f"{time.ctime()} Конец {func.__name__} -> {res}"
                if out is None:
                    print(msg)
                else:
                    print(msg, file=out)

                # Закрываем файл, если он был открыт
                if out:
                    out.close()

                return res

            except Exception as e:
                # Логируем ошибку
                msg = f"{time.ctime()} Ошибка {func.__name__}: {type(e).__name__} {args} {kwargs}"
                if out is None:
                    print(msg)
                else:
                    print(msg, file=out)

                # Закрываем файл, если он был открыт
                if out:
                    out.close()

                # Пробрасываем исключение дальше
                raise

        # Возвращаем обернутую функцию с сохранением сигнатуры
        return cast(F, wrapper)

    return decorator
