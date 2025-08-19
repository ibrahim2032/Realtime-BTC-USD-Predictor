# Price predictor service

This is used both to

- train a predictive model (aka training pipeline) and
- do inference with this model using live data (aka inference pipeline)

## TODOs

- [x] Fetch OHLC data from the Feature Store.
- [x] Visualize the data
- [x] Missing data imputation.
- [x] Create target metric we want to predict.

- [x] Build a baseline model.
- [x] Feature engineering with talib
- [x] Build an ML model
- [x] Integrate with CometML

- [x] Finish our Predictor class to load model artifact and metadata from CometML
- [x] Build REST API with Flask
- [ ] Dockerize it
- [ ] Start deploying


