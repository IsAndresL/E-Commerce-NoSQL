# E-commerce API - Grupo 2

API RESTful para un sistema de e-commerce construida con un enfoque moderno, escalable. El proyecto ahora incluye un frontend separado con React + Vite, una abstracción clara de la tabla `ecommerce` y un adaptador de acceso a DynamoDB.

---

## Colaboradores

* Farit Teran
* Andres Luna
* Daniel Ortiz

---

## Stack Tecnológico

Este proyecto está construido utilizando las siguientes tecnologías:

* **Backend:** Serverless (AWS Lambda + API Gateway HttpApi)
* **Infraestructura:** AWS CDK (Infrastructure as Code)
* **Lenguaje:** Python 3.11+
* **Base de datos principal:** DynamoDB (NoSQL)
* **Cache / almacenamiento en memoria:** Redis
* **SDK AWS:** boto3, aws-cdk-lib
* **Validación de datos:** Pydantic
* **Gestión de configuración:** python-dotenv
* **Frontend:** React 18 + Vite
* **Emulación local:** LocalStack/Ministack (AWS Lambda, API Gateway, DynamoDB en Docker)

La arquitectura ahora es **totalmente serverless**: los lambdas se invocan a través de **HTTP API Gateway** en lugar de FastAPI. Todo corre en Docker sin necesidad de instalar Python en tu máquina.

---

## Arquitectura

El proyecto sigue una arquitectura modular basada en capas:

Documentacion de flujo (cliente -> API -> DynamoDB):

* Ver `README_FLUJO.md`

```
app/
├── api/            # Endpoints (routes)
├── services/       # Lógica de negocio
├── repositories/   # Abstracción de la tabla Ecommerce
├── models/         # Esquemas (Pydantic)
├── db/             # Conexiones (DynamoDB, Redis)
├── core/           # Configuración global
└── main.py         # Punto de entrada
```

### Capas clave

* `app/services/dynamodb_adapter.py`: adaptador genérico para DynamoDB.
* `app/repositories/ecommerce_table.py`: abstracción de la tabla `ecommerce` y sus patrones de acceso.
* `app/services/ecommerce_dashboard_service.py`: preparación de datos para el panel de control.
* `app/api/routes/ecommerce.py`: endpoints JSON y vista legacy de apoyo.
* `frontend/`: frontend separado en React + Vite.

---

## Instalación y ejecución

**No necesitas instalar Python en tu máquina.** Todo corre con Docker.

### Requisitos previos

* Docker y Docker Compose instalados
* `sudo` acceso para ejecutar Docker (o agregar tu usuario al grupo docker)

### 1) Clonar el proyecto

```bash
git clone <repo-url>
cd E-Commerce-NoSQL
```

### 2) Preparar variables de entorno (opcional)

```bash
cp .env.example .env
```

### 3) Quick Start - Comando único

**Opción 1: Con Make (recomendado)**

```bash
make up           # Inicia todos los servicios
make deploy       # Despliega lambdas y API Gateway con CDK
make create-table # Crea tablas DynamoDB
make seed         # Carga datos de prueba
```

Luego accede a: **http://localhost:5173**

**Opción 2: Manual (sin Make)**

```bash
# Inicia servicios
sudo docker compose up -d ministack redis
sleep 5  # Espera a que ministack esté listo

# Despliega infraestructura (lambdas + API Gateway)
sudo docker compose run --rm --entrypoint /bin/sh \
  -e AWS_ENDPOINT=http://ministack:4566 \
  -e AWS_REGION=us-east-1 \
  deployer -c 'cd infra && cdk deploy --require-approval never'

# Crea tablas DynamoDB
sudo docker compose run --rm --entrypoint /bin/sh \
  -e AWS_ENDPOINT=http://ministack:4566 \
  -e AWS_REGION=us-east-1 \
  deployer -c 'python scripts/create_table.py'

# Carga datos de prueba
sudo docker compose run --rm --entrypoint /bin/sh \
  -e AWS_ENDPOINT=http://ministack:4566 \
  -e AWS_REGION=us-east-1 \
  deployer -c 'python scripts/seed_data.py'

# Inicia frontend
sudo docker compose up -d frontend
```

### 4) Acceder a la aplicación

