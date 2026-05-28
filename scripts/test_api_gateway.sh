#!/bin/bash
set -eu

AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://ministack:4566}"
AWS_REGION="${AWS_REGION:-us-east-1}"
USER_ID="${TEST_USER_ID:-1}"
ORDER_ID="${TEST_ORDER_ID:-555}"

PASS=0
FAIL=0

green()  { echo -e "\033[32m$*\033[0m"; }
red()    { echo -e "\033[31m$*\033[0m"; }
yellow() { echo -e "\033[33m$*\033[0m"; }

check() {
    local label="$1" result="$2"
    if [ "$result" = "ok" ]; then
        green "  ✓ $label"; PASS=$((PASS + 1))
    else
        red "  ✗ $label — $result"; FAIL=$((FAIL + 1))
    fi
}

aws_cmd() { python3 -m awscli --endpoint-url "$AWS_ENDPOINT_URL" --region "$AWS_REGION" "$@"; }

invoke_lambda() {
    local fn="$1" payload="$2" out="/tmp/lr_$$.json"
    aws_cmd lambda invoke --function-name "$fn" --payload "$payload" --log-type None "$out" > /dev/null 2>&1
    cat "$out"; rm -f "$out"
}

parse_status() {
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('statusCode','error'))" 2>/dev/null || echo "error"
}

parse_body() {
    python3 -c "import sys,json; d=json.load(sys.stdin); print(str(d.get('body',''))[:300])" 2>/dev/null || echo ""
}

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║     API Gateway & Lambda Test Suite        ║"
echo "╚════════════════════════════════════════════╝"
echo "  Endpoint : $AWS_ENDPOINT_URL"
echo "  Region   : $AWS_REGION"
echo "  User ID  : $USER_ID  |  Order ID: $ORDER_ID"
echo ""

# ── 1. Ministack ──────────────────────────────────────────────────────────────
echo "── 1. Ministack connectivity ────────────────"
if aws_cmd lambda list-functions > /dev/null 2>&1; then
    check "Ministack responde" "ok"
else
    check "Ministack responde" "no responde"
    red "Abortando"; exit 1
fi

# ── 2. Lambdas ────────────────────────────────────────────────────────────────
echo ""; echo "── 2. Lambda functions ──────────────────────"
FN_COUNT=$(aws_cmd lambda list-functions --query 'length(Functions)' --output text 2>/dev/null || echo "0")
check "Funciones desplegadas ($FN_COUNT)" "$([ "$FN_COUNT" -gt 0 ] && echo ok || echo 'ninguna')"
aws_cmd lambda list-functions --query 'Functions[*].[FunctionName,State]' --output table 2>/dev/null || true

# ── 3. API Gateway ────────────────────────────────────────────────────────────
echo ""; echo "── 3. HTTP API Gateway ──────────────────────"
API_ID=$(aws_cmd apigatewayv2 get-apis \
    --query "Items[?Name=='EcommerceHttpApi'] | sort_by(@, &CreatedDate)[-1].ApiId" --output text 2>/dev/null || echo "")
check "EcommerceHttpApi existe" "$([ -n "$API_ID" ] && [ "$API_ID" != "None" ] && echo ok || echo 'no encontrada')"
if [ -n "$API_ID" ] && [ "$API_ID" != "None" ]; then
    yellow "  API ID: $API_ID"
    ROUTE_COUNT=$(aws_cmd apigatewayv2 get-routes --api-id "$API_ID" \
        --query 'length(Items)' --output text 2>/dev/null || echo "0")
    check "Rutas registradas ($ROUTE_COUNT)" "$([ "$ROUTE_COUNT" -gt 0 ] && echo ok || echo 'sin rutas')"
    aws_cmd apigatewayv2 get-routes --api-id "$API_ID" \
        --query 'Items[*].[RouteKey]' --output table 2>/dev/null || true
fi

# ── 4. DynamoDB ───────────────────────────────────────────────────────────────
echo ""; echo "── 4. DynamoDB ──────────────────────────────"
TABLE=$(aws_cmd cloudformation describe-stacks \
    --stack-name EcommercePersistence \
    --query "Stacks[0].Outputs[?OutputKey=='TableName'].OutputValue | [0]" \
    --output text 2>/dev/null || echo "")
check "Tabla CDK existe" "$([ -n "$TABLE" ] && [ "$TABLE" != "None" ] && echo ok || echo 'no encontrada')"
if [ -n "$TABLE" ] && [ "$TABLE" != "None" ]; then
    yellow "  Tabla: $TABLE"
    ITEM_COUNT=$(aws_cmd dynamodb scan --table-name "$TABLE" \
        --select COUNT --query 'Count' --output text 2>/dev/null || echo "0")
    check "Items en tabla ($ITEM_COUNT)" "$([ "$ITEM_COUNT" -gt 0 ] && echo ok || echo 'vacía — ejecuta make seed')"
    PROD_COUNT=$(aws_cmd dynamodb scan --table-name "$TABLE" \
        --filter-expression "begins_with(PK, :pk)" \
        --expression-attribute-values '{":pk":{"S":"PRODUCT#"}}' \
        --select COUNT --query 'Count' --output text 2>/dev/null || echo "0")
    check "Productos en tabla ($PROD_COUNT)" "$([ "$PROD_COUNT" -gt 0 ] && echo ok || echo 'sin productos — ejecuta make seed')"
