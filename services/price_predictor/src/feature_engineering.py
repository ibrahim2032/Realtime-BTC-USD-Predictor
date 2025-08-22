from typing import Optional

import pandas as pd
import talib
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureEngineeringPipeline(BaseEstimator, TransformerMixin):
    """
    A Scikit Learn transformer that adds features to the input DataFrame
    simply wrap the existing `add_features` function into a Scikit Learn transformer
    persist the pipeline using the `joblib` library.

    - run hyper-parameter optimization of the feature engineering pipeline
    - save the best pipeline to disk, together with the model pickle, instead of having
      to save a separate JSON file with these parameters.
    """

    def __init__(
        self,
        n_candles_into_future: int,
        # momentum indicators
        RSI_timeperiod: Optional[int] = 14,
        MOM_timeperiod: Optional[int] = 10,
        MACD_fastperiod: Optional[int] = 12,
        MACD_slowperiod: Optional[int] = 26,
        MACD_signalperiod: Optional[int] = 9,
        MFI_timeperiod: Optional[int] = 14,
        ADX_timeperiod: Optional[int] = 14,
        ROC_timeperiod: Optional[int] = 10,
        STOCH_fastk_period: Optional[int] = 5,
        STOCH_slowk_period: Optional[int] = 3,
        STOCH_slowk_matype: Optional[int] = 0,
        STOCH_slowd_period: Optional[int] = 3,
        STOCH_slowd_matype: Optional[int] = 0,
        ULTOSC_timeperiod1: Optional[int] = 7,
        ULTOSC_timeperiod2: Optional[int] = 14,
        ULTOSC_timeperiod3: Optional[int] = 28,
        # statistic indicators
        STDDEV_timeperiod: Optional[int] = 5,
        STDDEV_nbdev: Optional[int] = 1,
        # volatility indicators
        ATR_timeperiod: Optional[int] = 14,
    ):
        """
        Saves inputs parameters as attributes

        Args:
            - n_candles_into_future: int: the number of candles into the future to predict

            # momentum indicators
            - RSI_timeperiod: Optional[int]: the time period for the RSI indicator.
            - MOM_timeperiod: Optional[int]: the time period for the momentum indicator.
            - MACD_fastperiod: Optional[int]: the fast period for the MACD indicator.
            - MACD_slowperiod: Optional[int]: the slow period for the MACD indicator.
            - MACD_signalperiod: Optional[int]: the signal period for the MACD indicator.
            - MFI_timeperiod: Optional[int]: the time period for the MFI indicator.
            - ADX_timeperiod: Optional[int]: the time period for the ADX indicator.
            - ROC_timeperiod: Optional[int]: the time period for the ROC indicator.
            - STOCH_fastk_period: Optional[int]: the fastk period for the STOCH indicator.
            - STOCH_slowk_period: Optional[int]: the slowk period for the STOCH indicator.
            - STOCH_slowk_matype: Optional[int]: the matype for the STOCH indicator.
            - STOCH_slowd_period: Optional[int]: the slowd period for the STOCH indicator.
            - STOCH_slowd_matype: Optional[int]: the matype for the STOCH indicator.
            - ULTOSC_timeperiod1: Optional[int]: the time period for the ULTOSC indicator.
            - ULTOSC_timeperiod2: Optional[int]: the time period for the ULTOSC indicator.
            - ULTOSC_timeperiod3: Optional[int]: the time period for the ULTOSC indicator.

            # statistic indicators
            - STDDEV_timeperiod: Optional[int]: the time period for the STDDEV indicator
            - STDDEV_nbdev: Optional[int]: the nbdev for the STDDEV indicator

            # volatility indicators
            - ATR_timeperiod: Optional[int]: the time period for the ATR indicator

        Returns:
            - None
        """
        self.n_candles_into_future = n_candles_into_future

        # momentum indicators
        self.RSI_timeperiod = RSI_timeperiod
        self.MOM_timeperiod = MOM_timeperiod
        self.MACD_fastperiod = MACD_fastperiod
        self.MACD_slowperiod = MACD_slowperiod
        self.MACD_signalperiod = MACD_signalperiod
        self.MFI_timeperiod = MFI_timeperiod
        self.ADX_timeperiod = ADX_timeperiod
        self.ROC_timeperiod = ROC_timeperiod
        self.STOCH_fastk_period = STOCH_fastk_period
        self.STOCH_slowk_period = STOCH_slowk_period
        self.STOCH_slowk_matype = STOCH_slowk_matype
        self.STOCH_slowd_period = STOCH_slowd_period
        self.STOCH_slowd_matype = STOCH_slowd_matype
        self.ULTOSC_timeperiod1 = ULTOSC_timeperiod1
        self.ULTOSC_timeperiod2 = ULTOSC_timeperiod2
        self.ULTOSC_timeperiod3 = ULTOSC_timeperiod3

        # statistic indicators
        self.STDDEV_timeperiod = STDDEV_timeperiod
        self.STDDEV_nbdev = STDDEV_nbdev

        # volatility indicators
        self.ATR_timeperiod = ATR_timeperiod

        self.final_features = [
            'RSI',
            'MOM',
            'MACD',
            'MACD_signal',
            # 'MFI',
            'ADX',
            'ROC',
            'STOCH_slowk',
            'STOCH_slowd',
            'ULTOSC',
            'STDDEV',
            'ATR',
            'last_observed_target',
            'day_of_week',
            'hour_of_day',
            'minute_of_hour',
        ]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return add_features(
            X,
            n_candles_into_future=self.n_candles_into_future,
            RSI_timeperiod=self.RSI_timeperiod,
            MOM_timeperiod=self.MOM_timeperiod,
            MACD_fastperiod=self.MACD_fastperiod,
            MACD_slowperiod=self.MACD_slowperiod,
            MACD_signalperiod=self.MACD_signalperiod,
            MFI_timeperiod=self.MFI_timeperiod,
            ADX_timeperiod=self.ADX_timeperiod,
            ROC_timeperiod=self.ROC_timeperiod,
            STOCH_fastk_period=self.STOCH_fastk_period,
            STOCH_slowk_period=self.STOCH_slowk_period,
            STOCH_slowk_matype=self.STOCH_slowk_matype,
            STOCH_slowd_period=self.STOCH_slowd_period,
            STOCH_slowd_matype=self.STOCH_slowd_matype,
            ULTOSC_timeperiod1=self.ULTOSC_timeperiod1,
            ULTOSC_timeperiod2=self.ULTOSC_timeperiod2,
            ULTOSC_timeperiod3=self.ULTOSC_timeperiod3,
            STDDEV_timeperiod=self.STDDEV_timeperiod,
            STDDEV_nbdev=self.STDDEV_nbdev,
            ATR_timeperiod=self.ATR_timeperiod,
        )[self.final_features]

    # @property
    # def feature_names_out(self):
    #     return self.features_to_use


