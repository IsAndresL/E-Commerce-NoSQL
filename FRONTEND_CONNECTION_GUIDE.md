# Guía: Conectar Frontend con Lambda + API Gateway

## Arquitectura de Conexión

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND (React + Vite)                                │
│  http://localhost:5173                                  │
│                                                         │
│  ┌────────────────────────────────────────────┐        │
│  │  App.jsx (useDashboardData hook)           │        │
│  │  ↓                                          │        │
│  │  ecommerceApi.js (fetch calls)             │        │
│  │  ↓                                          │        │
│  │  /ecommerce/user/{user_id}/profile         │        │
│  │  /ecommerce/user/{user_id}/orders          │        │
│  │  /ecommerce/dashboard-data?...             │        │
│  └────────────────────────────────────────────┘        │
│                          ↓ (HTTP proxy)                 │
└─────────────────────────────────────────────────────────┘
                           │
                    vite.config.js
                    VITE_API_PROXY_TARGET=
                    http://ministack:4566
                           │
    ┌──────────────────────────────────────────┐
    │  docker-compose.yml network: ecommerce-net
    │                                          │
    │  ┌────────────────────────────────────┐ │
    │  │  ministack service (LocalStack)    │ │
    │  │  Port: 4566                        │ │
    │  │                                    │ │
    │  │  ┌──────────────────────────────┐ │ │
    │  │  │ HTTP API Gateway             │ │ │
    │  │  │ Routes (from CDK):           │ │ │
    │  │  │ GET /ecommerce/user/{uid}/..│ │ │
    │  │  │ GET /ecommerce/dashboard-... │ │ │
    │  │  │ GET /products                │ │ │
    │  │  └──────────────────────────────┘ │ │
    │  │              ↓                     │ │
    │  │  ┌──────────────────────────────┐ │ │
    │  │  │ Lambda Functions             │ │ │
    │  │  │ • ecommerce (multi-handler)  │ │ │
    │  │  │ • products (list_products)   │ │ │
    │  │  └──────────────────────────────┘ │ │
    │  │              ↓                     │ │
    │  │  ┌──────────────────────────────┐ │ │
    │  │  │ DynamoDB Table               │ │ │
    │  │  │ ecommerce (PK: user_id#...)  │ │ │
    │  │  └──────────────────────────────┘ │ │
    │  └────────────────────────────────────┘ │
    │                                          │
    └──────────────────────────────────────────┘
```

## Flujo de Conexión Paso a Paso

### 1. **Frontend hace request HTTP**

El frontend (React) hace un fetch a una ruta `/ecommerce/...`:

```javascript
// frontend/src/api/ecommerceApi.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export function getUserProfile(userId, signal) {
  return fetchJson(
    `${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/profile`,
    signal
  )
}
```

**Ejemplo:** `fetch('/ecommerce/user/123/profile')`

### 2. **Vite Dev Server proxea a ministack**

El `vite.config.js` intercepta las requests a `/ecommerce`:

```javascript
// frontend/vite.config.js
server: {
  proxy: {
    '/ecommerce': {
      target: env.VITE_API_PROXY_TARGET,  // = http://ministack:4566
      changeOrigin: true,
    }
  }
}
```

**Ejemplo:** 
- Request: `GET http://localhost:5173/ecommerce/user/123/profile`
- Proxeado a: `GET http://ministack:4566/ecommerce/user/123/profile`

### 3. **LocalStack HTTP API Gateway recibe la request**

LocalStack tiene un **HTTP API Gateway** creado por CDK que tiene las siguientes rutas definidas:

```python
# infra/api_stack.py
handlers = {
    "/ecommerce/user/{user_id}/profile": "get_user_profile",
    "/ecommerce/user/{user_id}/orders": "get_recent_orders",
    "/ecommerce/user/{user_id}/order/{order_id}/details": "get_user_order_details",
    "/ecommerce/user/{user_id}/order/{order_id}/items": "get_user_order_items",
    "/ecommerce/order/{order_id}/details": "get_order_details",
    "/ecommerce/order/{order_id}/items": "get_order_items",
    "/ecommerce/dashboard-data": "dashboard_data",
    "/products": "list_products",
}
```

