run-dev:
	KAFKA_BROKER_ADDRESS=localhost:19092 \
	source $(CURDIR)/setup_live_config.sh && poetry run python src/main.py

run-dev-historical:
	KAFKA_BROKER_ADDRESS=localhost:19092 \
	source $(CURDIR)/setup_historical_config.sh && poetry run python src/main.py
	
run-dev-test:
	set -a && source $(CURDIR)/setup_live_config.sh && set +a && poetry run python test_env.py

run-dev-powershell:
	powershell -Command "Get-Content live.sh | ForEach-Object { if ($$_ -match '^\s*([^#][^=]+?)\s*=\s*(.*)$$') { [System.Environment]::SetEnvironmentVariable($$matches[1], $$matches[2]) } }; poetry run python src/main.py"

build:
	docker build -t trade-producer .

run: build
	docker run \
		--network=redpanda_network \
		--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		--env KAFKA_TOPIC=trade \
		--env PRODUCT_IDS='["BTC/USD"]' \
		--env LIVE_OR_HISTORICAL=live \
		trade-producer

run-historical: build
	docker volume create trade-producer-volume
	docker run \
		--network=redpanda_network \
		--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		--env KAFKA_TOPIC=trade_historical \
		--env PRODUCT_IDS='["BTC/USD"]' \
		--env LIVE_OR_HISTORICAL=historical \
		--env LAST_N_DAYS=90 \
		--env CACHE_DIR_HISTORICAL=/tmp/historical_trade_data \
		--volume trade-producer-volume:/tmp/historical_trade_data \
		trade-producer
lint:
	ruff check --fix

format:
	ruff format .

lint-and-format: lint format