#!/bin/bash

# Проверяем наличие переменных окружения
if [ -z "$CA_PASSWORD" ] || [ -z "$CERT_PASSWORD" ]; then
    echo "Ошибка: Не заданы CA_PASSWORD или CERT_PASSWORD"
    exit 1
fi

# Генерируем сертификаты
docker run --rm \
    -v $(pwd)/certs:/usr/share/elasticsearch/config/certs \
    -e CA_PASSWORD=$CA_PASSWORD \
    -e CERT_PASSWORD=$CERT_PASSWORD \
    docker.elastic.co/elasticsearch/elasticsearch:8.17.1 \
    bash -c '
        bin/elasticsearch-certutil ca --out config/certs/ca.p12 --pass $CA_PASSWORD --silent &&
        bin/elasticsearch-certutil cert --ca config/certs/ca.p12 --ca-pass $CA_PASSWORD --name elastic-node --out config/certs/elastic-certificates.p12 --pass $CERT_PASSWORD --silent
    '

# Устанавливаем правильные права
chmod 440 certs/*.p12