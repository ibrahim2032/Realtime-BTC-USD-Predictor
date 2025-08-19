# import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    kafka_broker_address: Optional[str] = None
    kafka_input_topic: str
    kafka_output_topic: str
    kafka_consumer_group: str
    ohlc_window_seconds: int 

config = Config()
