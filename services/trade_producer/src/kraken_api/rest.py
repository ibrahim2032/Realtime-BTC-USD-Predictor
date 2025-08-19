import json
import requests
import pandas as pd

from datetime import datetime, timezone
from time import sleep
from typing import Dict, List, Tuple, Optional
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.kraken_api.trade import Trade


class KrakenRestAPIMultipleProducts:
    def __init__(
        self, 
        product_ids: List[str], 
        last_n_days: int,
        n_threads: Optional[int] = 1,
        cache_dir: Optional[str] = None,
    ) -> None:
        self.product_ids = product_ids
        
        self.kraken_apis = [
            KrakenRestAPI(product_id=product_id, last_n_days=last_n_days, cache_dir=cache_dir)
            for product_id in product_ids
        ]
        
        self.n_threads = n_threads
        

    def get_trades(self) -> List[Dict]:
        """
        Fetches trades data from KrakenRestAPI in self.kraken_apis for the given product_id and time range.

        Args: None

        Returns:
            List[Dict]: A list of dictionaries containing trade data for all the product_ids.
        """
        if self.n_threads == 1:
            # This is the serial version
            trades: List[Dict] = []

            for kraken_api in self.kraken_apis:
                if kraken_api.is_done():
                    continue
                else:
                    trades += kraken_api.get_trades()
            return trades
        else:
            # This is a parallel version           
            with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
                trades = list(executor.map(self.get_trades_for_one_product, self.kraken_apis))
                
                # trades is a list of lists, so we need to flatten it
                trades = [trade for sublist in trades for trade in sublist]
            return trades
        
        
    def get_trades_for_one_product(self, kraken_api: 'KrakenRestAPI') -> List[Trade]:
        """
        Fetches trades data for the given product_id and time range.

        Args:
            kraken_api (KrakenRestAPI): The KrakenRestAPI object for the given product_id.

        Returns:
            List[Trade]: A list of Trade objects containing trade data.
        """
        if not kraken_api.is_done():
            return kraken_api.get_trades()
        return []


    def is_done(self) -> bool:
        """
        Check if the historical data fetching is done.

        Returns:
            bool: True if fetching is done, False otherwise.
        """
        for kraken_api in self.kraken_apis:
            if not kraken_api.is_done():
                return False
        return True
        # return all([kraken_api.is_done() for kraken_api in self.kraken_apis])