def add_features(
    X: pd.DataFrame,
    # Use this to compute the last observed target
    n_candles_into_future: int,
    # momentum indicators
    RSI_timeperiod: Optional[int] = 14,
    MOM_timeperiod: Optional[int] = 10,
    MACD_fastperiod: Optional[int] = 12,
    MACD_slowperiod: Optional[int] = 26,
    MACD_signalperiod: Optional[int] = 9,
    MFI_timeperiod: Optional[int] = 14,
    ADX_timeperiod: Optional[int] = 14,
    ROC_timeperiod: Optional[int] = 10,
    STOCH_fastk_period: Optional[int] = 5,
    STOCH_slowk_period: Optional[int] = 3,
    STOCH_slowk_matype: Optional[int] = 0,
    STOCH_slowd_period: Optional[int] = 3,
    STOCH_slowd_matype: Optional[int] = 0,
    ULTOSC_timeperiod1: Optional[int] = 7,
    ULTOSC_timeperiod2: Optional[int] = 14,
    ULTOSC_timeperiod3: Optional[int] = 28,
    # statistic indicators
    STDDEV_timeperiod: Optional[int] = 5,
    STDDEV_nbdev: Optional[int] = 1,
    # volatility indicators
    ATR_timeperiod: Optional[int] = 14,
) -> pd.DataFrame:
    """ """
    X_ = X.copy()

    # add momentum indicators
    X_ = add_RSI(X_, timeperiod=RSI_timeperiod)
    X_ = add_MOM(X_, timeperiod=MOM_timeperiod)
    X_ = add_MACD(
        X_,
        fastperiod=MACD_fastperiod,
        slowperiod=MACD_slowperiod,
        signalperiod=MACD_signalperiod,
    )
    # X_ = add_MFI(X_, timeperiod=MFI_timeperiod)
    X_ = add_ADX(X_, timeperiod=ADX_timeperiod)
    X_ = add_ROC(X_, timeperiod=ROC_timeperiod)
    X_ = add_STOCH(
        X_,
        fastk_period=STOCH_fastk_period,
        slowk_period=STOCH_slowk_period,
        slowk_matype=STOCH_slowk_matype,
        slowd_period=STOCH_slowd_period,
        slowd_matype=STOCH_slowd_matype,
    )
    X_ = add_ULTOSC(
        X_,
        timeperiod1=ULTOSC_timeperiod1,
        timeperiod2=ULTOSC_timeperiod2,
        timeperiod3=ULTOSC_timeperiod3,
    )

    # add statistic indicators
    X_ = add_STDDEV(X_, timeperiod=STDDEV_timeperiod, nbdev=STDDEV_nbdev)

    # add volatility indicators
    X_ = add_ATR(X_, timeperiod=ATR_timeperiod)

    # add last observed target
    X_ = add_last_observed_target(
        X_,
        n_candles_into_future=n_candles_into_future,
        # discretization_thresholds=discretization_thresholds,
    )

    # add temporal features
    X_ = add_temporal_features(X_)

    return X_


