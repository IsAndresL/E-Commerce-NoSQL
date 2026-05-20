# Troubleshooting Guide

## Problemas Comunes y Soluciones

### Frontend Issues

#### ❌ "Cannot GET /ecommerce/..." (404 error)

**Síntomas:** El frontend hace requests a `/ecommerce/...` pero obtiene 404.

**Causas posibles:**
1. CDK no fue deployado (no hay HTTP API Gateway)
2. Los Lambdas no están creados
3. Las rutas no están registradas en API Gateway

**Soluciones:**

```bash
# 1. Verificar que CDK fue deployado
make deploy

# 2. Verificar que Lambda functions existen
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda list-functions

# 3. Verificar que HTTP API Gateway existe
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 apigatewayv2 get-apis

# 4. Si no hay APIs, redeploy
make deploy
```

---

#### ❌ "timeout de conexión" o "ECONNREFUSED" en el frontend

**Síntomas:** El frontend intenta conectar pero obtiene error de conexión.

**Causas posibles:**
1. ministack no está corriendo
2. ministack no está listo aún (necesita esperar ~10s)
3. El frontend no está usando la variable `VITE_API_PROXY_TARGET` correctamente

**Soluciones:**

```bash
# 1. Verificar que ministack está corriendo
sudo docker compose ps | grep ministack

# 2. Si no está, iniciarlo
make up
sleep 10  # Esperar a que se inicie completamente

# 3. Verificar que ministack responde
sudo docker compose exec ministack \
  curl -s http://localhost:4566/health | head -20

# 4. Verificar que el frontend tiene la variable correcta
sudo docker compose exec frontend sh -c 'env | grep VITE'
# Debe mostrar: VITE_API_PROXY_TARGET=http://ministack:4566
```

---

#### ❌ Frontend hace requests a `http://localhost:8000` en lugar de ministack:4566

**Síntomas:** En DevTools Network tab, ves que el frontend está intentando conectar a `localhost:8000` (el viejo backend FastAPI).

**Causa:** La variable `VITE_API_PROXY_TARGET` no está correctamente configurada en `docker-compose.yml`.

**Solución:**

1. Verifica `docker-compose.yml`:
```yaml
frontend:
  environment:
    VITE_API_PROXY_TARGET: http://ministack:4566  # ← Debe estar aquí
```

2. Si no está, agrégalo manualmente

3. Redeploy:
```bash
sudo docker compose down frontend
sudo docker compose up -d frontend
```

---

#### ❌ "Mixed Content" error - "cannot load http content over https"

**Síntomas:** El navegador bloquea requests porque la página es HTTPS pero intenta cargar HTTP.

**Causa:** Estás accediendo al frontend vía HTTPS pero el proxy apunta a HTTP.

**Solución:**

En desarrollo local, evita HTTPS:
- Usa `http://localhost:5173` (no `https://`)
- Si accedes via HTTPS, configura el proxy para HTTPS también

---

### Backend / Lambda Issues

#### ❌ "EndpointConnectionError: Could not connect to the endpoint URL"

**Síntomas:** El Lambda intenta acceder a DynamoDB pero obtiene error de conexión.

**Causa:** El Lambda no tiene la variable de entorno `AWS_ENDPOINT_URL` correctamente configurada, o DynamoDB-local no está corriendo.

**Soluciones:**

```bash
# 1. Verificar que DynamoDB Local está corriendo
sudo docker compose ps | grep dynamodb

# 2. Verificar que responde
sudo docker compose exec dynamodb-local \
  curl -s http://localhost:8000/ | head -5

# 3. Si no está corriendo, iniciar todos los servicios
make up

# 4. Redeploy para que el Lambda tenga la variable correcta
make deploy
```

---

#### ❌ Lambda invocation returns "Error" o JSON vacío

**Síntomas:** Lambda se invoca pero retorna un error o respuesta vacía.

**Debug:**

```bash
# 1. Ver logs del Lambda
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda invoke \
    --function-name ecommerce \
    --payload '{"httpMethod":"GET","path":"/ecommerce/user/123/profile"}' \
    --log-type Tail \
    /tmp/response.json

# 2. Ver la respuesta
cat /tmp/response.json

# 3. Buscar el error en los logs del Lambda (si aparecen en la invocación)
```

---

#### ❌ "TableNotFoundException" o "ResourceNotFoundException" en Lambda

**Síntomas:** El Lambda intenta acceder a la tabla DynamoDB pero dice que no existe.