### 4. **CDK crea rutas HTTP API**

El CDK despliega estas rutas como **HTTP API Gateway routes** que apuntan a los lambdas:

```python
for path, fn in lambda_map.items():
    integration = integrations.HttpLambdaIntegration(...)
    http_api.add_routes(path=path, methods=[apigwv2.HttpMethod.GET], integration=integration)
```

### 5. **Lambda ejecuta la lógica de negocio**

La ruta `/ecommerce/user/{user_id}/profile` invoca el lambda `ecommerce` con handler `get_user_profile.lambda_handler`:

```python
# lambdas/ecommerce/get_user_profile.py
def lambda_handler(event, context):
    # event contiene: path, queryStringParameters, headers, body, etc.
    user_id = event['pathParameters']['user_id']
    # ... buscar en DynamoDB
    return {
        'statusCode': 200,
        'body': json.dumps(user_profile_data)
    }
```

### 6. **Lambda accede a DynamoDB**

El lambda está configurado por CDK para tener permisos IAM sobre la tabla DynamoDB:

```python
# infra/api_stack.py
if persistence_table:
    persistence_table.grant_read_write_data(fn)  # Lambda puede leer/escribir
```

El lambda usa boto3 con la variable de entorno `TABLE_NAME`:

```python
# lambdas/ecommerce/get_user_profile.py
import boto3
import os

dynamodb = boto3.resource('dynamodb', endpoint_url=os.getenv('AWS_ENDPOINT_URL'))
table = dynamodb.Table(os.getenv('TABLE_NAME', 'ecommerce'))
```

### 7. **Response vuelve al frontend**

La response del lambda vuelve a través de API Gateway:

```json
{
  "statusCode": 200,
  "body": "{\"user_id\": \"123\", \"name\": \"John\", ...}"
}
```

El frontend parsea el JSON y renderiza los datos.

## Configuración Necesaria

### Paso 1: Environment Variables en Docker Compose

```yaml
# docker-compose.yml
frontend:
  environment:
    VITE_API_PROXY_TARGET: http://ministack:4566  # ← IMPORTANTE
```

Este env var se lee en `vite.config.js`:

```javascript
const target = env.VITE_API_PROXY_TARGET || 'http://localhost:8000'
```

### Paso 2: Desplegar CDK

El CDK **debe** ejecutarse para crear el HTTP API Gateway con todas las rutas:

```bash
make deploy
# o manualmente:
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://ministack:4566 \
  sh -c 'cd infra && cdk deploy --require-approval never'
```

Esto:
- Crea todos los lambdas (ecommerce, products)
- Crea el HTTP API Gateway con todas las rutas
- Asigna permisos IAM a los lambdas para acceder a DynamoDB

### Paso 3: Crear tablas DynamoDB

```bash
make create-table
# o manualmente:
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://ministack:4566 \
  python scripts/create_table.py
```

### Paso 4: Cargar datos

```bash
make seed
# o manualmente:
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://ministack:4566 \
  python scripts/seed_data.py
```

### Paso 5: Iniciar frontend

```bash
sudo docker compose up -d frontend
# Accede a: http://localhost:5173
```

## Variables de Entorno Importantes

