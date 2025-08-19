import warnings
from typing import Optional

warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import optuna
import pandas as pd
from loguru import logger
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


def fit_xgboost_regressor(
    X: pd.DataFrame,
    y: pd.Series,
    hyper_param_search_trials: Optional[int] = 0,
) -> XGBRegressor:
    """ """
    if hyper_param_search_trials == 0:
        model = XGBRegressor()
        model.fit(X, y)

    else:

        def objective(trial):
            # Suggest values for the XGBRegressor hyperparameters
            param = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 50),
                'learning_rate': trial.suggest_float(
                    'learning_rate', 1e-4, 0.1, log=True
                ),
                'subsample': trial.suggest_uniform('subsample', 0.5, 1.0),
                'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.5, 1.0),
                'alpha': trial.suggest_float('alpha', 1e-5, 1e1, log=True),
                'lambda': trial.suggest_float('lambda', 1e-5, 1e1, log=True),
            }

            # Create an XGBRegressor model with the suggested hyperparameters
            model = XGBRegressor(**param)

            # Time-based splitting
            tscv = TimeSeriesSplit(n_splits=3)

            mae_scores = []

            for train_index, test_index in tscv.split(X):
                X_train, X_test = X.iloc[train_index], X.iloc[test_index]
                y_train, y_test = y.iloc[train_index], y.iloc[test_index]

                model.fit(
                    X_train,
                    y_train,
                    eval_set=[(X_test, y_test)],
                    early_stopping_rounds=10,
                    verbose=False,
                )
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                mae_scores.append(mae)

            # Return the mean of the mae scores across all splits
            return np.mean(mae_scores)

        # Optimize the objective function
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=hyper_param_search_trials)

        # Best hyperparameters and value
        logger.info(f'Best hyperparameters: {study.best_params}')
        logger.info(f'Best MAE: {study.best_value}')

        # Fit the model with the best hyperparameters
        model = XGBRegressor(**study.best_params)
        model.fit(X, y)

    return model


def fit_lasso_regressor(
    X: pd.DataFrame,
    y: pd.Series,
    hyper_param_search_trials: Optional[int] = 0,
) -> Lasso:
    """ """
    if hyper_param_search_trials == 0:
        logger.info('Fitting Lasso model with default hyperparameter of alpha=0.1')

        model = Pipeline([('scaler', StandardScaler()), ('lasso', Lasso(alpha=0.1))])
        # model = Lasso(alpha=0.1)
        model.fit(X, y)

    else:
        logger.info(
            f'Performing {hyper_param_search_trials} trials of hyperparameter search for Lasso model'
        )

        def objective(trial):
            """
            Objective function we want Optuna to minimize.
            """
            # Suggest a value for the alpha hyperparameter
            alpha = trial.suggest_float('alpha', 1e-4, 1e1, log=True)

            # Create a Lasso model with the suggested alpha
            model = Pipeline(
                [
                    ('scaler', StandardScaler()),  # Standardize the features
                    ('lasso', Lasso(alpha=alpha)),
                ]
            )

            # Time-based splitting
            tscv = TimeSeriesSplit(n_splits=4)

            mae_scores = []

            for train_index, test_index in tscv.split(X):
                # breakpoint()
                X_train, X_test = X.iloc[train_index], X.iloc[test_index]
                y_train, y_test = y.iloc[train_index], y.iloc[test_index]

                logger.debug(f'X_train length={len(X_train)}')
                logger.debug(f'X_test length={len(X_test)}')

                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                mae_scores.append(mae)

            # Return the mean of the MAE scores across all splits
            return np.mean(mae_scores)

        # Optimize the objective function
        study = optuna.create_study(direction='minimize')
        study.optimize(
            objective, n_trials=hyper_param_search_trials
        )  # You can adjust the number of trials

        # Best hyperparameter and value
        logger.info(f"Best alpha: {study.best_params['alpha']}")
        logger.info(f'Best MSE: {study.best_value}')

        # Fit the model with the best hyperparameter
        model = Pipeline(
            [
                ('scaler', StandardScaler()),
                ('lasso', Lasso(alpha=study.best_params['alpha'])),
            ]
        )
        model.fit(X, y)

    return model