**Causas:**
1. La tabla no fue creada
2. El Lambda está buscando el nombre incorrecto de tabla
3. El Lambda está apuntando a la región incorrecta

**Soluciones:**

```bash
# 1. Crear la tabla
make create-table

# 2. Verificar que la tabla existe
sudo docker compose run deployer \
  aws --endpoint-url http://dynamodb-local:8000 dynamodb list-tables

# 3. Verificar el nombre exacto de la tabla
# Debería estar en: scripts/create_table.py → TableName='ecommerce'

# 4. Verificar que el Lambda tiene la variable de entorno TABLE_NAME
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda get-function-configuration \
    --function-name ecommerce | grep TABLE_NAME

# 5. Si es incorrecto, redeploy
make deploy
```

---

### Docker / Services Issues

#### ❌ "Cannot connect to Docker daemon"

**Síntomas:** Al ejecutar `docker` o `sudo docker`, obtienes error de conexión.

**Causa:** Docker no está instalado o el daemon no está corriendo.

**Soluciones:**

```bash
# Verificar que Docker está instalado
docker --version

# Si no está, instalarlo (macOS/Linux)
# macOS:
brew install docker docker-compose

# Linux (Ubuntu/Debian):
sudo apt-get install docker.io docker-compose

# Iniciar Docker daemon
sudo systemctl start docker

# Verificar que funciona
sudo docker ps
```

---

#### ❌ "Permission denied while trying to connect to Docker daemon"

**Síntomas:** `sudo docker` funciona pero `docker` sin sudo no funciona.

**Causa:** Tu usuario no tiene permisos para acceder a Docker.

**Soluciones:**

```bash
# Opción 1: Usar siempre sudo (lo que hacemos en los comandos)
sudo docker compose up

# Opción 2: Agregar tu usuario al grupo docker (requiere logout/login)
sudo usermod -aG docker $USER
newgrp docker
docker compose up
```

---

#### ❌ "network ecommerce-net not found"

**Síntomas:** Al intentar hacer `docker compose run`, obtienes error sobre la red.

**Causa:** La red de Docker Compose fue eliminada o no se creó.

**Soluciones:**

```bash
# Recrear la red y servicios
sudo docker compose down
sudo docker compose up -d

# O limpiar completamente
make clean
make up
```

---

#### ❌ "port 5173 already in use"

**Síntomas:** El frontend no inicia porque el puerto 5173 está en uso.

**Causas:**
1. Ya hay otra instancia del frontend corriendo
2. Otro proceso está usando el puerto 5173

**Soluciones:**

```bash
# 1. Detener el frontend antiguo
sudo docker compose down frontend

# 2. Si aún sigue en uso, encontrar qué está usando el puerto
sudo lsof -i :5173

# 3. Matar el proceso
kill -9 <PID>

# 4. Reintentar
make up
```

---

#### ❌ "Cannot start service deployer: Dockerfile not found"

**Síntomas:** Al hacer `make deploy` o `make up`, obtiene error sobre Dockerfile.

**Causa:** El archivo `deployer/Dockerfile` no existe.

**Verificar:**

```bash
ls -la deployer/Dockerfile

# Si no existe, debe estar en:
# E-Commerce-NoSQL/deployer/Dockerfile

# Si está en otro lado o no existe, crear o mover correctamente
```

---

### CDK / Deployment Issues

#### ❌ "No stacks to deploy" o "deployment skipped"

**Síntomas:** `cdk deploy` termina sin crear nada.

**Causas:**
1. Los stacks ya existen (update, no create)
2. No hay cambios detectados
3. LocalStack no responde

**Soluciones:**

```bash
# 1. Forzar redeploy
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://ministack:4566 \
  sh -c 'cd infra && cdk deploy --force --require-approval never'

# 2. Destruir stacks antigos en LocalStack y redeploy
# (LocalStack limpia auto al reiniciar, así que):
sudo docker compose restart ministack
make deploy

# 3. Ver el estado de los stacks
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 cloudformation list-stacks
```

---

#### ❌ "ModuleNotFoundError" o "ImportError" durante CDK deploy

**Síntomas:** `cdk deploy` falla con error de importación.

**Causa:** Las dependencias de Python no están instaladas en el contenedor `deployer`.

**Soluciones:**

```bash
# 1. Rebuildar el contenedor deployer
sudo docker compose build deployer

# 2. Reinstalar dependencias
sudo docker compose run deployer pip install -r requirements.txt

# 3. Reintentar
make deploy
```

---

### Data / DynamoDB Issues

#### ❌ "No data showing in frontend" o tabla vacía

