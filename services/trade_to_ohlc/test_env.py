# test_env.py
import os

print('KAFKA_INPUT_TOPIC:', os.getenv('KAFKA_INPUT_TOPIC'))
print('KAFKA_OUTPUT_TOPIC:', os.getenv('KAFKA_OUTPUT_TOPIC'))
print('KAFKA_CONSUMER_GROUP:', os.getenv('KAFKA_CONSUMER_GROUP'))
print('KAFKA_BROKER_ADDRESS:', os.getenv('KAFKA_BROKER_ADDRESS'))
print('OHLC_WINDOW_SECONDS:', os.getenv('OHLC_WINDOW_SECONDS'))