def add_RSI(
    X: pd.DataFrame,
    timeperiod: Optional[int] = 14,
) -> pd.DataFrame:
    """
    Adds a new column called `rsi` to the given DataFrame with the RSI indicator
    """
    X['RSI'] = talib.RSI(X['close'], timeperiod=timeperiod)
    return X


def add_MOM(
    X: pd.DataFrame,
    timeperiod: Optional[int] = 10,
) -> pd.DataFrame:
    """
    Adds a new column called `momentum` to the given DataFrame with the momentum indicator
    """
    X['MOM'] = talib.MOM(X['close'], timeperiod=timeperiod)
    return X


def add_MACD(
    X: pd.DataFrame,
    fastperiod: Optional[int] = 12,
    slowperiod: Optional[int] = 26,
    signalperiod: Optional[int] = 9,
) -> pd.DataFrame:
    """
    Adds the MACD (Moving Average Convergence Divergence) indicator to the `ts_data`
    """
    macd, macd_signal, _ = talib.MACD(
        X['close'],
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod,
    )
    X['MACD'] = macd
    X['MACD_signal'] = macd_signal
    return X


def add_MFI(
    X: pd.DataFrame,
    timeperiod: Optional[int] = 14,
) -> pd.DataFrame:
    """
    Adds a new column called `mfi` to the given DataFrame with the MFI indicator
    """
    X['MFI'] = talib.MFI(
        X['high'], X['low'], X['close'], X['volume'], timeperiod=timeperiod
    )
    return X


def add_ADX(
    X: pd.DataFrame,
    timeperiod: Optional[int] = 14,
) -> pd.DataFrame:
    """
    Adds a new column called `adx` to the given DataFrame with the ADX indicator
    """
    X['ADX'] = talib.ADX(X['high'], X['low'], X['close'], timeperiod=timeperiod)
    return X


