from typing import List, Dict

import pandas as pd
import hopsworks
import time
from hsfs.client.exceptions import FeatureStoreException

from loguru import logger
from src.config import config
    
# Login
project = hopsworks.login(
    project=config.hopsworks_project_name,
    api_key_value=config.hopsworks_api_key,
)
logger.info("Logged in to Hopsworks successfully!")

# # Feature store and group
feature_store = project.get_feature_store()


def get_feature_view() -> 'FeatureView': 
    """
    Retrieves the feature view from the feature store.
    
    Returns:
        FeatureView: The feature view object.
    """
    feature_group = feature_store.get_feature_group(
        name=config.feature_group_name,
        version=config.feature_group_version,
    )
    logger.info(f"{feature_group.name} Feature group retrieved successfully!")

    feature_view = feature_store.get_or_create_feature_view(
        name=config.feature_view_name,
        version=config.feature_view_version,
        query=feature_group.select_all(),
    )
    logger.info(f"{feature_view.name} Feature view retrieved successfully!")
    
    return feature_view
    
    
def get_features_from_the_store(
        online_or_offline: str,
    ) -> pd.DataFrame:
    """
    Fetches the features from the store and returns them as a pandas DataFrame.
    All the config parameters are read from the src.config module

    Args:
        None

    Returns:
        pd.DataFrame: The features as a pandas DataFrame sorted by timestamp (ascending)
    """

    logger.debug(f"Reading data from feature view ({online_or_offline})...")
    feature_view = get_feature_view()    

    # For the moment, let's get all rows from this feature group
    if online_or_offline == 'offline':
        try:
            features: pd.DataFrame = feature_view.get_batch_data()

        except FeatureStoreException:
            # breakpoint()
            # retry the call with the use_hive option. This is what Hopsworks recommends
            features: pd.DataFrame = feature_view.get_batch_data(read_options={"use_hive": True})
    else:
        # Fetch from the online feature store.
        # Build this list of dictionaries with the primary keys
        features = feature_view.get_feature_vectors(
            entry=get_primary_keys(last_n_minutes=20),
            return_type="pandas"
        )

    # sort the features by timestamp (ascending)
    features = features.sort_values(by='timestamp')
    logger.debug(features.head())

    return features


def get_primary_keys(
        last_n_minutes: int = 20,
    ) -> List[Dict]:
    """
    Returns a list of primary keys to read from the feature store.
    The primary keys are the product_id and timestamp.

    Args:
        last_n_minutes (int): The number of minutes to go back in time.

    Returns:
        List[Dict[str, str]]: The list of primary keys.
    """
    
    current_utc = int(time.time() * 1000)
    current_utc = current_utc - (current_utc % 60000)

    # generate a list of timestamps in miliseconds for the last 'last_n_minutes' minutes
    timestamps = [current_utc - i * 60000 for i in range(last_n_minutes)]
    
    # primary keys are pairs of product_id and timestamp
    primary_keys = [
        {
            'product_id': config.product_id,
            'timestamp': timestamp,
        } for timestamp in timestamps
    ]

    # breakpoint()

    return primary_keys
        
    
    
if __name__ == '__main__':

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--online', action='store_true')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()

    if args.online and args.offline:
        raise ValueError('You cannot pass both --online and --offline')    
    online_or_offline = 'offline' if args.offline else 'online'
    
    from loguru import logger
    data = get_features_from_the_store(online_or_offline)
    
    logger.debug(f'Received {len(data)} rows of data from the Feature Store')

    print(data.head())
    print(data.tail())
    
