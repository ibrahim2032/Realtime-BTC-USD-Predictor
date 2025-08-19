run-dev:
	KAFKA_BROKER_ADDRESS=localhost:19092 \
	source $(CURDIR)/setup_live_config.sh && poetry run python src/main.py

run-dev-historical:
	KAFKA_BROKER_ADDRESS=localhost:19092 \
	source $(CURDIR)/setup_historical_config.sh && poetry run python src/main.py
	
run-dev-test:
	KAFKA_BROKER_ADDRESS=localhost:19092 \
	source $(CURDIR)/setup_historical_config.sh && poetry run python test_env.py

build:
	docker build -t trade-to-ohlc .

run: build
	docker run \
		--network=redpanda_network \
		--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		--env OHLC_WINDOW_SECONDS=60 \
		trade-to-ohlc

lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .
	
lint-and-format: lint format