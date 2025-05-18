# Docker конфигурация

## Обзор
Этот каталог содержит Docker конфигурации для развертывания микросервисной архитектуры `Event Mosaic`.  
Система состоит из нескольких сервисов, работающих совместно через `Service Discovery (Eureka)`.

## Структура каталога

```
docker/  
├── elasticsearch/                # Конфигурации Elasticsearch
│   ├── init/                     # Скрипты и конфигурации для инициализации ES (ILM, шаблоны)
│   ├── certs/                    # SSL сертификаты для Elasticsearch (для prod)
│   ├── elasticsearch.dev.yml     # Конфигурация ES для dev-среды
│   ├── elasticsearch.prod.yml    # Конфигурация ES для prod-среды
│   └── security.yml              # Конфигурация безопасности ES (для prod)
├── kafka-connect/                # Конфигурации Kafka Connect
│   ├── connectors/               # JSON конфигурации для коннекторов (Elasticsearch sink)
│   ├── Dockerfile                # Dockerfile для сборки образа Kafka Connect с плагинами
│   └── register-connectors.py    # Python скрипт для регистрации/обновления коннекторов
├── redis/                        # Конфигурации Redis  
├── prometheus/                   # Конфигурации Prometheus  
├── grafana/                      # Конфигурации Grafana  
├── loki/                         # Конфигурации Loki
├── promtail/                     # Конфигурации Promtail
├── env/                          # Файлы переменных окружения  
├── compose.dev.yml               # Docker Compose для разработки  
├── compose.prod.yml              # Docker Compose для продакшена  
└── README.md  
```

## Сервисы

### Основные компоненты
- `em-discovery` (Eureka Server) - Сервис обнаружения (порт 8761)
- `em-gateway` (API Gateway) - API шлюз (порт 8080)
- `em-api` - API сервис (порт 8081)
- `em-adapter` - Адаптер сервис (порт 8082)
- `em-collector` - Сервис сбора данных (порт 8083)
- `em-processor` - Сервис обработки данных (порт 8084)

### Инфраструктурные сервисы
- `elasticsearch` - Хранение и поиск данных (порты 9200, 9300)
- `elasticsearch-init` - Контейнер для инициализации Elasticsearch (применение ILM, шаблонов индексов) в dev-окружении.
- `redis` - Хранение флага о готовности данных к обработке (порт 6379)
- `kafka` - Брокер сообщений для асинхронного взаимодействия (порт 9092)
- `kafka-connect` - Сервис для потоковой передачи данных между Kafka и Elasticsearch (порт 8383)
- `zookeeper` - Координационный сервис для Kafka (порт 2181)
- `prometheus` - Система мониторинга и сбора метрик (порт 9090)
- `grafana` - Платформа для визуализации метрик (порт 3000)
- `loki` - Система агрегации и хранения логов (порт 3100)
- `promtail` - Агент для сбора логов и отправки их в Loki
- `minio` - S3-совместимое объектное хранилище (API: 9000, Console: 9001)

---

## Конфигурация Elasticsearch

### Сертификаты SSL/TLS

1. Скопировать `.env.certs.example` в `.env.certs`
2. Задать надежные пароли в `.env.certs`
3. Создать директорию `certs` в `elasticsearch` если ее нет
4. Запустить генерацию сертификатов:
   `source .env.certs && ./generate-certs.sh` или  
   выполнить через `export CA_PASSWORD=ca_password` и т.д.  и запустить `./generate-certs.sh`
5. Запустить `docker-compose`

### Важно
- Файлы сертификатов и `.env.certs` не должны попадать в git
- Пароли должны быть в безопасном месте
- Сертификаты нужно обновлять по истечении срока действия

### Конфигурация
- `elasticsearch.prod.yml` - конфиги для prod
- `elasticsearch.dev.yml` - конфиги для dev
- `security.yml` - конфиги безопасности

### Инициализация Elasticsearch (ILM и Шаблоны Индексов) в dev-окружении

Для автоматической настройки Elasticsearch при первом запуске в dev-окружении (через `compose.dev.yml`) используется сервис `elasticsearch-init`.  
Этот сервис выполняет следующие задачи:
- Ожидает полной загрузки и доступности Elasticsearch.
- Применяет Политику Управления Жизненным Циклом Индексов (ILM Policy).
- Создает Шаблоны Индексов (Index Templates) для событий (`gdelt-events-*`) и упоминаний (`gdelt-mentions-*`).