**Síntomas:** El frontend carga pero muestra datos vacíos.

**Causas:**
1. Los datos no fueron seeded
2. El Lambda está haciendo query a la tabla incorrecta
3. Los datos fueron insertados con formato incorrecto

**Soluciones:**

```bash
# 1. Hacer seed de datos
make seed

# 2. Verificar que los datos existen
sudo docker compose run deployer \
  aws --endpoint-url http://dynamodb-local:8000 dynamodb scan \
    --table-name ecommerce

# 3. Si no hay datos, revisar el script seed_data.py
cat scripts/seed_data.py

# 4. Reimportar si es necesario
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://dynamodb-local:8000 \
  python scripts/seed_data.py
```

---

#### ❌ Datos duplicados o corrompidos en DynamoDB

**Síntomas:** Los datos se ven duplicados o incompletos.

**Causas:**
1. Ejecutaste seed múltiples veces
2. Data fue parcialmente importada

**Soluciones:**

```bash
# 1. Limpiar y recrear la tabla
sudo docker compose run deployer \
  -e AWS_ENDPOINT=http://dynamodb-local:8000 \
  aws dynamodb delete-table --table-name ecommerce

# 2. Recrear
make create-table

# 3. Reseed
make seed

# O más simple:
make clean
make up
make deploy
make create-table
make seed
```

---

## Debugging en DevTools

### Browser Console / Network Tab

1. Abre http://localhost:5173 en el navegador
2. Presiona F12 para abrir DevTools
3. Ve a **Network** tab
4. Realiza una acción en el frontend (ej: cargar perfil de usuario)
5. Deberías ver requests a `/ecommerce/...`
6. Verifica:
   - **URL:** Debería ser `http://localhost:5173/ecommerce/...`
   - **Status:** Debería ser 200 (OK)
   - **Response:** Debería contener JSON con datos

Si ves 404 o 500, revisa:
- El Lambda está deployado (`make deploy`)
- La ruta existe en CDK (`infra/api_stack.py`)
- La tabla DynamoDB existe (`make create-table`)

---

## Comandos de Verificación Rápida

```bash
# Verificar que todo está corriendo
make up

# Verificar que los Lambdas están deployados
make test-api

# Verificar conectividad completa
make validate

# Ver logs del frontend (para errores de conexión)
make logs-frontend

# Ver logs de ministack (para errores de Lambda)
make logs-ministack

# Limpiar todo y empezar de cero
make clean
make up
make deploy
make create-table
make seed
make validate
```

---

## Request para Support

Si aún no funciona, copia esta información y pégala cuando pidas ayuda:

```bash
# Información de sistema
uname -a
docker --version
docker compose --version

# Estado de servicios
sudo docker compose ps

# Log de deployer (últimos 50 líneas)
sudo docker compose logs deployer | tail -50

# Log de ministack (últimos 50 líneas)
sudo docker compose logs ministack | tail -50

# Lista de Lambdas
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda list-functions

# Estado de DynamoDB
sudo docker compose run deployer \
  aws --endpoint-url http://dynamodb-local:8000 dynamodb list-tables

# Error específico del navegador (captura en DevTools)
```

---

## Preguntas Frecuentes

### ¿Por qué se usa `ministack` en lugar de `localhost`?

LocalStack necesita ser accedido por nombre de servicio (ministack) cuando estás dentro de la red Docker. `localhost` desde dentro de un contenedor apunta al contenedor mismo, no al host.

### ¿Puedo acceder a ministack desde mi máquina host?

Sí, usa `http://localhost:4566`. Pero desde dentro de contenedores Docker, debe ser `http://ministack:4566`.

### ¿Qué pasa si los servicios no inician?

Algunos servicios como ministack pueden tardar 10-20 segundos en estar listos. Los scripts tienen retry logic, pero puedes esperar manualmente:

```bash
make up
sleep 15  # Esperar a que ministack esté 100% listo
make deploy
```

### ¿Puedo desplegar a AWS real?

Sí, pero requiere credenciales AWS y cambios en la configuración. Ver [infra/README.md](infra/README.md#deployment-a-aws-real).

### ¿Cómo debuggeo un Lambda específico?

```bash
sudo docker compose run deployer \
  aws --endpoint-url http://ministack:4566 lambda invoke \
    --function-name ecommerce \
    --payload '{"test": "data"}' \
    --log-type Tail \
    /tmp/response.json && cat /tmp/response.json
```

Ver la response en `/tmp/response.json` y los logs en la salida.