class KrakenRestAPI:
    URL = 'https://api.kraken.com/0/public/Trades?pair={product_id}&since={since_sec}'

    def __init__(self, product_id: str, last_n_days: int, cache_dir: Optional[str] = None) -> None:
        """
        Initializes the KrakenRestAPI object with the given product_id and last_n_days.
        Args:
            product_id (str): The product ID for which to fetch historical data.
            last_n_days (int): Number of days to fetch historical data.
            cache_dir (Optional[str]): Directory to cache the data. Defaults to None.
            
        Returns:
            None
        """
        self.product_id = product_id
        self.from_ms, self.to_ms = self._init_from_to_ms(last_n_days)

        logger.debug(
            f'Initializing KrakenRestAPI for {product_id} from {ts_to_date(self.from_ms)} to {ts_to_date(self.to_ms)}..'
        )
        # breakpoint()
        # The timestamp from which we want to fetch historical data
        self.last_trade_ms = self.from_ms

        # Check if the historical data fetching is done (default: False): if data['result']['product_id']['last'] >= self.to_ms
        # self._is_done = False
        
        # Cache_dir is the directory where the historical data is cached to speed up the process
        # self.use_cache = False
        # if cache_dir is not None:
        #     self.cache = CachedTradeData(cache_dir)
        #     self.use_cache = True
        # Cache_dir is the directory where the historical data is cached to speed up the process
        self.use_cache = False

        if cache_dir is not None:
            logger.info(f"Setting up cache in directory: {cache_dir}")

            try:
                self.cache = CachedTradeData(cache_dir)
                self.use_cache = True
                logger.debug(f"Cache successfully initialized")
            except Exception as e:
                logger.error(f"Failed to set up cache: {str(e)}")


    @staticmethod
    def _init_from_to_ms(last_n_days: int) -> Tuple[int, int]:
        """
        Initialize the from and to milliseconds for the given last_n_days. and return them as a tuple.
        The from time is calculated as the current time - last_n_days.

        Args:
            last_n_days (int): Number of days to fetch historical data.

        Returns:
            Tuple[int, int]: The from and to time in milliseconds
        """
        # Get UTC time in seconds
        today_date = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Get the current time in milliseconds
        to_ms = int(today_date.timestamp() * 1000)
        # Calculate the from time in milliseconds
        from_ms = to_ms - last_n_days * 24 * 60 * 60 * 1000
        return from_ms, to_ms

    def get_trades(self) -> List[Trade]:
        """
        Retruns the next batch of trades from product_id from
        -> the cache (if use_cache is True and the data is already cached)
        -> the Kraken API (if use_cache is False or the data is not cached)

        Args: None

        Returns:
            List[Trade]: A list of Trade objects containing trade data.
        """
        
        since_ns = self.last_trade_ms * 1_000_000
        payload = {}
        headers = {'Accept': 'application/json'}
        url = self.URL.format(product_id=self.product_id, since_sec=since_ns)
        logger.debug(f'{url=}')
            
        if self.use_cache and self.cache.has(url):
            # cache is enabled, read data from cache
            trades = self.cache.read(url)
            logger.debug(f'Loaded {len(trades)} trades for {self.product_id} from cache, since: {ns_to_date(since_ns)}. from cache.')
        else:
            # Otherwise, fetch the data from the Kraken Rest API
            response = requests.request('GET', url, headers=headers, data=payload)
            
            # Parse string response as dictionary
            data = json.loads(response.text)
            
            if ('error' in data) and ('EGeneral: Too many requests' in data['error']):
                # If the error is "Too many requests", sleep for 30 seconds and return an empty list
                # to avoid hitting the rate limit
                logger.info(f'Sleeping for 30 Seconds, Too many requests, : {data["error"]}')
                sleep(30)
            
            trades = [
                Trade(
                    price=float(trade[0]),
                    volume=float(trade[1]),
                    timestamp_ms=int(trade[2] * 1000),  # Convert to milliseconds
                    product_id=self.product_id,
                )
                for trade in data['result'][self.product_id]
            ]
            logger.debug(f'Fetched {len(trades)} trades for {self.product_id} from Kraken API, since: {ns_to_date(since_ns)}')
        
            if self.use_cache:
                # cache is enabled, write data to cache
                self.cache.write(url, trades)
                logger.debug(f'Wrote {len(trades)} trades for {self.product_id} to cache, since: {ns_to_date(since_ns)}.')
            
            # slow down the requests to avoid rate limiting by Kraken API
            sleep(1)
                

        if trades[-1].timestamp_ms == self.last_trade_ms:
            # if the last trade timestamp in the batch is the same as self.last_trade_ms,
            # then we need to increment it by 1 to avoid repeating the exact same API request,
            # which would result in an infinite loop
            self.last_trade_ms = trades[-1].timestamp_ms + 1
        else:
            # otherwise, update self.last_trade_ms to the timestamp of the last trade
            # in the batch
            self.last_trade_ms = trades[-1].timestamp_ms
        
        # filter out trades that are after the end timestamp
        trades = [trade for trade in trades if trade.timestamp_ms <= self.to_ms]

        # if ns_to_date(since_ns) == '2024-04-30 18:33:41':
        #     # self.cache._get_file_path(url)
        #     breakpoint()

        return trades
    
    def is_done(self) -> bool:
        """
        Check if the historical data fetching is done.

        Returns:
            bool: True if fetching is done, False otherwise.
        """
        return self.last_trade_ms >= self.to_ms
    
    
class CachedTradeData:
    """
    Class to cache the trade data to avoid fetching the same data multiple times
    """

    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = Path(cache_dir)
        
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
    
    
    def read(self, url: str) -> List[Trade]:
        """
        Reads from the cache the trade data for the given url
        """
        file_path = self._get_file_path(url)

        if file_path.exists():
            # read the data from the parquet file
            import pandas as pd

            data = pd.read_parquet(file_path)
            # transform the data to a list of Trade objects
            return [Trade(**trade) for trade in data.to_dict(orient='records')]

        return []

    def write(self, url: str, trades: List[Trade]) -> None:
        """
        Saves the given trades to a parquet file in the cache directory.
        """
        if not trades:
            return

        # transform the trades to a pandas DataFrame
        import pandas as pd

        data = pd.DataFrame([trade.model_dump() for trade in trades])

        # write the DataFrame to a parquet file
        file_path = self._get_file_path(url)
        data.to_parquet(file_path)

    def has(self, url: str) -> bool:
        """
        Returns True if the cache has the trade data for the given url, False otherwise.
        """
        file_path = self._get_file_path(url)
        return file_path.exists()

    def _get_file_path(self, url: str) -> str:
        """
        Returns the file path where the trade data for the given url is (or will be) stored.
        """
        # use the given url to generate a unique file name in a deterministic way
        import hashlib

        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f'{url_hash}.parquet'
        # return self.cache_dir / f'{product_id.replace ("/","-")}_{from_ms}.parquet'


def ts_to_date(ts: int) -> str:
    """
    Transform a timestamp in Unix milliseconds to a human-readable date

    Args:
        ts (int): A timestamp in Unix milliseconds

    Returns:
        str: A human-readable date in the format '%Y-%m-%d %H:%M:%S'
    """
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime(
        '%Y-%m-%d %H:%M:%S'
    )


def ns_to_date(ns: int) -> str:
    """
    Transform a timestamp in Unix nanoseconds to a human-readable date

    Args:
        ns (int): A timestamp in Unix nanoseconds

    Returns:
        str: A human-readable date in the format '%Y-%m-%d %H:%M:%S'
    """
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ns / 1_000_000_000, tz=timezone.utc).strftime(
        '%Y-%m-%d %H:%M:%S'
    )