import csv
import os
from typing import Dict, List

import pandas as pd


def load_transactions_csv(file_path=None) -> List[Dict]:
    """Считывает финансовые операции из CSV файла, выдает список словарей с транзакциями"""
    # Если путь не указан, формируем путь по умолчанию
    if file_path is None:
        # Получаем путь к текущему файлу и поднимаемся в корень проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        file_path = os.path.join(project_root, "data", "transactions.csv")

    # Проверяем существование файла
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # Читаем CSV файл
    transactions = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Очищаем значения от пробелов
            clean_row = {}
            for key, value in row.items():
                clean_key = key.strip()
                clean_value = value.strip() if value else value

                # Пробуем преобразовать amount в число
                if clean_key == "amount" and clean_value:
                    try:
                        clean_value = float(clean_value)
                    except ValueError:
                        pass

                clean_row[clean_key] = clean_value
            transactions.append(clean_row)

    return transactions


def load_transactions_excel(file_path=None) -> List[Dict]:
    """Считывает финансовые операции из Excel файла, выдает список словарей с транзакциями"""
    # Если путь не указан, формируем путь по умолчанию
    if file_path is None:
        # Получаем путь к текущему файлу и поднимаемся в корень проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        file_path = os.path.join(project_root, "data", "transactions_excel")

    # Проверяем существование файла (проверяем оба возможных расширения)
    excel_extensions = [".xlsx", ".xls", ".xlsm"]
    actual_file_path = None

    for ext in excel_extensions:
        test_path = file_path + ext if not file_path.endswith(ext) else file_path
        if os.path.exists(test_path):
            actual_file_path = test_path
            break

    # Если файл не найден с расширениями, проверяем как есть
    if actual_file_path is None:
        if os.path.exists(file_path):
            actual_file_path = file_path
        else:
            raise FileNotFoundError(f"Файл не найден: {file_path} (проверены расширения {excel_extensions})")

    # Читаем Excel файл
    try:
        df = pd.read_excel(actual_file_path)

        # Преобразуем DataFrame в список словарей
        transactions = []
        for _, row in df.iterrows():
            transaction = {}
            for col in df.columns:
                value = row[col]

                # Обработка NaN значений
                if pd.isna(value):
                    value = None
                elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
                    value = str(value.date())  # Преобразуем дату в строку
                elif isinstance(value, (int, float)):
                    # Оставляем числа как есть
                    pass
                else:
                    value = str(value).strip() if value else value

                transaction[col] = value
            transactions.append(transaction)

        return transactions

    except Exception as e:
        raise Exception(f"Ошибка при чтении Excel файла {actual_file_path}: {e}")
