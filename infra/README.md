# AWS CDK Infrastructure (Lambda + API Gateway)

Este directorio contiene la definición de infraestructura como código usando **AWS CDK** para desplegar:
- Lambda functions (ecommerce, products)
- HTTP API Gateway con routing
- DynamoDB table
- Roles y permisos IAM

## Estructura

```
infra/
├── app.py                 # CDK App - orquestador principal
├── api_stack.py          # ApiStack - Lambdas + HTTP API Gateway
├── persistence_stack.py  # PersistenceStack - DynamoDB
├── core_stack.py         # CoreStack - Configuración base
├── cdk.json             # Configuración CDK (context, outdir, etc.)
└── README.md            # Este archivo
```

## Archivos Principales

### `app.py` - Punto de entrada

```python
from infra.api_stack import ApiStack
from infra.core_stack import CoreStack
from infra.persistence_stack import PersistenceStack

app = App()

core = CoreStack(app, "EcommerceCore")
persistence = PersistenceStack(app, "EcommercePersistence")
api = ApiStack(app, "EcommerceApi", persistence_table=persistence.table)

app.synth()
```

**Qué hace:**
1. Crea el stack Core (configuración base)
2. Crea el stack de Persistence (DynamoDB)
3. Crea el stack API (Lambdas + API Gateway) pasándole la tabla DynamoDB
4. Sintetiza el CloudFormation template

### `api_stack.py` - Lambdas y HTTP API Gateway

```python
class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, persistence_table=None, **kwargs):
        # Define handler paths y módulos
        handlers = {
            "/ecommerce/user/{user_id}/profile": "get_user_profile",
            "/ecommerce/user/{user_id}/orders": "get_recent_orders",
            # ... más rutas
        }
        
        # Para cada ruta, crea un Lambda
        for path, module in handlers.items():
            fn = _lambda.Function(...)
            persistence_table.grant_read_write_data(fn)  # Permisos IAM
            lambda_map[path] = fn
        
        # Crea HTTP API Gateway
        http_api = apigwv2.HttpApi(...)
        
        # Para cada Lambda, crea una ruta
        for path, fn in lambda_map.items():
            integration = integrations.HttpLambdaIntegration(...)
            http_api.add_routes(path=path, methods=[HttpMethod.GET], integration=integration)
```

**Qué hace:**
1. Define todas las rutas HTTP (`/ecommerce/user/{user_id}/profile`, etc.)
2. Crea un Lambda para cada ruta
3. Asigna permisos IAM a los Lambdas para leer/escribir en DynamoDB
4. Crea un HTTP API Gateway
5. Mapea cada ruta HTTP a su respectivo Lambda
6. Expone el API en LocalStack puerto 4566

### `persistence_stack.py` - DynamoDB

```python
class PersistenceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        self.table = _dynamodb.Table(
            self, "EcommerceTable",
            table_name="ecommerce",
            partition_key=_dynamodb.Attribute(name="user_id", type=_dynamodb.AttributeType.STRING),
            sort_key=_dynamodb.Attribute(name="sort_key", type=_dynamodb.AttributeType.STRING),
            # ...
        )
```

**Qué hace:**
1. Define la tabla DynamoDB `ecommerce`
2. Configura la partition key (`user_id`) y sort key (`sort_key`)
3. Retorna la tabla para que otros stacks puedan usarla

### `core_stack.py` - Configuración base

Placeholder para configuración global (VPCs, roles base, etc.).

### `cdk.json` - Configuración del sintetizador

```json
{
  "app": "python app.py",
  "context": {}
}
```

Define cómo CDK debe ejecutar el app y opciones de contexto.

## Cómo funciona LocalStack + CDK

### Diagrama

```
┌──────────────────────┐
│   cdk deploy         │
│   --require-approval │
│   never              │
└──────────┬───────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  CDK Synthesis → CloudFormation        │
│  (cdk.json apunta a LocalStack)        │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  CloudFormation API                    │
│  (endpoint: http://ministack:4566)     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  LocalStack / Ministack                │
│  - Lambda: creates functions           │
│  - ApiGatewayV2: creates HTTP API      │
│  - DynamoDB: creates tables            │
│  - IAM: creates roles                  │
└─────────────────────────────────────────┘
```

### Flujo de deployment

