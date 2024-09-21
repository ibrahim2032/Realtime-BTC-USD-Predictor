import json
from typing import Dict, List

from loguru import logger
from websocket import create_connection


class KrakenWebsocketTradeAPI:
    URL = 'wss://ws.kraken.com/v2'

    def __init__(self, product_id: str):
        self.product_id = product_id

        # Establish Connection
        self._ws = create_connection(self.URL)
        logger.info('Connection established...')

        # Subscribe to the trades for product_id
        self._subscribe(product_id)

    def _subscribe(self, product_id: str):
        """
        Establish Connection to the Kraken Websocket API and Subscribe to the trade for `product_id`.

        Args:
            product_id (str): BTC/USD
        """
        logger.info(f'Subscribing to trade for {product_id}...')
        # Subscribe to trade for product_id
        sub_msg = {
            'method': 'subscribe',
            'params': {'channel': 'trade', 'symbol': [product_id], 'snapshot': False},
        }
        self._ws.send(json.dumps(sub_msg))
        logger.info(f'Subscribed for {product_id}!')

        # Dumping first two results that give no trade data
        _ = self._ws.recv()
        _ = self._ws.recv()

    def get_trades(self) -> List[Dict]:
        message = self._ws.recv()
        logger.info('Message received', message)

        if 'heartbeat' in message:
            return []

        # Parse message string as dictionary
        message = json.loads(message)

        # extract trades data from message
        trades = []
        for trade in message['data']:
            trades.append(
                {
                    'product_id': self.product_id,
                    'price': trade['price'],
                    'volume': trade['qty'],
                    'timestamp': trade['timestamp'],
                }
            )

        return trades