def add_ROC(
    X: pd.DataFrame,
    timeperiod: Optional[int] = 10,
) -> pd.DataFrame:
    """
    Adds a new column called `roc` to the given DataFrame with the ROC indicator
    """
    X['ROC'] = talib.ROC(X['close'], timeperiod=timeperiod)
    return X


def add_STOCH(
    X: pd.DataFrame,
    fastk_period: Optional[int] = 5,
    slowk_period: Optional[int] = 3,
    slowk_matype: Optional[int] = 0,
    slowd_period: Optional[int] = 3,
    slowd_matype: Optional[int] = 0,
) -> pd.DataFrame:
    """
    Adds the Stochastic Oscillator indicator to the `ts_data`
    """
    slowk, slowd = talib.STOCH(
        X['high'],
        X['low'],
        X['close'],
        fastk_period=fastk_period,
        slowk_period=slowk_period,
        slowk_matype=slowk_matype,
        slowd_period=slowd_period,
        slowd_matype=slowd_matype,
    )
    X['STOCH_slowk'] = slowk
    X['STOCH_slowd'] = slowd
    return X


def add_ULTOSC(
    X: pd.DataFrame,
    timeperiod1: Optional[int] = 7,
    timeperiod2: Optional[int] = 14,
    timeperiod3: Optional[int] = 28,
) -> pd.DataFrame:
    """
    Adds the Ultimate Oscillator indicator to the `ts_data`
    """
    ultosc = talib.ULTOSC(
        X['high'],
        X['low'],
        X['close'],
        timeperiod1=timeperiod1,
        timeperiod2=timeperiod2,
        timeperiod3=timeperiod3,
    )
    X['ULTOSC'] = ultosc
    return X


def add_STDDEV(
    X: pd.DataFrame,
    timeperiod: Optional[int] = 5,
    nbdev: Optional[int] = 1,
) -> pd.DataFrame:
    """
    Adds a new column with the standard deviation to capture volatility in
    the market
    """
    X['STDDEV'] = talib.STDDEV(X['close'], timeperiod=timeperiod, nbdev=nbdev)
    return X


def add_ATR(
    X: pd.DataFrame,
    timeperiod: Optional[int] = 14,
) -> pd.DataFrame:
    """
    Adds a new column with the Average True Range (ATR) indicator to the `ts_data`
    """
    X['ATR'] = talib.ATR(X['high'], X['low'], X['close'], timeperiod=timeperiod)
    return X


def add_temporal_features(X: pd.DataFrame) -> pd.DataFrame:
    """
    Adds columns with temporal features to the given DataFrame using the X['datetime']
    - day_of_week
    - hour_of_day
    - minute_of_hour

    Args:
        - X: pd.DataFrame: the input DataFrame

    Returns:
        - pd.DataFrame: the input DataFrame with the new columns
    """
    X_ = X.copy()

    X_['day_of_week'] = X_['datetime'].dt.dayofweek
    X_['hour_of_day'] = X_['datetime'].dt.hour
    X_['minute_of_hour'] = X_['datetime'].dt.minute

    return X_


def add_last_observed_target(
    X: pd.DataFrame,
    n_candles_into_future: int,
    # discretization_thresholds: list,
) -> pd.DataFrame:
    """
    Adds the target column to the given DataFrame.

    Args:
        - X: pd.DataFrame: the input DataFrame
        - n_candles_into_future: int: the number of candles into the future to predict
        - discretization_thresholds: list: the thresholds to discretize the target

    Returns:
        - pd.DataFrame: the input DataFrame with the new column
    """
    X_ = X.copy()

    X_['last_observed_target'] = X_['close'].pct_change(n_candles_into_future)

    # the first `n_candles_into_future` rows will have NaN as target
    # because no have historical data to compute the pct_change
    # Imputing missing values or not at this stage depends on the model you are using
    # - As far as I know, Random Forests can handle missing values
    # - Neural Networks can't handle missing values
    # - Boosting trees can handle missing values
    # TODO: check if the model you are using can handle missing values
    # X_['last_observed_target'].fillna(0, inplace=True)

    return X_
