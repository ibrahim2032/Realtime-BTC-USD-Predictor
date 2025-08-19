# test_env.py
import os

print("KAFKA_TOPIC:", os.getenv("KAFKA_TOPIC"))
print("KAFKA_CONSUMER_GROUP:", os.getenv("KAFKA_CONSUMER_GROUP"))
print("FEATURE_GROUP_NAME:", os.getenv("FEATURE_GROUP_NAME"))
print("LIVE_OR_HISTORICAL:", os.getenv("LIVE_OR_HISTORICAL"))
print("HOPSWORKS_API_KEY:", os.getenv("HOPSWORKS_API_KEY"))
print("HOPSWORKS_PROJECT_NAME:", os.getenv("HOPSWORKS_PROJECT_NAME"))
