.PHONY: help up down ensure-deployer wait-ministack install-infra-deps bootstrap deploy create-table seed test-api validate logs-frontend logs-ministack clean

DOCKER_COMPOSE ?= $(shell docker info >/dev/null 2>&1 && echo docker compose || echo sudo docker compose)
AWS_ACCESS_KEY_ID ?= test
AWS_SECRET_ACCESS_KEY ?= test
AWS_REGION ?= us-east-1
AWS_DEFAULT_REGION ?= $(AWS_REGION)
CDK_DEFAULT_ACCOUNT ?= 000000000000
CDK_DEFAULT_REGION ?= $(AWS_REGION)
AWS_ENDPOINT_URL ?= http://10.0.2.20:4566
AWS_S3_FORCE_PATH_STYLE ?= true
AWS_SDK_LOAD_CONFIG ?= 1

GET_TABLE_NAME = $(shell $(DOCKER_COMPOSE) exec -T $(DEPLOYER_ENV) cdk-deployer \
	.infra_venv/bin/python3 -m awscli --endpoint-url $(AWS_ENDPOINT_URL) cloudformation describe-stacks \
    --stack-name EcommercePersistence \
    --query "Stacks[0].Outputs[?OutputKey=='TableName'].OutputValue" \
    --output text 2>/dev/null)

define DEPLOYER_ENV
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

up:
	@echo "Starting all services..."
	@$(DOCKER_COMPOSE) down --remove-orphans >/dev/null 2>&1 || true
	@$(DOCKER_COMPOSE) up -d ministack cdk-deployer redis frontend
	@echo "Waiting for services to boot..."
	@sleep 5

ensure-deployer:
	@$(DOCKER_COMPOSE) up -d cdk-deployer ministack

# Instala Python de forma ultra-ligera en Alpine e instala CDK globalmente con NPM de forma nativa
install-infra-deps: ensure-deployer
	@echo "Installing light Python and CDK CLI inside Node Alpine..."
	@$(DOCKER_COMPOSE) exec -T $(DEPLOYER_ENV) cdk-deployer sh -lc '\
		if ! command -v cdk >/dev/null 2>&1; then npm install -g aws-cdk; fi && \
		if ! command -v docker >/dev/null 2>&1; then apk add --no-cache docker-cli; fi && \
		if ! command -v python3 >/dev/null 2>&1; then apk add --no-cache python3 py3-pip; fi && \
		if [ ! -d ".infra_venv" ]; then python3 -m venv .infra_venv; fi && \
		.infra_venv/bin/python3 -m pip install --upgrade pip && \
		.infra_venv/bin/python3 -m pip install awscli -r infra/requirements.txt'
	@echo "✓ Infrastructure dependencies installed"

wait-ministack: install-infra-deps
	@echo "Waiting for ministack to answer AWS calls..."
	@$(DOCKER_COMPOSE) exec -T $(DEPLOYER_ENV) cdk-deployer sh -lc '\
		until .infra_venv/bin/python3 -m awscli --endpoint-url "$(AWS_ENDPOINT_URL)" lambda list-functions >/dev/null 2>&1; do \
			sleep 2; \
		done'
	@echo "✓ MiniStack está listo."

bootstrap: wait-ministack
	@echo "Bootstrapping CDK environment..."
	@$(DOCKER_COMPOSE) exec -T $(DEPLOYER_ENV) cdk-deployer sh -lc '\
		mkdir -p ~/.aws && printf "[default]\ns3 =\n  addressing_style = path\n" > ~/.aws/config && \
		cdk bootstrap --app ".infra_venv/bin/python3 -m infra.app" aws://$(CDK_DEFAULT_ACCOUNT)/$(CDK_DEFAULT_REGION)'

deploy: bootstrap
	@echo "Limpiando cdk.out anterior..."
	@$(DOCKER_COMPOSE) exec -T cdk-deployer rm -rf cdk.out
	@echo "Deploying lambdas and API Gateway..."
	@$(DOCKER_COMPOSE) exec -T $(DEPLOYER_ENV) cdk-deployer sh -lc '\
		cdk deploy --all --require-approval never --outputs-file /tmp/cdk-outputs.json --app ".infra_venv/bin/python3 -m infra.app"'
	@echo "Writing frontend/.env..."
	@$(DOCKER_COMPOSE) exec -T $(DEPLOYER_ENV) cdk-deployer .infra_venv/bin/python3 scripts/write_frontend_env.py
	@echo "✓ Deployment complete"

create-table: wait-ministack
	@$(DOCKER_COMPOSE) exec -T -e ECOMMERCE_TABLE_NAME=$(GET_TABLE_NAME) $(DEPLOYER_ENV) cdk-deployer .infra_venv/bin/python3 scripts/create_table.py

seed: wait-ministack
	@$(DOCKER_COMPOSE) exec -T -e ECOMMERCE_TABLE_NAME=$(GET_TABLE_NAME) $(DEPLOYER_ENV) cdk-deployer .infra_venv/bin/python3 scripts/seed_data.py

test-api: wait-ministack
	@$(DOCKER_COMPOSE) exec -T $(DEPLOYER_ENV) cdk-deployer sh -lc 'PATH="$$PWD/.infra_venv/bin:$$PATH" sh scripts/test_api_gateway.sh'

clean:
	@$(DOCKER_COMPOSE) up -d cdk-deployer >/dev/null 2>&1 || true
	@$(DOCKER_COMPOSE) exec -T cdk-deployer rm -rf cdk.out .infra_venv >/dev/null 2>&1 || true
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	