# Standard Library Packages
from datetime import timedelta
from typing import Any, List, Optional, Tuple

# Third Party Packages
from loguru import logger
from quixstreams import Application

# Application Local Packages
from src.config import config

    
def init_ohlc_candle(value: dict) -> dict:
    """
    Initialize the OHLC candle with the first trade data.
    Args:
        value (dict): _description_

    Returns:
        dict: _description_
    """
    return {
        "open":  value["price"],
        "high":  value["price"],
        "low":   value["price"],
        "close": value["price"],
        "product_id": value["product_id"],
    }
    
def update_ohlc_candle(ohlc_candle: dict, trade: dict) -> dict:
    """
    Update the OHLC candle with the new trade data and return the updated candle.
    Args:
        ohlc_candle (dict): The current OHLC candle.
        trade (dict): The incoming trade data.
        
    Returns:
        dict: The updated OHLC candle.
    """
    return {
        "open":  ohlc_candle["open"],
        "high":  max(ohlc_candle["high"], trade["price"]),
        "low":   min(ohlc_candle["low"], trade["price"]),
        "close": trade["price"],
        "product_id": trade["product_id"],
    }

def custom_ts_extractor(
    value: Any,
    headers: Optional[List[Tuple[str, bytes]]],
    timestamp: float,
    timestamp_type #: TimestampType,
) -> int:
    """
    Specifying a custom timestamp extractor to use the timestamp from the message payload 
    instead of Kafka timestamp.
    
    Timestamp from trade data is in milliseconds.
    Args:
        value (Any): The message payload.
        headers (Optional[List[Tuple[str, bytes]]]): The message headers.
        timestamp (float): The timestamp from Kafka.
        timestamp_type (TimestampType): The type of the timestamp.
    """
    return value["timestamp_ms"]


def trade_to_ohlc(
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_broker_address: str,
    kafka_consumer_group: str,
    ohlc_window_seconds: int,    
) -> None:
    
    """
    Reads trades from the Kafka topic
    Aggregates them into OHLC candles using the given window size in 'ohlc_window_seconds'
    Saves the OHLC data into another Kafka topic.

    Args:
        kafka_input_topic (str): Kafka topic to read trades data from.
        kafka_output_topic (str): Kafka topic to write OHLC data to.
        kafka_broker_address (str): Kafka broker address.
        kafka_consumer_group (str): Kafka consumer group.
        ohlc_window_seconds (int): The window size in seconds for which OHLC data is calculated.

    Returns:
        None
    """
      
    app = Application(
        broker_address=kafka_broker_address, 
        consumer_group=kafka_consumer_group, 
        auto_offset_reset='latest'
        )


    # Topic to read trades
    input_topic = app.topic(
        name=kafka_input_topic, 
        value_deserializer='json', 
        timestamp_extractor=custom_ts_extractor,
        )

    # Topic to save OHLC data
    output_topic = app.topic(name=kafka_output_topic, value_serializer='json')

    # Creating a streaming dataframe
    # to apply transformations on the incoming  data
    sdf = app.dataframe(topic=input_topic)
    
    # apply transformations on the incoming data -start
    # Here we need to define how we transform the incoming trades data to OHLC candles
    sdf = sdf.tumbling_window(duration_ms=timedelta(seconds=ohlc_window_seconds))
    sdf = sdf.reduce(reducer=update_ohlc_candle, initializer=init_ohlc_candle).final()
    
    # Extract the open, high, low, close prices from the OHLC candle (value) and add them as separate columns
    # The current output has the formart: {'start': 1740968790000, 'end': 1740968820000, 'value': {'open': 2433.47, 'high': 2433.47, 'low': 2430.48, 'close': 2430.48, 'product_id': 'BTC-USD'}}
    # The desired output formart will be: {'timestamp': 1740968820000 # end of the window 'open': 2433.47, 'high': 2433.47, 'low': 2430.48, 'close': 2430.48, 'product_id': 'BTC-USD'}
    
    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['product_id'] = sdf['value']['product_id']
    sdf['timestamp'] = sdf['end']
    
    # Keep only the desired columns
    sdf = sdf[['timestamp', 'open', 'high', 'low', 'close', 'product_id']]
    
    # apply transformations on the incoming data -end
    
    sdf = sdf.update(logger.info)
    
    # Write the transformed data to the output topic
    sdf = sdf.to_topic(output_topic)
    
    # Clear the invalid state store
    # app.clear_state()  
    
    # Run the streaming application
    app.run(sdf)
    
    
 

if __name__ == '__main__':
    trade_to_ohlc(
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_broker_address=config.kafka_broker_address,
        ohlc_window_seconds=config.ohlc_window_seconds,
        kafka_consumer_group=config.kafka_consumer_group,
    )