| Variable | Ubicación | Valor | Propósito |
|----------|-----------|-------|----------|
| `VITE_API_PROXY_TARGET` | `docker-compose.yml` (frontend) | `http://ministack:4566` | Le dice a Vite dónde proxear las requests de `/ecommerce` |
| `VITE_API_BASE_URL` | `docker-compose.yml` (frontend) | (vacío, usa root) | Base URL para fetch requests en el frontend |
| `AWS_ENDPOINT` | `docker compose run -e` | `http://ministack:4566` | Le dice a boto3 y awscli dónde está LocalStack |
| `AWS_REGION` | `docker compose run -e` | `us-east-1` | Región AWS (local) |
| `TABLE_NAME` | Env var del lambda (en CDK) | `ecommerce` | Nombre de la tabla DynamoDB |
| `AWS_ENDPOINT_URL` | Env var del lambda | `http://dynamodb-local:8000` | Para que el lambda acceda a DynamoDB |

## Rutas Disponibles

Una vez que el CDK está deployado y las tablas existen, estas rutas están disponibles en `http://localhost:4566`:

### E-Commerce (Multi-handler)
```
GET /ecommerce/user/{user_id}/profile
GET /ecommerce/user/{user_id}/orders
GET /ecommerce/user/{user_id}/order/{order_id}/details
GET /ecommerce/user/{user_id}/order/{order_id}/items
GET /ecommerce/order/{order_id}/details
GET /ecommerce/order/{order_id}/items
GET /ecommerce/dashboard-data?user_id=123&order_id=555
```

### Productos
```
GET /products
```

## Testing desde el Frontend

### URL de prueba
```
http://localhost:5173/?user_id=1&order_id=555
```

El frontend leerá estos query parameters y hará fetch a las APIs correspondientes.

### Browser DevTools

1. Abre `http://localhost:5173` en el navegador
2. Abre DevTools (F12)
3. Ve a la pestaña **Network**
4. Verás requests a `http://localhost:5173/ecommerce/...` que se proxean a `http://ministack:4566/ecommerce/...`
5. Verifica que los status sean 200 y los responses contén los datos esperados

## Troubleshooting

### ❌ "Cannot GET /ecommerce/user/123/profile" (404)

**Causa:** El CDK no fue deployado o el HTTP API Gateway no existe.

**Solución:**
```bash
make deploy
```

### ❌ "timeout de conexión" o "ECONNREFUSED"

**Causa:** ministack no está corriendo o no está listo.

**Solución:**
```bash
make up
sleep 5  # Espera a que ministack sea ready
make deploy
```

### ❌ Frontend hace requests a `localhost:8000` en lugar de `ministack:4566`

**Causa:** `VITE_API_PROXY_TARGET` no está configurado correctamente en docker-compose.yml

**Verificar:**
```bash
sudo docker compose exec frontend sh -c 'env | grep VITE'
```

Debe mostrar:
```
VITE_API_PROXY_TARGET=http://ministack:4566
```

### ❌ Lambda no puede acceder a DynamoDB

**Causa:** La tabla no existe o el lambda no tiene permisos.

**Soluciones:**
```bash
# 1. Crear la tabla
make create-table

# 2. Verificar que la tabla existe
sudo docker compose run deployer \
  aws --endpoint-url http://dynamodb-local:8000 dynamodb list-tables

# 3. Verificar que el lambda tiene permisos en el CDK
```

## Resumen del Flujo Completo

```
1. Frontend (React) hace fetch('/ecommerce/user/123/profile')
   ↓
2. Vite proxy intercepta y redirige a http://ministack:4566/ecommerce/user/123/profile
   ↓
3. LocalStack HTTP API Gateway recibe la request
   ↓
4. API Gateway routing encuentra la ruta /ecommerce/user/{user_id}/profile
   ↓
5. API Gateway invoca el lambda 'ecommerce' con el handler 'get_user_profile'
   ↓
6. Lambda ecommerce ejecuta get_user_profile.lambda_handler(event, context)
   ↓
7. Lambda hace query a DynamoDB usando boto3
   ↓
8. Lambda retorna el resultado como JSON
   ↓
9. Response vuelve a través de API Gateway
   ↓
10. Frontend recibe la response y renderiza los datos en React
```

Para más información sobre CDK, ver [infra/README.md](../infra/README.md)
