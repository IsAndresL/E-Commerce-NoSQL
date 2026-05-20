.PHONY: help up down deploy create-table seed test-api validate logs-frontend logs-ministack clean

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

deploy:
	@echo "Building deployer image..."
	@sudo docker compose build deployer
	@echo "Deploying lambdas and API Gateway with CDK..."
	@sudo docker compose run --rm --entrypoint /bin/sh \
		-e AWS_ENDPOINT=http://ministack:4566 \
		-e AWS_REGION=us-east-1 \
		deployer -c 'cdk deploy --require-approval never'
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
