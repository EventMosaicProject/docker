# Docker конфигурация

## Обзор
Этот каталог содержит Docker конфигурации для развертывания микросервисной архитектуры `Event Mosaic`.  
Система состоит из нескольких сервисов, работающих совместно через `Service Discovery (Eureka)`.

## Структура каталога

```
docker/  
├── elasticsearch/               # Конфигурации Elasticsearch  
├── redis/                       # Конфигурации Redis  
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

