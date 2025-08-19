import sys
import time
import json
from typing import Optional
from datetime import datetime, timezone

from loguru import logger
from quixstreams import Application

from src.config import config
from src.hopsworks_api import push_data_to_feature_store, initialize_hopsworks

def get_current_utc_sec() -> int:
    return int(datetime.now(timezone.utc).timestamp())

def kafka_to_feature_store(
    kafka_topic: str,
    kafka_broker_address: str,
    kafka_consumer_group: str,
    feature_group_name: str,
    feature_group_version: int,
    buffer_size: Optional[int] = 1,
    flush_interval_sec: Optional[int] = 600,
    live_or_historical: Optional[str] = 'live',
) -> None:
    """
    Reads messages from a Kafka topic and writes them to a feature group in the Hopsworks feature store specified by the feature group name and version.
    This function uses the Quix Streams library to consume messages from Kafka and the Hopsworks API to write data to the feature store.
    The function handles errors and retries, and it flushes the buffer to the feature store at regular intervals.
    The function also handles the case where the Kafka topic is empty or the consumer group is not found.
    
   Args:
        kafka_topic (str): The name of the Kafka topic.
        kafka_broker_address (str): The address of the Kafka broker.
        kafka_consumer_group (str): The name of the Kafka consumer group.
        feature_group_name (str): The name of the feature group to write.
        feature_group_version (int): The version of the feature group to write.
        buffer_size (int): The number of messages to buffer before writing to the feature store.
        flush_interval_sec (int): The interval in seconds to flush the buffer to the feature store.
        live_or_historical (str): Whether the data is live or historical.
                If live, the data is written to the online feature store.
                If historical, the data is written to the offline feature store.
                
    Returns:
        None
    """
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset="earliest" if live_or_historical == "historical" else "latest",
    )
    
    online_or_offline="online" if live_or_historical == "live" else "offline"

    # Initialize Hopsworks once
    feature_group = initialize_hopsworks(
        feature_group_name=feature_group_name,
        feature_group_version=feature_group_version,
        online_or_offline=online_or_offline,
    )

    last_saved_to_feature_store_ts = get_current_utc_sec()
    buffer = []
    max_errors = 5
    error_count = 0

    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[kafka_topic])
        logger.info(f"Subscribed to {kafka_topic} Kafka topic. Start saving to {online_or_offline} feature store.")

        while True:
            try:
                message = consumer.poll(1)

                if message is None:
                    if get_current_utc_sec() - last_saved_to_feature_store_ts > flush_interval_sec and buffer:
                        logger.info(f"Flush interval reached. Writing {len(buffer)} messages to feature store.")
                        push_data_to_feature_store(feature_group, buffer, online_or_offline)
                        buffer.clear()
                        last_saved_to_feature_store_ts = get_current_utc_sec()
                    else:
                        time.sleep(0.5)  # Avoid high CPU usage
                    continue

                if message.error():
                    logger.error(f"Kafka error: {message.error()}")
                    error_count += 1
                    if error_count >= max_errors:
                        logger.critical("Too many consecutive Kafka errors. Exiting consumer.")
                        break
                    continue

                try:
                    ohlc = json.loads(message.value().decode("utf-8"))
                    buffer.append(ohlc)
                except Exception as e:
                    logger.error(f"Failed to decode message: {e}")
                    continue

                if len(buffer) >= buffer_size:
                    logger.info(f"Buffer full. Writing {len(buffer)} messages to feature store.")
                    push_data_to_feature_store(feature_group, buffer, online_or_offline)
                    buffer.clear()
                    last_saved_to_feature_store_ts = get_current_utc_sec()

                consumer.store_offsets(message=message)
                error_count = 0  # Reset error count on success

            except Exception as e:
                logger.critical(f"Unexpected error: {e}")
                sys.exit(1)

if __name__ == "__main__":
    try:
        kafka_to_feature_store(
            kafka_topic=config.kafka_topic,
            kafka_broker_address=config.kafka_broker_address,
            kafka_consumer_group=config.kafka_consumer_group,
            feature_group_name=config.feature_group_name,
            feature_group_version=config.feature_group_version,
            buffer_size=config.buffer_size,
            flush_interval_sec=config.flush_interval_sec,
            live_or_historical=config.live_or_historical,
        )
    except Exception as e:
        logger.critical(f"Application terminated unexpectedly: {e}")
        sys.exit(1)
