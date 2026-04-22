

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

* **Backend Framework:** FastAPI
* **Lenguaje:** Python 3.11+
* **Base de datos principal:** DynamoDB (NoSQL)
* **Cache / almacenamiento en memoria:** Redis
* **SDK AWS:** boto3
* **Servidor ASGI:** Uvicorn
* **Validación de datos:** Pydantic
* **Gestión de configuración:** python-dotenv

La interfaz web vive en `frontend/` y consume la API en `app/`. DynamoDB Local y awscli quedan como soporte para pruebas locales.

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

## Dependencias

Instala las dependencias principales con:

```bash
pip install fastapi uvicorn boto3 redis pydantic python-dotenv
```

Dependencias de desarrollo (opcional):

```bash
pip install pytest httpx
```

Frontend:

```bash
cd frontend
npm install
```

---

## Ejecución del Proyecto

1. Clonar el repositorio:

```bash
git clone <repo-url>
cd <repo-name>
```

2. Copiar archivo de variables del backend:

```bash
cp .env.example .env
```

3. Elegir modo de ejecucion.

### Opcion A: Docker (recomendado)

1. Levantar servicios:

```bash
docker compose up -d --build
```

2. Crear la tabla en DynamoDB Local (dentro del contenedor backend):

```bash
docker compose exec backend python -m scripts.create_table
```

3. Cargar datos iniciales (seed):

```bash
docker compose exec backend python -m scripts.seed_data
```

4. Abrir la aplicacion:

* Frontend: [http://localhost:5173](http://localhost:5173)
* Frontend con IDs: [http://localhost:5173/?user_id=1&order_id=555](http://localhost:5173/?user_id=1&order_id=555)
* API (Docker): [http://localhost:8002/docs](http://localhost:8002/docs)

### Opcion B: Manual (sin Docker para backend/frontend)

1. Levantar solo DynamoDB Local y awscli:

```bash
docker compose up -d dynamodb-local awscli
```

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Instalar dependencias backend:

```bash
pip install -r requirements.txt
```

4. Crear la tabla `ecommerce`:

```bash
python -m scripts.create_table
```

5. Cargar datos iniciales (seed):

```bash
python -m scripts.seed_data
```

6. Ejecutar backend (manual):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. Configurar frontend:

```bash
cp frontend/.env.example frontend/.env
```

`frontend/.env` debe tener (o mantener) este valor para modo manual:

```env
VITE_API_PROXY_TARGET=http://localhost:8000
```

8. Ejecutar frontend:

```bash
cd frontend
npm install
npm run dev
```

9. Abrir la aplicacion:

* Frontend: [http://localhost:5173](http://localhost:5173)
* Frontend con IDs: [http://localhost:5173/?user_id=1&order_id=555](http://localhost:5173/?user_id=1&order_id=555)
* API (manual): [http://localhost:8000/docs](http://localhost:8000/docs)

### Variables de entorno del backend (`.env`)

```env
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
AWS_DEFAULT_REGION=us-east-1


# Local
DYNAMODB_ENDPOINT_URL=http://localhost:8001

ECOMMERCE_TABLE_NAME=ecommerce

REDIS_HOST=localhost
REDIS_PORT=6379
```

Parametros del frontend:

* `user_id`: ID del usuario
* `order_id`: ID de la orden/pedido

---

## Documentación de la API

FastAPI genera documentación automáticamente:

* Swagger UI (Docker): [http://localhost:8002/docs](http://localhost:8002/docs)
* Swagger UI (Manual): [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc (Docker): [http://localhost:8002/redoc](http://localhost:8002/redoc)
* ReDoc (Manual): [http://localhost:8000/redoc](http://localhost:8000/redoc)

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

## Arranque

Arranque rapido con Docker:

```bash
docker compose up --build
```

Si el puerto `8000` esta ocupado, puedes levantar el backend en otro puerto del host:

```bash
BACKEND_PORT=8002 docker compose up --build
```

Por defecto, este compose ya usa `8002` para evitar colisiones con procesos locales en `8000`.

Tambien usa DynamoDB Local en modo `inMemory` para evitar bloqueos por archivos SQLite en desarrollo.

Si prefieres correr localmente, usa la Opcion B de la seccion "Ejecución del Proyecto". El frontend vive en `http://localhost:5173`.

## Pruebas

Para probar la API puedes usar:

```bash
curl "http://localhost:8002/ecommerce/dashboard-data?user_id=1&order_id=555"
```

En modo manual, usa el puerto `8000`:

```bash
curl "http://localhost:8000/ecommerce/dashboard-data?user_id=1&order_id=555"
```

Para probar DynamoDB Local desde `awscli`:

```bash
docker compose exec -T awscli aws dynamodb list-tables --endpoint-url http://dynamodb-local:8000 --no-cli-pager
```

---

## Testing

Para ejecutar pruebas:

```bash
pytest
```

---

## Docker (Opcional)

```dockerfile
FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install fastapi uvicorn boto3 redis pydantic python-dotenv

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Licencia

Este proyecto es de uso académico - Grupo 2.
