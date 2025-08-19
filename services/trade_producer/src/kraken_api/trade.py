from pydantic import BaseModel


class Trade(BaseModel):
    """
    Instance of trade. model for trade data.
    """

    product_id: str
    price: float
    volume: float
    timestamp_ms: int
