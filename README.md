# Docker конфигурация

## Обзор
Этот каталог содержит Docker конфигурации для развертывания микросервисной архитектуры `Event Mosaic`.  
Система состоит из нескольких сервисов, работающих совместно через `Service Discovery (Eureka)`.

## Структура каталога

```
docker/  
├── elasticsearch/               # Конфигурации Elasticsearch  
├── redis/                       # Конфигурации Redis  
├── prometheus/                  # Конфигурации Prometheus  
├── env/                         # Файлы переменных окружения  
├── compose.dev.yml              # Docker Compose для разработки  
├── compose.prod.yml             # Docker Compose для продакшена  
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
- `redis` - Хранение флага о готовности данных к обработке (порт 6379)
- `prometheus` - Система мониторинга и сбора метрик (порт 9090)
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

