#!/bin/bash

# Test API Gateway connectivity and routes

AWS_ENDPOINT="${AWS_ENDPOINT:-http://ministack:4566}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "=== Testing LocalStack Connectivity ==="
echo "Endpoint: $AWS_ENDPOINT"
echo ""

echo "1. Testing Lambda API (list-functions):"
aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" lambda list-functions

echo ""
echo "2. Testing HTTP APIs:"
aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" apigatewayv2 get-apis

echo ""
echo "3. Testing HTTP API Routes:"
# Get the first API ID
API_ID=$(aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" apigatewayv2 get-apis --query 'Items[0].ApiId' --output text 2>/dev/null)

if [ "$API_ID" != "None" ] && [ -n "$API_ID" ]; then
    echo "Found API: $API_ID"
    aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" apigatewayv2 get-routes --api-id "$API_ID"
    
    echo ""
    echo "4. Testing direct lambda invocation (ecommerce handler):"
    aws --endpoint-url "$AWS_ENDPOINT" --region "$AWS_REGION" lambda invoke \
        --function-name ecommerce \
        --payload '{"httpMethod": "GET", "path": "/ecommerce/user/test-user/profile", "headers": {}, "body": null}' \
        --log-type Tail \
        /tmp/lambda_response.json
    
    echo "Response:"
    cat /tmp/lambda_response.json
else
    echo "No HTTP APIs found. You may need to run: docker compose run --rm deployer cdk synth && cdk deploy"
fi
