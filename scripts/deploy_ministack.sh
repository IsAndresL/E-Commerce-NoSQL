#!/bin/sh
set -eu

# Example: deploy lambdas to a local ministack/localstack running at localhost:4566
# Assumes ministack/localstack is running (see docker-compose.yml service 'ministack')

AWS_ENDPOINT="${AWS_ENDPOINT:-http://ministack:4566}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Wait for LocalStack/Ministack to be ready at the endpoint before proceeding
wait_for_endpoint() {
  echo "Waiting for LocalStack at $AWS_ENDPOINT ..."
  tries=0
  max=30
  until aws --endpoint-url "$AWS_ENDPOINT" lambda list-functions >/dev/null 2>&1; do
    tries=$((tries + 1))
    if [ "$tries" -ge "$max" ]; then
      echo "Timed out waiting for LocalStack at $AWS_ENDPOINT" >&2
      return 1
    fi
    sleep 2
  done
  echo "LocalStack responded after $tries attempts."
}

if ! wait_for_endpoint; then
  echo "LocalStack not available at $AWS_ENDPOINT, aborting." >&2
  exit 2
fi

echo "Deploying infrastructure with CDK (creates lambdas + API Gateway HTTP routes)..."
# CDK must be run from project root where cdk.json is located
cdk deploy --require-approval never

echo ""
echo "=== Deployment Complete ==="
echo "HTTP API Gateway endpoint: $AWS_ENDPOINT"
echo "Available routes:"
echo "  GET /ecommerce/user/{user_id}/profile"
echo "  GET /ecommerce/user/{user_id}/orders"
echo "  GET /ecommerce/user/{user_id}/order/{order_id}/details"
echo "  GET /ecommerce/user/{user_id}/order/{order_id}/items"
echo "  GET /ecommerce/order/{order_id}/details"
echo "  GET /ecommerce/order/{order_id}/items"
echo "  GET /ecommerce/dashboard-data?user_id=...&order_id=..."
echo "  GET /products"
echo ""
echo "Next step: Run 'python scripts/create_table.py' to create DynamoDB tables"
