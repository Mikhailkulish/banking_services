import json
import logging
import os
from typing import Any, Dict, List

# Указываем путь к существующей папке с логами
log_dir = "logs"
log_file = os.path.join(log_dir, "utils.log")

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


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Загружает финансовые транзакции из JSON-файла"""
    logger.info(f"Вызов функции load_transactions с аргументом: {file_path}")

    try:
        # Проверяем размер файла
        file_size = os.path.getsize(file_path)
        logger.info(f"Размер файла {file_path}: {file_size} байт")

        if file_size == 0:
            logger.warning(f"Файл {file_path} пустой. Возвращаем пустой список")
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            logger.info(f"Открыт файл {file_path} для чтения")
            data = json.load(file)
            logger.info(f"Данные из файла {file_path} успешно загружены")

        # Проверяем, что данные являются списком
        if isinstance(data, list):
            logger.info(f"Данные являются списком. Количество транзакций: {len(data)}")
            logger.info(f"load_transactions успешно завершена. Возвращаем список из {len(data)} транзакций")
            return data
        else:
            logger.warning(
                f"Данные в файле {file_path} не являются списком (тип: {type(data).__name__}). Возвращаем пустой список"
            )
            return []

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON в файле {file_path}: {e}")
        return []
    except IOError as e:
        logger.error(f"Ошибка ввода/вывода при чтении файла {file_path}: {e}")
        return []
    except OSError as e:
        logger.error(f"Ошибка операционной системы при доступе к файлу {file_path}: {e}")
        return []
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка в load_transactions: {e}")
        return []
