FROM confluentinc/cp-kafka-connect:7.9.0

# Устанавливаем Elasticsearch Sink Connector и Transformations
# confluent-hub install <имя_компонента>:<версия> --no-prompt
RUN confluent-hub install confluentinc/kafka-connect-elasticsearch:15.0.0 --no-prompt && \
    confluent-hub install confluentinc/connect-transforms:1.6.2 --no-prompt