Эта автоматизация реализована с помощью скрипта `elasticsearch/init/init-es.sh`, который использует конфигурационные JSON файлы:
- `elasticsearch/init/ilm_policy.json`: Определяет политику `gdelt_30_day_retention_policy`, которая удаляет индексы старше 30 дней.
- `elasticsearch/init/events_template.json`: Задает шаблон для индексов событий, включая маппинги полей и привязку к ILM-политике.
- `elasticsearch/init/mentions_template.json`: Задает шаблон для индексов упоминаний, включая маппинги полей и привязку к ILM-политике.

Это гарантирует, что данные будут сохраняться с корректной схемой и автоматически управляться согласно заданной политике хранения.  
В prod среде (`compose.prod.yml`) подобную инициализацию планируется выполнять отдельными скриптами или через CI/CD.

---

## Конфигурация Kafka

### Обзор
Kafka используется как брокер сообщений для асинхронного взаимодействия между микросервисами:
- `em-collector` → `gdelt-raw-data-topic` → `em-adapter`
- `em-adapter` → `gdelt-parsed-data-topic` → `em-processor`
- `em-processor` → `gdelt-processed-data-topic` → (`Kafka Connect` → `Elasticsearch`)

### Компоненты
- `zookeeper` - координационный сервис для Kafka (dev и prod)
- `kafka` - брокер сообщений Kafka
- `kafka-ui` - веб-интерфейс для управления Kafka (только в dev-окружении)

### Конфигурация

#### Общая конфигурация
- Порт брокера: `9092` (для внешнего доступа)
- Внутренний порт: `29092` (для контейнеров)
- Автоматическое создание топиков: включено
- Базовая надежность: фактор репликации 1 (для одиночного брокера)
- Идемпотентные продюсеры для предотвращения дублирования сообщений

#### Для разработки (dev)
- Упрощенная конфигурация с одним брокером
- Включен веб-интерфейс Kafka UI (порт 8090)
- Хранение данных во временных томах

#### Для продакшена (prod)
- Расширенная конфигурация брокера с улучшенными параметрами надежности
- Увеличенный период хранения сообщений (72 часа)
- Настроены healthcheck-проверки
- Постоянное хранение данных в именованных томах

### Доступ
- Брокер Kafka: `localhost:9092`
- Kafka UI (только в dev): `http://localhost:8090`

---

## Конфигурация Kafka Connect

### Обзор
Kafka Connect используется для надежной и масштабируемой потоковой передачи данных между Apache Kafka и другими системами.  
В данном проекте он настроен для отправки обработанных событий (events) и упоминаний (mentions) из соответствующих топиков Kafka в Elasticsearch.

### Компоненты и конфигурация
- **Dockerfile**: `kafka-connect/Dockerfile` используется для сборки кастомного образа Kafka Connect, который включает необходимые плагины:
    - `confluentinc/kafka-connect-elasticsearch`: для интеграции с Elasticsearch.
    - `confluentinc/connect-transforms`: для преобразований сообщений "на лету".
- **Сервис в Docker Compose**: Определен в `compose.dev.yml` и `compose.prod.yml`.
  - Зависит от `kafka` и `elasticsearch`.
  - REST API доступен на порту `8383` хоста для управления коннекторами.
- **Конфигурации коннекторов**: JSON файлы, определяющие поведение sink-коннекторов, расположены в `kafka-connect/connectors/`:
  - `elasticsearch-gdelt-events-sink.json`: для отправки данных из топика `gdelt-processor-event-topic` в индексы Elasticsearch с паттерном `gdelt-events-yyyy-MM-dd`.
  - `elasticsearch-gdelt-mentions-sink.json`: для отправки данных из топика `gdelt-processor-mention-topic` в индексы Elasticsearch с паттерном `gdelt-mentions-yyyy-MM-dd`.
  - **Ключевые настройки коннекторов**:
    - Использование `TimestampRouter` SMT (Single Message Transform) для динамического формирования имени индекса на основе поля `elasticIndexDate` (формат `yyyy-MM-dd`) из сообщения.
    - `key.ignore=false`: ключ сообщения Kafka используется как `_id` документа в Elasticsearch.
    - Настроена обработка ошибок с использованием DLQ (Dead Letter Queue): сообщения, которые не удалось записать в Elasticsearch, отправляются в топики `dlq-gdelt-event-topic` и `dlq-gdelt-mention-topic` соответственно.
    - Поле `elasticIndexDate` удаляется из сообщения перед записью в Elasticsearch с помощью SMT `ReplaceField$Value`.
