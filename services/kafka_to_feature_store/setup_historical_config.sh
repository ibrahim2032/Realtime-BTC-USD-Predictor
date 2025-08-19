export KAFKA_TOPIC=ohlc_historical
export KAFKA_CONSUMER_GROUP=ohlc_historical_consumer_group_121

export FEATURE_GROUP_NAME=ohlc_feature_group
export FEATURE_GROUP_VERSION=1

# 43,200 is 60 minutes * 24 hours * 30 days worth of data for one product_id * 1 product.
export  BUFFER_SIZE=43200

export LIVE_OR_HISTORICAL=historical

export SAVE_EVERY_N_SECONDS=30

export FLUSH_INTERVAL_SEC=30
export CREATE_NEW_CONSUMER_GROUP=true