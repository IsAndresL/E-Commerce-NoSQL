.PHONY: help up down ensure-devcontainer bootstrap deploy create-table seed test-api validate logs-frontend logs-ministack clean

DOCKER_COMPOSE := sudo docker compose
AWS_ACCESS_KEY_ID ?= test
AWS_SECRET_ACCESS_KEY ?= test
AWS_REGION ?= us-east-1
AWS_DEFAULT_REGION ?= $(AWS_REGION)
CDK_DEFAULT_ACCOUNT ?= 000000000000
CDK_DEFAULT_REGION ?= $(AWS_REGION)
AWS_ENDPOINT_URL ?= http://ministack:4566
AWS_S3_FORCE_PATH_STYLE ?= true
AWS_SDK_LOAD_CONFIG ?= 1

define DEVCONTAINER_ENV
	-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	-e AWS_REGION=$(AWS_REGION) \
	-e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
	-e CDK_DEFAULT_ACCOUNT=$(CDK_DEFAULT_ACCOUNT) \
	-e CDK_DEFAULT_REGION=$(CDK_DEFAULT_REGION) \
	-e AWS_ENDPOINT_URL=$(AWS_ENDPOINT_URL) \
	-e AWS_S3_FORCE_PATH_STYLE=$(AWS_S3_FORCE_PATH_STYLE) \
	-e AWS_SDK_LOAD_CONFIG=$(AWS_SDK_LOAD_CONFIG)
endef

help:
	@echo "E-Commerce Serverless Docker Makefile"
	@echo "======================================"
	@echo ""
	@echo "Usage:"
	@echo "  make up              - Start ministack, devcontainer, redis and frontend"
	@echo "  make down            - Stop all services"
	@echo "  make bootstrap       - Bootstrap the CDK app inside devcontainer"
	@echo "  make deploy          - Bootstrap and deploy lambdas and API Gateway"
	@echo "  make create-table    - Create DynamoDB ecommerce table"
	@echo "  make seed            - Seed initial data"
	@echo "  make test-api        - Test API Gateway connectivity and routes"
	@echo "  make validate        - Validate complete Frontend→Lambda→DynamoDB connection"
	@echo "  make logs-frontend   - Show frontend logs"
	@echo "  make logs-ministack  - Show ministack logs"
	@echo "  make clean           - Remove containers and volumes"
	@echo ""
	@echo "Quick start:"
	@echo "  make up && make deploy && make create-table && make seed"
	@echo "  Then: make validate"
	@echo ""

up:
	@echo "Starting all services..."
	@$(DOCKER_COMPOSE) down --remove-orphans >/dev/null 2>&1 || true
	@$(DOCKER_COMPOSE) up -d ministack devcontainer redis frontend
	@echo "Waiting for ministack to be ready..."
	@sleep 5
	@echo "✓ Services started"
	@echo "  - Frontend: http://localhost:5173"
	@echo "  - Devcontainer: available for bootstrap/deploy/scripts"
	@echo "  - Ministack API: http://localhost:4566"
	@echo "  - DynamoDB: http://localhost:4566"

down:
	@echo "Stopping all services..."
	@$(DOCKER_COMPOSE) down
	@echo "✓ Services stopped"

ensure-devcontainer:
	@$(DOCKER_COMPOSE) up -d devcontainer ministack

wait-ministack:
	@echo "Waiting for ministack to answer AWS calls..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer sh -lc 'until aws --endpoint-url "$(AWS_ENDPOINT_URL)" lambda list-functions >/dev/null 2>&1; do sleep 2; done'

bootstrap: ensure-devcontainer wait-ministack
	@echo "Bootstrapping CDK environment inside devcontainer..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer sh -lc 'mkdir -p ~/.aws && printf "[default]\ns3 =\n  addressing_style = path\n" > ~/.aws/config && cdk bootstrap --app "python3 -m infra.app" aws://$(CDK_DEFAULT_ACCOUNT)/$(CDK_DEFAULT_REGION)'
	@echo "✓ Bootstrap complete"

deploy: bootstrap
	@echo "Deploying lambdas and API Gateway with CDK inside devcontainer..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer sh -lc 'mkdir -p ~/.aws && printf "[default]\ns3 =\n  addressing_style = path\n" > ~/.aws/config && cdk deploy --all --require-approval never --outputs-file /tmp/cdk-outputs.json --app "python3 -m infra.app"'
	@echo "Writing frontend/.env with API URL from CDK outputs..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer python3 scripts/write_frontend_env.py
	@echo "✓ Deployment complete"

create-table: ensure-devcontainer wait-ministack
	@echo "Creating DynamoDB tables..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer python3 scripts/create_table.py
	@echo "✓ Tables created"

seed: ensure-devcontainer wait-ministack
	@echo "Seeding initial data..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer python3 scripts/seed_data.py
	@echo "✓ Data seeded"

test-api: ensure-devcontainer wait-ministack
	@echo "Testing API Gateway..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer sh scripts/test_api_gateway.sh

validate: ensure-devcontainer wait-ministack
	@echo "Validating Frontend→Lambda→DynamoDB connection..."
	@$(DOCKER_COMPOSE) exec -T $(DEVCONTAINER_ENV) devcontainer sh scripts/validate_connection.sh

test-lambdas: ensure-devcontainer wait-ministack
	@echo "Testing Lambda endpoints via API Gateway base from frontend/.env"
	@if [ -f frontend/.env ]; then \
		API_BASE=$$(sed -n 's/^VITE_API_BASE_URL=//p' frontend/.env); \
	else \
		echo "frontend/.env not found. Run 'make deploy' first to generate it."; exit 1; \
	fi; \
	if [ -z "$$API_BASE" ]; then echo "VITE_API_BASE_URL is empty in frontend/.env"; exit 1; fi; \
	echo "Using API_BASE=$$API_BASE"; \
	echo; echo "[Dashboard] GET $$API_BASE/ecommerce/dashboard-data?user_id=1&order_id=554"; \
	curl -sS -D - "$$API_BASE/ecommerce/dashboard-data?user_id=1&order_id=554" || true; \
	echo; echo "[Products] GET $$API_BASE/products"; \
	curl -sS -D - "$$API_BASE/products" || true; \
	echo; echo "[Profile] GET $$API_BASE/ecommerce/user/1/profile"; \
	curl -sS -D - "$$API_BASE/ecommerce/user/1/profile" || true; \
	echo

logs-frontend:
	@echo "Frontend logs (press Ctrl+C to exit):"
	@$(DOCKER_COMPOSE) logs -f frontend

logs-ministack:
	@echo "Ministack logs (press Ctrl+C to exit):"
	@$(DOCKER_COMPOSE) logs -f ministack

clean:
	@echo "Removing containers and volumes..."
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo "✓ Cleanup complete"