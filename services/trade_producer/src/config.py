from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    kafka_broker_address: Optional[str] = None
    kafka_topic: Optional[str]
    product_ids: List[str]
    live_or_historical: str
    last_n_days: Optional[int] = 1
    cache_dir_historical: Optional[str] = None
    

    @field_validator('live_or_historical')
    @classmethod
    def validate_live_or_historical(cls, value: str) -> str:
        assert (
            value in {'live', 'historical'}
        ), f'live_or_historical must be either "live" or "historical value. Got: {value}"'
        return value


config = Config()