fi

# ── 5. Dependencias Lambda ────────────────────────────────────────────────────
echo ""; echo "── 5. Lambda dependencies ───────────────────"
PROFILE_FN=$(aws_cmd lambda list-functions \
    --query "Functions[?contains(FunctionName, 'getuserprofile')] | sort_by(@, &LastModified)[-1].FunctionName" \
    --output text 2>/dev/null || echo "")

if [ -n "$PROFILE_FN" ] && [ "$PROFILE_FN" != "None" ]; then
    yellow "  Verificando dependencias en: $PROFILE_FN"
    # Invoca con payload mínimo para detectar errores de import
    RESP=$(invoke_lambda "$PROFILE_FN" \
        '{"pathParameters":{"user_id":"__check__"},"queryStringParameters":null,"body":null}')
    BODY=$(echo "$RESP" | parse_body)

    if echo "$BODY" | grep -q "No module named"; then
        MODULE=$(echo "$BODY" | grep -o "No module named '[^']*'" | head -1)
        check "Dependencias Python" "FALTA $MODULE"
        echo ""
        red "  ══ FIX: ejecuta estos comandos ══"
        yellow "  1. sudo docker compose exec devcontainer \\"
        yellow "       pip install -r requirements.txt --break-system-packages"
        yellow "  2. make deploy"
        echo ""
    elif echo "$BODY" | grep -q "Worker init failed"; then
        ERR=$(echo "$BODY" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('errorMessage',''))" 2>/dev/null || echo "$BODY")
        check "Dependencias Python" "Worker init failed: $ERR"
    else
        check "Dependencias Python" "ok"
    fi
fi

# ── 6. Invocación Lambda ──────────────────────────────────────────────────────
echo ""; echo "── 6. Lambda invocation ─────────────────────"

if [ -n "$PROFILE_FN" ] && [ "$PROFILE_FN" != "None" ]; then
    yellow "  $PROFILE_FN"
    RESP=$(invoke_lambda "$PROFILE_FN" \
        "{\"pathParameters\":{\"user_id\":\"$USER_ID\"},\"queryStringParameters\":null,\"body\":null}")
    STATUS=$(echo "$RESP" | parse_status)
    check "get_user_profile (user $USER_ID) → HTTP $STATUS" \
        "$([ "$STATUS" = "200" ] && echo ok || echo "statusCode=$STATUS")"
    [ "$STATUS" != "200" ] && yellow "  Body: $(echo "$RESP" | parse_body)"
fi

DASH_FN=$(aws_cmd lambda list-functions \
    --query "Functions[?contains(FunctionName, 'dashboard')] | sort_by(@, &LastModified)[-1].FunctionName" \
    --output text 2>/dev/null || echo "")
if [ -n "$DASH_FN" ] && [ "$DASH_FN" != "None" ]; then
    yellow "  $DASH_FN"
    RESP=$(invoke_lambda "$DASH_FN" \
        "{\"pathParameters\":null,\"queryStringParameters\":{\"user_id\":\"$USER_ID\",\"order_id\":\"$ORDER_ID\"},\"body\":null}")
    STATUS=$(echo "$RESP" | parse_status)
    check "dashboard_data (user $USER_ID, order $ORDER_ID) → HTTP $STATUS" \
        "$([ "$STATUS" = "200" ] && echo ok || echo "statusCode=$STATUS")"
    [ "$STATUS" != "200" ] && yellow "  Body: $(echo "$RESP" | parse_body)"
fi

PROD_FN=$(aws_cmd lambda list-functions \
    --query "Functions[?contains(FunctionName, 'Products')] | sort_by(@, &LastModified)[-1].FunctionName" \
    --output text 2>/dev/null || echo "")
if [ -n "$PROD_FN" ] && [ "$PROD_FN" != "None" ]; then
    yellow "  $PROD_FN"
    RESP=$(invoke_lambda "$PROD_FN" \
        '{"pathParameters":null,"queryStringParameters":null,"body":null}')
    STATUS=$(echo "$RESP" | parse_status)
    check "list_products → HTTP $STATUS" \
        "$([ "$STATUS" = "200" ] && echo ok || echo "statusCode=$STATUS")"
    [ "$STATUS" != "200" ] && yellow "  Body: $(echo "$RESP" | parse_body)"
fi

# ── Resumen ───────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════"
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
    green "  ✓ Todos los checks pasaron ($PASS/$TOTAL)"
else
    yellow "  Resultado: $PASS/$TOTAL pasaron"
    red "  $FAIL checks fallaron"
fi
echo "════════════════════════════════════════════"
echo ""
exit $FAIL
