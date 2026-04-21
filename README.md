

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

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Configurar variables de entorno (`.env`):

```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1


# Local
DYNAMODB_ENDPOINT_URL=http://localhost:8001

ECOMMERCE_TABLE_NAME=ecommerce

REDIS_HOST=localhost
REDIS_PORT=6379
```

4. Configurar el frontend:

```bash
cp frontend/.env.example frontend/.env
```

Si vas a correr en Docker, puedes dejar `VITE_API_PROXY_TARGET=http://backend:8000`. Si vas a correr localmente, el valor por defecto `http://localhost:8000` funciona.

5. Levantar DynamoDB Local y awscli:

```bash
docker compose up -d dynamodb-local awscli
```

6. Crear la tabla `ecommerce`:

```bash
python scripts/create_table.py
```

7. Ejecutar el backend:

```bash
uvicorn app.main:app --reload
```

8. Ejecutar el frontend:

```bash
cd frontend
npm run dev
```

9. Abrir la interfaz:

* Frontend: [http://localhost:5173](http://localhost:5173)
* API root: [http://localhost:8002](http://localhost:8002) (o el puerto definido en `BACKEND_PORT`)
* Datos del panel: [http://localhost:8002/ecommerce/dashboard-data](http://localhost:8002/ecommerce/dashboard-data) (o el puerto definido en `BACKEND_PORT`)
* Perfil de usuario: [http://localhost:8002/ecommerce/user/1/profile](http://localhost:8002/ecommerce/user/1/profile)
* Pedidos recientes: [http://localhost:8002/ecommerce/user/1/orders](http://localhost:8002/ecommerce/user/1/orders)
* Detalle del pedido: [http://localhost:8002/ecommerce/order/555/details](http://localhost:8002/ecommerce/order/555/details)
* Items del pedido: [http://localhost:8002/ecommerce/order/555/items](http://localhost:8002/ecommerce/order/555/items)

---

## Documentación de la API

FastAPI genera documentación automáticamente:

* Swagger UI: [http://localhost:8002/docs](http://localhost:8002/docs)
* ReDoc: [http://localhost:8002/redoc](http://localhost:8002/redoc)

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

Levanta todo con Docker:

```bash
docker compose up --build
```

Si el puerto `8000` esta ocupado, puedes levantar el backend en otro puerto del host:

```bash
BACKEND_PORT=8002 docker compose up --build
```

Por defecto, este compose ya usa `8002` para evitar colisiones con procesos locales en `8000`.

Tambien usa DynamoDB Local en modo `inMemory` para evitar bloqueos por archivos SQLite en desarrollo.

Si prefieres correr localmente, usa el paso a paso anterior. La URL `/` del backend devuelve estado y enlaces útiles, mientras que el frontend vive en `http://localhost:5173`.

## Pruebas

Para probar la API puedes usar:

```bash
curl "http://localhost:8002/ecommerce/dashboard-data?user_id=1&order_id=555&demo=true"
```

Si levantaste con `BACKEND_PORT=8002`, usa ese puerto en el `curl`.

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
