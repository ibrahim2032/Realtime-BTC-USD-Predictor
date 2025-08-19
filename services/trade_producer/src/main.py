from typing import List

from loguru import logger
from quixstreams import Application

from src.config import config
from src.kraken_api.rest import KrakenRestAPIMultipleProducts
from src.kraken_api.trade import Trade
from src.kraken_api.websocket import KrakenWebsocketTradeAPI


def produce_trades(
    kafka_broker_address: str,
    kafka_topic: str,
    product_ids: List[str],
    live_or_historical: str,
    last_n_days: int,
    cache_dir: str,
) -> None:
    """
    Reads trades from the Kraken websocket API, and saves into Kafka topic.

    Args:
        Kafka_broker_address (str): The address of the Kafka broker.
        Kafka_topic (str): The name of the Kafka topic.
        product_ids (List[str]): List of product ids.
        live_or_historical (str): 'live' or 'historical'..
        last_n_days (int): Number of days to fetch historical data.

    Returns:
        None.
    """

    # Create an Application instance
    app = Application(broker_address=kafka_broker_address)

    # Topic to save trades
    topic = app.topic(name=kafka_topic, value_serializer='json')

    logger.info(
        f'Creating Kraken API instance to fetch trades data for {product_ids}..'
    )

    if live_or_historical == 'live':
        # Create instance of Kraken API to fetch live trades
        kraken_api = KrakenWebsocketTradeAPI(product_ids=product_ids)
    else:
        # Create instance of Kraken API to fetch historical trades
        kraken_api = KrakenRestAPIMultipleProducts(
            product_ids=product_ids, last_n_days=last_n_days, cache_dir=cache_dir
        )
   

    logger.info('Creating producer..')

    # Create a Producer instance
    with app.get_producer() as producer:
        while True:
            # Check is rest api is done fetching historical data
            if kraken_api.is_done():
                logger.info('Historical data fetching done!')
                break

            # Get the trades from Kraken API
            trades: List[Trade] = kraken_api.get_trades()
            # breakpoint()
            for trade in trades:
                # Serialize an event using the defined Topic
                message = topic.serialize(
                    key=trade.product_id,
                    value=trade.model_dump(),
                    # timestamp_ms=int(trade['timestamp']) * 1000
                )

                # Produce a message into the Kafka topic
                producer.produce(
                    topic=topic.name,
                    value=message.value,
                    key=message.key,
                )
                
                logger.info(f'{trade.model_dump()}')
                # logger.info('Message Sent!')
                # 



if __name__ == '__main__':

    logger.debug('Configuration:')
    logger.debug(config.model_dump())
    try:
        logger.info('Starting Trade Producer...')
        #  Log all config values
        # logger.info(f'{config.model_dump()}')
        produce_trades(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic=config.kafka_topic,
            product_ids=config.product_ids,
            live_or_historical=config.live_or_historical,
            last_n_days=config.last_n_days,
            cache_dir=config.cache_dir_historical,
        )
    except KeyboardInterrupt:
        logger.info('Exiting Trade Producer...')
