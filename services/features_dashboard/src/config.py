from pydantic_settings import BaseSettings


class Config(BaseSettings):

    # Environment variables for authentication of hopsworks api
    hopsworks_project_name: str
    hopsworks_api_key: str

    # Environment variables for feature group to read from
    feature_group_name: str
    feature_group_version: int
    
    # Environment variables for feature view to read from
    feature_view_name: str
    feature_view_version: int
    
    product_id: str



config = Config()
