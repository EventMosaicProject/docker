import json
import urllib.request
import sys
import os

# Базовый URL для Kafka Connect REST API
KAFKA_CONNECT_URL = "http://localhost:8383"

def register_connector(json_file_path):
    """
    Регистрирует или обновляет коннектор Kafka Connect, используя конфигурацию из JSON-файла.
    """
    if not os.path.exists(json_file_path):
        print(f"Ошибка: Файл конфигурации не найден по пути: {json_file_path}")
        return

    print(f"Обработка файла: {json_file_path}")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Ошибка: Не удалось прочитать JSON из файла {json_file_path}. Детали: {e}")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла {json_file_path}. Детали: {e}")
        return

    connector_name = data.get("name")
    connector_config = data.get("config")

    if not connector_name:
        print(f"Ошибка: Поле 'name' не найдено или пусто в файле {json_file_path}")
        return

    if not connector_config:
        print(f"Ошибка: Поле 'config' не найдено или пусто для коннектора '{connector_name}' в файле {json_file_path}")
        return

    target_url = f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config"
    print(f"Отправка конфигурации для коннектора '{connector_name}' на URL: {target_url}")

    # Подготовка данных и запроса
    # json.dumps сериализует объект Python (dict) обратно в JSON-строку
    # .encode('utf-8') кодирует эту строку в байты для отправки
    req_data = json.dumps(connector_config).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    req = urllib.request.Request(target_url, data=req_data, headers=headers, method='PUT')

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            print(f"Успех! Статус: {response.status}, Ответ от сервера для '{connector_name}':")
            # Пробуем красиво напечатать JSON, если это JSON
            try:
                print(json.dumps(json.loads(response_body), indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(response_body) # Если ответ не JSON, печатаем как есть

    except urllib.error.HTTPError as e:
        print(f"Ошибка HTTP при обращении к Kafka Connect для '{connector_name}': {e.code} {e.reason}")
        try:
            error_response_body = e.read().decode('utf-8')
            print("Тело ответа с ошибкой:")
            print(json.dumps(json.loads(error_response_body), indent=2, ensure_ascii=False))
        except Exception:
            print("(Не удалось прочитать тело ответа с ошибкой или оно не в формате JSON)")
    except urllib.error.URLError as e:
        print(f"Ошибка URL (вероятно, Kafka Connect недоступен) для '{connector_name}': {e.reason}")
    except Exception as e:
        print(f"Непредвиденная ошибка при регистрации коннектора '{connector_name}': {e}")
    print("-" * 40)


if __name__ == "__main__":
    # Проверяем, переданы ли пути к файлам как аргументы командной строки
    if len(sys.argv) > 1:
        for file_path_arg in sys.argv[1:]:
            # Для Windows, если путь в кавычках, убираем их
            clean_file_path = file_path_arg.strip('"').strip("'")
            register_connector(clean_file_path)
    else:
        # Если аргументы не переданы, можно зарегистрировать известные файлы по умолчанию
        # Указать корректные пути к файлам здесь
        # Например, если скрипт лежит в docker/kafka-connect/
        # А файлы коннекторов в docker/kafka-connect/connectors/
        connectors_dir = os.path.join(os.path.dirname(__file__), "connectors")

        default_files = [
            os.path.join(connectors_dir, "elasticsearch-gdelt-events-sink.json"),
            os.path.join(connectors_dir, "elasticsearch-gdelt-mentions-sink.json")
        ]
        print("Аргументы командной строки не указаны. Используются файлы по умолчанию:")
        for file_path in default_files:
            register_connector(file_path)

    print("Процесс регистрации коннекторов завершен.")