1. **`cdk deploy`** se ejecuta dentro del contenedor `deployer`
2. Sabe que `AWS_ENDPOINT=http://ministack:4566` (en docker-compose.yml)
3. CDK sintetiza el CloudFormation template
4. Envía el template a LocalStack (port 4566)
5. LocalStack crea:
   - Lambda functions (ecommerce, products)
   - HTTP API Gateway con todas las rutas
   - DynamoDB table
   - IAM roles con permisos

## Variables de Entorno

Cuando se ejecuta `cdk deploy` dentro del contenedor `deployer`:

```bash
AWS_ENDPOINT=http://ministack:4566      # Dónde está LocalStack
AWS_REGION=us-east-1                    # Región (local)
AWS_ACCESS_KEY_ID=local                 # Credenciales fake para LocalStack
AWS_SECRET_ACCESS_KEY=local
```

Estas variables hace que boto3 (que usa CDK internamente) apunte a LocalStack en lugar de AWS real.

## Flujo HTTP API Gateway en LocalStack

Cuando haces una request al frontend:

```
1. Frontend: fetch('/ecommerce/user/123/profile')
2. Vite proxy: GET http://ministack:4566/ecommerce/user/123/profile
3. LocalStack HTTP API Gateway recibe la request
4. Busca la ruta /ecommerce/user/{user_id}/profile
5. Encuentra el Lambda handler: lambdas.ecommerce.get_user_profile.lambda_handler
6. Invoca el Lambda con event = {
     path: '/ecommerce/user/123/profile',
     pathParameters: { user_id: '123' },
     httpMethod: 'GET',
     ...
   }
7. Lambda retorna { statusCode: 200, body: JSON.stringify(...) }
8. API Gateway devuelve la response al frontend
```

## Cómo modificar las rutas

Para agregar una nueva ruta HTTP que invoque un Lambda:

### Paso 1: Crear el handler

```python
# lambdas/ecommerce/new_handler.py
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Hello'})
    }
```

### Paso 2: Agregar a api_stack.py

```python
handlers = {
    # ... existing routes
    "/ecommerce/new-endpoint": "new_handler",
}
```

### Paso 3: Redeploy

```bash
make deploy
# o
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://ministack:4566 \
  sh -c 'cd infra && cdk deploy --require-approval never'
```

## Modificar permisos IAM

Las Lambdas necesitan permisos para acceder a recursos (DynamoDB, S3, etc.).

```python
# En api_stack.py, para cada Lambda:
persistence_table.grant_read_write_data(fn)  # Permite leer y escribir en DynamoDB
```

Opciones comunes:
- `grant_read_data(fn)` - Solo lectura
- `grant_write_data(fn)` - Solo escritura
- `grant_read_write_data(fn)` - Leer y escribir
- `grant_full_access(fn)` - Acceso completo

## Variables de Entorno en Lambdas

El CDK configura variables de entorno para cada Lambda:

```python
fn = _lambda.Function(
    ...,
    environment={
        "TABLE_NAME": persistence_table.table_name,
        "AWS_ENDPOINT_URL": os.getenv("AWS_ENDPOINT_URL"),
        # ...
    }
)
```

Los Lambdas pueden acceder a estas variables:

```python
import os

table_name = os.getenv('TABLE_NAME', 'ecommerce')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
```

## Debugging

### Ver el CloudFormation template sintetizado

```bash
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://ministack:4566 \
  sh -c 'cd infra && cdk synth'
```

Genera un archivo `cdk.out/EcommerceApi.json` con el template.

### Ver recursos creados

```bash
# Lambda functions
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda list-functions

# HTTP APIs
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 apigatewayv2 get-apis

# DynamoDB tables
sudo docker compose run deployer \
  aws --endpoint-url http://dynamodb-local:8000 dynamodb list-tables
```

### Ver logs de un Lambda

```bash
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda get-function \
    --function-name ecommerce
```

## Deployment a AWS Real

Para desplegar a AWS real (cuando sea el momento):

1. Configura credenciales AWS:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

2. Ejecuta CDK deploy contra AWS:
```bash
cd infra
cdk deploy --require-approval never
```

CDK automáticamente detectará que no hay `AWS_ENDPOINT` configurado y deployará a AWS real.

## Recursos útiles

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [aws-cdk-lib Python API Reference](https://docs.aws.amazon.com/cdk/api/latest/python/index.html)
- [AWS Lambda Integration with API Gateway V2](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigatewayv2_integrations.html)
- [LocalStack Documentation](https://docs.localstack.cloud/)
