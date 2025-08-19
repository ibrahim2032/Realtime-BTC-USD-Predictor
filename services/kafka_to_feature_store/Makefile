run-dev:
	KAFKA_BROKER_ADDRESS=localhost:19092 \
	source $(CURDIR)/setup_credentials.sh && source $(CURDIR)/setup_live_config.sh && poetry run python src/main.py

run-dev-historical:
	KAFKA_BROKER_ADDRESS=localhost:19092 \
	source $(CURDIR)/setup_credentials.sh && source $(CURDIR)/setup_historical_config.sh && poetry run python src/main.py

run-dev-test:
	set -a && source $(CURDIR)/setup_credentials.sh && source $(CURDIR)/setup_live_config.sh && set +a && poetry run python test_env.py

build:
	docker build -t kafka-to-feature-store .

run: build
	docker run \
		--network=redpanda_network \
		--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		--env-file .env \
		kafka-to-feature-store

lint:
	ruff check --fix

format:
	ruff format .

lint-and-format: lint format