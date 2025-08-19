# test_env.py
import os

print('KAFKA_TOPIC:', os.getenv('KAFKA_TOPIC'))
print('PRODUCT_IDS:', os.getenv('PRODUCT_IDS'))
print('LIVE_OR_HISTORICAL:', os.getenv('LIVE_OR_HISTORICAL'))