* **Frontend:** [http://localhost:5173](http://localhost:5173)
* **Frontend con datos específicos:** [http://localhost:5173/?user_id=1&order_id=555](http://localhost:5173/?user_id=1&order_id=555)
* **Ministack/LocalStack:** http://localhost:4566 (API Gateway)
* **DynamoDB en MiniStack:** http://localhost:4566

### 5) Verificar que todo funciona

```bash
# Listar funciones lambda deployadas
sudo docker compose run --rm deployer \
  aws --endpoint-url http://ministack:4566 lambda list-functions

# Probar invocación directa de lambda
sudo docker compose run --rm deployer \
  aws --endpoint-url http://ministack:4566 lambda invoke \
    --function-name ecommerce \
    --payload '{"httpMethod":"GET","path":"/ecommerce/user/1/profile"}' \
    /tmp/response.json && cat /tmp/response.json
```

### Comandos útiles con Make

```bash
make help         # Muestra todos los comandos disponibles
make logs-frontend   # Ver logs del frontend
make logs-ministack  # Ver logs de LocalStack
make test-api     # Probar conectividad API Gateway
make clean        # Eliminar contenedores y volúmenes
make down         # Detener servicios sin eliminarlos
```

### Estructura de carpetas (Serverless)

```
infra/
├── app.py                 # CDK App (orquestador)
├── api_stack.py          # Stack: Lambda + HTTP API routes
├── persistence_stack.py  # Stack: DynamoDB
├── core_stack.py         # Stack: Configuración base
└── cdk.json             # Configuración CDK para LocalStack

lambdas/
├── ecommerce/           # Lambda handlers para e-commerce
│   ├── handler.py       # Router principal (HTTP API entrypoint)
│   ├── get_user_profile.py
│   ├── get_recent_orders.py
│   ├── get_order_details.py
│   └── ...
└── products/            # Lambda handlers para productos
    ├── handler.py
    └── list_products.py

scripts/
├── deploy_ministack.sh  # Despliega CDK a LocalStack
├── create_table.py      # Crea tablas DynamoDB
├── seed_data.py         # Carga datos iniciales
└── test_api_gateway.sh  # Valida conectividad API Gateway

frontend/
├── src/
│   ├── App.jsx          # Componente principal
│   ├── api/
│   │   └── ecommerceApi.js  # Cliente fetch para lambdas
│   └── components/
│       └── dashboard/   # Componentes de UI
└── vite.config.js       # Configuración proxy a ministack:4566
```
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT=http://ministack:4566
```

Parámetros del frontend:

* `user_id`: ID del usuario
* `order_id`: ID de la orden/pedido

### Apagar el entorno local

```bash
sudo docker compose down
```

### Documentación de la API

La API vive en `lambdas/` y se expone a través de API Gateway local cuando usas `ministack`.

* Endpoint local de pruebas: depende de la ruta montada en `infra/api_stack.py`
* Para invocar directo, usa `aws lambda invoke` contra `http://ministack:4566`

---

## Integraciones

* **DynamoDB:** almacenamiento principal de productos, usuarios y órdenes
* **Redis:** caching, sesiones y optimización de consultas
* **boto3:** comunicación con servicios AWS

## Patrones de acceso a DynamoDB

La tabla `ecommerce` usa una clave compuesta `PK` y `SK`. Los accesos principales están modelados así:

1. Obtener perfil de usuario

	* `PK = USER#<ID>`
	* `SK = PROFILE`

2. Obtener pedidos recientes

	* `PK = USER#<ID>`
	* `SK = ORDER#<times>`

3. Obtener detalles del pedido

	* `PK = ORDER#<ID>`
	* `SK = DETAILS`

4. Obtener ítems del pedido

	* `PK = ORDER#<ID>`
	* `SK = ITEM#<ID>`

## Interfaz

La pantalla principal del frontend agrupa:

* Perfil del usuario
* Pedidos recientes
* Detalle del pedido seleccionado
* Ítems del pedido

El diseño es responsivo y se adapta a escritorio y móvil.

## Pruebas

Una vez levantado el entorno, puedes comprobar que DynamoDB responde:

```bash
sudo docker compose run --rm --entrypoint /bin/sh -e AWS_ENDPOINT_URL=http://ministack:4566 deployer -c 'aws --endpoint-url http://ministack:4566 dynamodb list-tables --no-cli-pager'
```

Si quieres verificar la API agregada desde el handler, puedes invocar directamente la lambda `ecommerce` con `aws lambda invoke` como se muestra arriba.

## Notas sobre Docker

* El servicio `deployer` incluye Python, `awscli` y la CLI de CDK.
* El servicio `ministack` usa la red Docker `ecommerce-net` para ejecutar las Lambdas.
* Si el despliegue falla con permisos, antepone `sudo` a los comandos `docker compose`.

---

## Licencia

Este proyecto es de uso académico - Grupo 2.
