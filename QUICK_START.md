# Quick Start - Conectar Frontend con Lambdas

## En 5 minutos

```bash
# 1. Iniciar todos los servicios (ministack, dynamodb, redis, frontend)
make up

# Esperar ~10 segundos a que ministack esté listo
sleep 10

# 2. Desplegar infraestructura (lambdas + API Gateway con CDK)
make deploy

# 3. Crear tablas DynamoDB
make create-table

# 4. Cargar datos de prueba
make seed

# 5. Validar que todo está conectado
make validate

# 6. Acceder al frontend
# Abre en el navegador: http://localhost:5173/?user_id=1&order_id=555
```

## ¿Qué acaba de pasar?

1. **`make up`** inició 5 servicios Docker:
   - `ministack` - Emulador de AWS (Lambda, API Gateway, DynamoDB en puerto 4566)
   - `dynamodb-local` - DynamoDB local en puerto 8001
   - `redis` - Redis para caché
   - `deployer` - Contenedor con Python, CDK, awscli
   - `frontend` - React + Vite en puerto 5173

2. **`make deploy`** ejecutó CDK que:
   - Creó 2 Lambda functions: `ecommerce` (multi-handler), `products`
   - Creó HTTP API Gateway con 7 rutas HTTP
   - Asignó permisos IAM para que los lambdas accedan a DynamoDB

3. **`make create-table`** creó la tabla DynamoDB `ecommerce` con:
   - Partition Key: `user_id`
   - Sort Key: `sort_key`

4. **`make seed`** insertó datos de prueba en la tabla

5. **Frontend** en http://localhost:5173 hace requests HTTP a `/ecommerce/...` que:
   - Vite proxea a `http://ministack:4566/ecommerce/...`
   - API Gateway recibe la request y invoca el Lambda correspondiente
   - Lambda accede a DynamoDB y retorna datos
   - Frontend renderiza los datos en React

## Arquitectura

```
┌─────────────────┐
│  Frontend       │
│  React + Vite   │
│  :5173          │
└────────┬────────┘
         │ fetch('/ecommerce/user/123/profile')
         │
    Vite proxy target:
    http://ministack:4566
         │
         ▼
┌──────────────────────────┐
│   LocalStack/Ministack   │
│   :4566                  │
│                          │
│  HTTP API Gateway ─────▶ Lambdas ─────▶ DynamoDB
│  (routes)   (ecommerce,      (query data)
│             products)        
└──────────────────────────┘
```

## URLs Importantes

- **Frontend:** http://localhost:5173
- **Frontend con datos:** http://localhost:5173?user_id=1&order_id=555
- **LocalStack API:** http://localhost:4566 (acceso interno a Lambdas, API Gateway)
- **DynamoDB Local:** http://localhost:8001 (acceso admin)

## Rutas HTTP Disponibles

Todas disponibles en http://localhost:5173/ con proxy automático:

```
GET /ecommerce/user/{user_id}/profile
GET /ecommerce/user/{user_id}/orders
GET /ecommerce/user/{user_id}/order/{order_id}/details
GET /ecommerce/user/{user_id}/order/{order_id}/items
GET /ecommerce/order/{order_id}/details
GET /ecommerce/order/{order_id}/items
GET /ecommerce/dashboard-data?user_id={id}&order_id={id}
GET /products
```

Ejemplos:
```
http://localhost:5173/ecommerce/user/1/profile
http://localhost:5173/ecommerce/user/1/orders
http://localhost:5173/ecommerce/dashboard-data?user_id=1&order_id=555
```

## Próximos Pasos

### Ver logs
```bash
make logs-frontend    # Logs del frontend
make logs-ministack   # Logs de LocalStack
```

### Modificar un Lambda
1. Edita el archivo en `lambdas/ecommerce/`
2. Redeploy: `make deploy`
3. La change se refleja automáticamente

### Agregar una nueva ruta
1. Crea `lambdas/ecommerce/mi_handler.py` con `def lambda_handler(event, context)`
2. Agrega a `infra/api_stack.py`:
   ```python
   handlers = {
       ...
       "/ecommerce/mi-ruta": "mi_handler",
   }
   ```
3. Redeploy: `make deploy`

### Cargar más datos
1. Edita `scripts/seed_data.py`
2. Ejecuta: `make seed`

### Detener servicios
```bash
make down      # Para servicios pero no borra volumes
make clean     # Para servicios Y borra volumes
```

## Debugging

```bash
# Ver estado de todos los servicios
sudo docker compose ps

# Ver logs detallados
sudo docker compose logs deployer

# Probar un Lambda directamente
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda invoke \
    --function-name ecommerce \
    --payload '{"test":"data"}' \
    /tmp/response.json && cat /tmp/response.json

# Ver requests HTTP en el browser (F12 → Network tab)
```

## Si algo no funciona

Pasos de troubleshooting:

1. **¿Ministack está listo?**
   ```bash
   sudo docker compose logs ministack | tail -20
   # Buscar: "Startup finished"
   ```

2. **¿Lambdas están deployados?**
   ```bash
   make test-api
   ```

3. **¿Tabla DynamoDB existe?**
   ```bash
   sudo docker compose run deployer \
     aws --endpoint-url http://dynamodb-local:8000 dynamodb list-tables
   ```

4. **¿Frontend conecta a ministack?**
   - Abre DevTools (F12)
   - Network tab
   - Haz una acción en el frontend
   - Verifica que ves requests a `/ecommerce/...`
   - Status debe ser 200 (si es 404, CDK no fue deployado)

Ver **TROUBLESHOOTING.md** para guía completa de debugging.

## Documentación Completa

- **FRONTEND_CONNECTION_GUIDE.md** - Cómo funciona la conexión Frontend→Lambda→DynamoDB en detalle
- **infra/README.md** - Cómo funciona CDK y cómo modificar la infraestructura
- **TROUBLESHOOTING.md** - Soluciones a problemas comunes
- **README.md** - Documentación general del proyecto

## Comandos Make Disponibles

```bash
make help              # Ver todos los comandos
make up                # Iniciar servicios
make down              # Detener servicios
make deploy            # Desplegar CDK (lambdas + API Gateway)
make create-table      # Crear tabla DynamoDB
make seed              # Cargar datos de prueba
make validate          # Validar conectividad completa
make test-api          # Probar API Gateway
make logs-frontend     # Ver logs del frontend
make logs-ministack    # Ver logs de ministack
make clean             # Limpiar todo
```

## ¡Listo!

Ahora puedes:
- ✅ Acceder al frontend: http://localhost:5173
- ✅ Ver datos cargados desde lambdas
- ✅ Modificar handlers de lambdas
- ✅ Agregar nuevas rutas HTTP
- ✅ Escalar a AWS real cuando esté listo

¡Diviértete! 🚀