- **Регистрация коннекторов**:
  - Для автоматизации регистрации или обновления конфигураций коннекторов предоставлен Python-скрипт `kafka-connect/register-connectors.py`.
  - Этот скрипт можно запустить после старта сервиса `kafka-connect`. Он подключается к REST API Kafka Connect и применяет конфигурации из JSON-файлов.
  - В `compose.dev.yml` присутствует монтирование скрипта `register-connectors.sh` в контейнер `kafka-connect`. Если этот скрипт является оберткой для `register-connectors.py` или выполняет аналогичную функцию, он может использоваться для автоматической регистрации коннекторов при старте контейнера (потребуется соответствующая настройка `command` или `entrypoint` в сервисе `kafka-connect`).

### Доступ
- Kafka Connect REST API: `http://localhost:8383`

---

## Конфигурация Prometheus

### Обзор
Prometheus используется для сбора метрик со всех микросервисов через Spring Boot Actuator.

### Настройка
1. Все микросервисы имеют зависимость `micrometer-registry-prometheus` для экспорта метрик
2. Actuator в каждом сервисе настроен на порт 8081 и экспортирует эндпоинт `/actuator/prometheus`
3. Prometheus автоматически обнаруживает сервисы через Eureka

### Конфигурация
- `prometheus.yml` - основной конфигурационный файл Prometheus
- Для Eureka Server используется статическая конфигурация
- Для остальных сервисов используется автоматическое обнаружение через Eureka

### Доступ к метрикам
- Веб-интерфейс Prometheus: `http://localhost:9090`
- Список целей мониторинга: `http://localhost:9090/targets`
- Обнаруженные сервисы: `http://localhost:9090/service-discovery`

---

## Конфигурация Grafana

### Конфигурация
- `grafana.ini` - основной конфигурационный файл Grafana
- `datasources/` - конфигурации источников данных (Prometheus)
- `dashboards/` - предустановленные дашборды

### Доступ к Grafana
- Веб-интерфейс Grafana: `http://localhost:3000`
- Логин по умолчанию: `admin`
- Пароль по умолчанию: `admin` (рекомендуется сменить при первом входе)

---

## Конфигурация Loki

### Обзор
Loki используется для агрегации и хранения логов со всех микросервисов. Интегрирован с Grafana.

### Конфигурация
- `loki.dev.yml` - конфиг для разработки (локальное хранение)
- `loki.prod.yml` - конфиг для прода (хранение в MinIO)
- Основные параметры:
  - Хранение логов в файловой системе (dev) или S3-совместимом хранилище (prod)
  - Порт API: 3100
  - Интеграция с Grafana через datasource

### Доступ
- Веб-интерфейс через Grafana: `http://localhost:3000`

---

## Конфигурация Promtail

### Обзор
Promtail собирает логи с:
- Микросервисов приложения (`/logs/*.log`)
- Системных логов хоста (`/var/log`)
- Docker-контейнеров (`/var/lib/docker/containers`)

### Конфигурация
- `promtail.dev.yml` - конфиг для разработки
- `promtail.prod.yml` - конфиг для прода
- Основные параметры:
  - Отправка логов в Loki
  - Автоматическое добавление меток

---

## Конфигурация MinIO

### Обзор
MinIO используется как S3-совместимое объектное хранилище в окружении для разработки.
Это позволяет эмулировать работу с облачными хранилищами типа AWS S3 локально.

### Доступ
- API MinIO: `http://localhost:9000`
- Веб-консоль MinIO: `http://localhost:9001`
- Учетные данные по умолчанию:
    - Логин: `eventmosaic`
    - Пароль: `eventmosaic`
- Bucket по умолчанию: `event-mosaic`

---

## Запуск и остановка

Из каталога `/docker` выполнить команду:
#### Старт

```bash
docker compose -f compose.dev.yml up -d
```

#### Стоп

```bash
docker compose -f compose.dev.yml down
```
---

