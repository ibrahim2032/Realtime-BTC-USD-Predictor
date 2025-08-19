import json
from datetime import datetime, timezone
from typing import List

from loguru import logger
from websocket import create_connection

from src.kraken_api.trade import Trade


class KrakenWebsocketTradeAPI:
    URL = 'wss://ws.kraken.com/v2'

    def __init__(self, product_ids: str):
        self.product_ids = product_ids

        # Establish Connection
        self._ws = create_connection(self.URL)
        logger.info('Connection established...')

        # Subscribe to the trades for product_id
        self._subscribe(product_ids)

    def _subscribe(self, product_ids: List[str]):
        """
        Establish Connection to the Kraken Websocket API and Subscribe to the trade for `product_id`.

        Args:
            product_ids (str): The product id to subscribe to.
        """
        logger.info(f'Subscribing to trade for {product_ids}...')
        # Subscribe to trade for product_id
        sub_msg = {
            'method': 'subscribe',
            'params': {'channel': 'trade', 'symbol': product_ids, 'snapshot': False},
        }
        self._ws.send(json.dumps(sub_msg))
        logger.info(f'Subscribed for {product_ids}!')

        # Dumping first two results that give no trade data
        _ = self._ws.recv()

        for product_id in product_ids:
            response = self._ws.recv()
            data = json.loads(response)

            if not data.get('success', True):
                logger.warning(
                    f"Subscription failed: {data.get('error')} for {data.get('symbol')}"
                )
            else:
                symbol = data.get('result', {}).get('symbol', product_id)
                logger.info(f'Subscribed to {symbol} successfully')

    def get_trades(self) -> List[Trade]:
        message = self._ws.recv()
        # breakpoint()

        # logger.info('Message received', message)

        if 'heartbeat' in message:
            return []

        # Parse message string as dictionary
        message = json.loads(message)

        # extract trades data from message
        trades = []
        for trade in message['data']:
            timestamp_ms = self.to_ms(trade['timestamp'])

            trades.append(
                Trade(
                    product_id=trade['symbol'],
                    price=trade['price'],
                    volume=trade['qty'],
                    timestamp_ms=timestamp_ms,
                )
            )
            # logger.info(f'Trade: {trade}')

        return trades

    def is_done(self) -> bool:
        """
        Check if the Websocket stops fetching data.

        Returns:
            bool: False because websocket never stops feteching data.
        """
        return False

    @staticmethod
    # Transform timestamp from '2025-04-03T00:45:31.125659Z' to milliseconds
    def to_ms(timestamp: str) -> int:
        """
        Transform timestamp from '2025-04-03T00:45:31.125659Z' to milliseconds.

        Args:
            timestamp (str): '2025-04-03T00:45:31.125659Z'

        Returns:
            int: 1680483931125
        """
        # return int(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp() * 1000)
        timestamp = datetime.fromisoformat(timestamp[:-1]).replace(tzinfo=timezone.utc)
        return int(timestamp.timestamp() * 1000)
