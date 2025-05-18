#!/bin/sh
set -e # Выход при ошибке

# Переменные (вынести в env)
ELASTICSEARCH_HOST="elasticsearch"
ELASTICSEARCH_PORT="9200"
ELASTIC_USER="elastic"
ELASTIC_PASSWORD="elastic"

# Путь к файлам конфигурации внутри контейнера
# Очередность создания файлов:
# 1. ILM policy
# 2. Events template
# 3. Mentions template
CONFIG_PATH="/etc/elasticsearch-init"
ILM_POLICY_FILE="${CONFIG_PATH}/ilm_policy.json"
EVENTS_TEMPLATE_FILE="${CONFIG_PATH}/events_template.json"
MENTIONS_TEMPLATE_FILE="${CONFIG_PATH}/mentions_template.json"

# Ожидание доступности Elasticsearch
echo "Waiting for Elasticsearch to be available at ${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}..."
until curl -s -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" "http://${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}/_cluster/health?wait_for_status=yellow&timeout=5s"; do
  echo "Elasticsearch is unavailable - sleeping"
  sleep 5
done
echo "Elasticsearch is up and running!"

# 1. Применение ILM политики
echo "Applying ILM policy 'gdelt_30_day_retention_policy'..."
curl -s -X PUT -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" "http://${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}/_ilm/policy/gdelt_30_day_retention_policy" \
  -H 'Content-Type: application/json' \
  -d "@${ILM_POLICY_FILE}"
echo "\nILM policy applied."

# 2. Применение шаблона для событий
echo "Applying index template 'gdelt_events_template'..."
curl -s -X PUT -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" "http://${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}/_index_template/gdelt_events_template" \
  -H 'Content-Type: application/json' \
  -d "@${EVENTS_TEMPLATE_FILE}"
echo "\nEvents template applied."

# 3. Применение шаблона для упоминаний
echo "Applying index template 'gdelt_mentions_template'..."
curl -s -X PUT -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" "http://${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}/_index_template/gdelt_mentions_template" \
  -H 'Content-Type: application/json' \
  -d "@${MENTIONS_TEMPLATE_FILE}"
echo "\nMentions template applied."

echo "Elasticsearch initialization complete."