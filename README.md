

# E-commerce API - Grupo 2

API RESTful para un sistema de e-commerce construida con un enfoque moderno, escalable y orientado a microservicios.

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

---

## Arquitectura

El proyecto sigue una arquitectura modular basada en capas:

```
app/
├── api/            # Endpoints (routes)
├── services/       # Lógica de negocio
├── repositories/   # Acceso a datos (DynamoDB)
├── models/         # Esquemas (Pydantic)
├── db/             # Conexiones (DynamoDB, Redis)
├── core/           # Configuración global
└── main.py         # Punto de entrada
```

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
AWS_ACCESS_KEY=your_key
AWS_SECRET_KEY=your_secret
AWS_REGION=us-east-1

REDIS_HOST=localhost
REDIS_PORT=6379
```

4. Ejecutar el servidor:

```bash
uvicorn app.main:app --reload
```

---

## Documentación de la API

FastAPI genera documentación automáticamente:

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Integraciones

* **DynamoDB:** almacenamiento principal de productos, usuarios y órdenes
* **Redis:** caching, sesiones y optimización de consultas
* **boto3:** comunicación con servicios AWS

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
