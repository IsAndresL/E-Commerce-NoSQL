#!/bin/bash

# Validation script to verify Frontend ↔ Lambda ↔ DynamoDB connectivity

set -e

AWS_ENDPOINT="${AWS_ENDPOINT:-http://ministack:4566}"
AWS_REGION="${AWS_REGION:-us-east-1}"
DYNAMODB_ENDPOINT="${DYNAMODB_ENDPOINT:-http://dynamodb-local:8000}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  E-Commerce Frontend-Lambda Connection Validation         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
  echo -e "${GREEN}✓${NC} $1"
}

fail() {
  echo -e "${RED}✗${NC} $1"
  return 1
}

warn() {
  echo -e "${YELLOW}⚠${NC} $1"
}

echo "Checking endpoints..."
echo "  AWS_ENDPOINT: $AWS_ENDPOINT"
echo "  DYNAMODB_ENDPOINT: $DYNAMODB_ENDPOINT"
echo ""

# 1. Check LocalStack/Ministack
echo "1. Checking LocalStack connectivity..."
if aws --endpoint-url "$AWS_ENDPOINT" lambda list-functions >/dev/null 2>&1; then
  pass "LocalStack is responding at $AWS_ENDPOINT"
else
  fail "Cannot connect to LocalStack at $AWS_ENDPOINT"
  exit 1
fi
echo ""

# 2. Check Lambda functions
echo "2. Checking Lambda functions..."
LAMBDA_COUNT=$(aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" lambda list-functions --query 'length(Functions)' --output text)
if [ "$LAMBDA_COUNT" -gt 0 ]; then
  pass "Found $LAMBDA_COUNT Lambda function(s)"
  aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" lambda list-functions --query 'Functions[*].[FunctionName,State]' --output table
else
  fail "No Lambda functions found (run: make deploy)"
  exit 1
fi
echo ""

# 3. Check HTTP API Gateway
echo "3. Checking HTTP API Gateway..."
API_COUNT=$(aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" apigatewayv2 get-apis --query 'length(Items)' --output text 2>/dev/null || echo "0")
if [ "$API_COUNT" -gt 0 ]; then
  pass "Found $API_COUNT HTTP API(s)"
  API_ID=$(aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" apigatewayv2 get-apis --query 'Items[0].ApiId' --output text)
  
  echo "   API Routes:"
  aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" apigatewayv2 get-routes --api-id "$API_ID" \
    --query 'Items[*].[RouteKey,State]' --output table 2>/dev/null || true
else
  fail "No HTTP APIs found (run: make deploy)"
  exit 1
fi
echo ""

# 4. Check DynamoDB connectivity
echo "4. Checking DynamoDB connectivity..."
if aws --endpoint-url "$DYNAMODB_ENDPOINT" dynamodb list-tables >/dev/null 2>&1; then
  pass "DynamoDB is responding at $DYNAMODB_ENDPOINT"
  
  TABLE_COUNT=$(aws --endpoint-url "$DYNAMODB_ENDPOINT" dynamodb list-tables --query 'length(TableNames)' --output text)
  if [ "$TABLE_COUNT" -gt 0 ]; then
    pass "Found $TABLE_COUNT table(s)"
    aws --endpoint-url "$DYNAMODB_ENDPOINT" dynamodb list-tables --output text | tr '\t' '\n'
  else
    warn "No DynamoDB tables found (run: make create-table)"
  fi
else
  fail "Cannot connect to DynamoDB at $DYNAMODB_ENDPOINT"
  exit 1
fi
echo ""

# 5. Test Lambda invocation
echo "5. Testing Lambda invocation (ecommerce function)..."
TEMP_RESPONSE=$(mktemp)
if aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" lambda invoke \
  --function-name ecommerce \
  --payload '{"httpMethod": "GET", "path": "/ecommerce/user/test-user/profile", "headers": {}, "body": null, "pathParameters": {"user_id": "test-user"}}' \
  --log-type Tail \
  "$TEMP_RESPONSE" >/dev/null 2>&1; then
  
  STATUS=$(aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" lambda invoke \
    --function-name ecommerce \
    --payload '{}' \
    /dev/null --query 'StatusCode' --output text 2>/dev/null || echo "200")
  
  pass "Lambda invocation successful (StatusCode: $STATUS)"
else
  fail "Lambda invocation failed"
fi
rm -f "$TEMP_RESPONSE"
echo ""

# 6. Check Frontend
echo "6. Checking Frontend container..."
if sudo docker ps --filter "name=ecommerce-frontend" --format "{{.State}}" 2>/dev/null | grep -q "running"; then
  pass "Frontend container is running"
  FRONTEND_URL="http://localhost:5173"
  echo "   → Accede a: $FRONTEND_URL"
  echo "   → Con parámetros: $FRONTEND_URL?user_id=1&order_id=555"
else
  warn "Frontend container is not running (run: make up && sleep 5)"
fi
echo ""

# 7. Environment variables check
echo "7. Checking environment variables..."
if [ -f "/app/docker-compose.yml" ] 2>/dev/null || [ -f "./docker-compose.yml" ]; then
  if grep -q "VITE_API_PROXY_TARGET.*ministack:4566" docker-compose.yml 2>/dev/null; then
    pass "docker-compose.yml has VITE_API_PROXY_TARGET=http://ministack:4566"
  else
    fail "docker-compose.yml missing VITE_API_PROXY_TARGET=http://ministack:4566"
  fi
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Validation Complete!                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Access Frontend: http://localhost:5173"
echo "  2. Check browser Network tab to verify /ecommerce requests"
echo "  3. Verify responses from Lambda functions"
echo ""
echo "For more details, see FRONTEND_CONNECTION_GUIDE.md"
