.PHONY: help up down bootstrap deploy create-table seed test-api validate logs-frontend logs-ministack clean

help:
	@echo "E-Commerce Serverless Docker Makefile"
	@echo "======================================"
	@echo ""
	@echo "Usage:"
	@echo "  make up              - Start all services (ministack, dynamodb, redis, frontend)"
	@echo "  make down            - Stop all services"
	@echo "  make deploy          - Deploy lambdas and API Gateway (requires: services running)"
	@echo "  make create-table    - Create DynamoDB ecommerce table"
	@echo "  make seed            - Seed initial data"
	@echo "  make test-api        - Test API Gateway connectivity and routes"
	@echo "  make validate        - Validate complete Frontend→Lambda→DynamoDB connection"
	@echo "  make logs-frontend   - Show frontend logs"
	@echo "  make logs-ministack  - Show ministack/localstack logs"
	@echo "  make clean           - Remove containers and volumes"
	@echo ""
	@echo "Quick start:"
	@echo "  make up && make deploy && make create-table && make seed"
	@echo "  Then: make validate"
	@echo ""

up:
	@echo "Starting all services..."
	@sudo docker compose up -d ministack dynamodb-local redis
	@echo "Waiting for ministack to be ready..."
	@sleep 5
	@sudo docker compose up -d deployer frontend
	@echo "✓ Services started"
	@echo "  - Frontend: http://localhost:5173"
	@echo "  - Ministack API: http://localhost:4566"
	@echo "  - DynamoDB: http://localhost:8001"

down:
	@echo "Stopping all services..."
	@sudo docker compose down
	@echo "✓ Services stopped"

bootstrap:
	@echo "Bootstrapping CDK environment..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ACCESS_KEY_ID=local \
		-e AWS_SECRET_ACCESS_KEY=local \
		-e AWS_DEFAULT_REGION=us-east-1 \
		-e CDK_DEFAULT_ACCOUNT=000000000000 \
		-e CDK_DEFAULT_REGION=us-east-1 \
		-e AWS_ENDPOINT_URL=http://ministack:4566 \
		deployer -c 'cdk bootstrap aws://000000000000/us-east-1'
	@echo "✓ Bootstrap complete"

deploy:
	@echo "Limpiando cdk.out anterior..."
	@sudo rm -rf cdk.out
	@echo "Building deployer image..."
	@sudo docker compose build deployer
	@echo "Bootstrapping CDK..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ACCESS_KEY_ID=local \
		-e AWS_SECRET_ACCESS_KEY=local \
		-e AWS_DEFAULT_REGION=us-east-1 \
		-e CDK_DEFAULT_ACCOUNT=000000000000 \
		-e CDK_DEFAULT_REGION=us-east-1 \
		-e AWS_ENDPOINT_URL=http://ministack:4566 \
		deployer -c 'cdk bootstrap aws://000000000000/us-east-1'
	@echo "Deploying lambdas and API Gateway with CDK..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ACCESS_KEY_ID=local \
		-e AWS_SECRET_ACCESS_KEY=local \
		-e AWS_DEFAULT_REGION=us-east-1 \
		-e CDK_DEFAULT_ACCOUNT=000000000000 \
		-e CDK_DEFAULT_REGION=us-east-1 \
		-e AWS_ENDPOINT_URL=http://ministack:4566 \
		deployer -c 'cdk deploy --all --require-approval never'
	@echo "✓ Deployment complete"

create-table:
	@echo "Creating DynamoDB tables..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ENDPOINT=http://ministack:4566 \
		-e AWS_REGION=us-east-1 \
		deployer -c 'python scripts/create_table.py'
	@echo "✓ Tables created"

seed:
	@echo "Seeding initial data..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ENDPOINT=http://ministack:4566 \
		-e AWS_REGION=us-east-1 \
		deployer -c 'python scripts/seed_data.py'
	@echo "✓ Data seeded"

test-api:
	@echo "Testing API Gateway..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ENDPOINT=http://ministack:4566 \
		-e AWS_REGION=us-east-1 \
		deployer -c 'sh scripts/test_api_gateway.sh'

validate:
	@echo "Validating Frontend→Lambda→DynamoDB connection..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ENDPOINT=http://ministack:4566 \
		-e AWS_REGION=us-east-1 \
		-e DYNAMODB_ENDPOINT=http://dynamodb-local:8000 \
		deployer -c 'sh scripts/validate_connection.sh'

logs-frontend:
	@echo "Frontend logs (press Ctrl+C to exit):"
	@sudo docker compose logs -f frontend

logs-ministack:
	@echo "Ministack logs (press Ctrl+C to exit):"
	@sudo docker compose logs -f ministack

clean:
	@echo "Removing containers and volumes..."
	@sudo docker compose down -v
	@echo "✓ Cleanup complete"
