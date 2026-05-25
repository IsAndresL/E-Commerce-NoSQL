# Comandos para inspeccionar datos en AWS / MiniStack

Este documento reúne comandos útiles para ver tablas, revisar ítems y consultar datos en DynamoDB usando el entorno local del proyecto.

El endpoint local del proyecto es:

```bash
http://ministack:4566
```

Si ejecutas comandos desde tu máquina host, también puedes probar con:

```bash
http://localhost:4566
```

## 1. Verificar que MiniStack responde

La forma más útil dentro de este proyecto es probar una llamada AWS CLI contra el endpoint local:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 lambda list-functions --output table'
```

Si ese comando devuelve funciones, el endpoint está respondiendo.

## 2. Listar tablas DynamoDB

Desde el contenedor `cdk-deployer`:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb list-tables --output table'
```

Solo nombres de tablas:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb list-tables --query "TableNames" --output text'
```

## 3. Describir una tabla

Reemplaza `<NOMBRE_TABLA>` por la tabla que te devolvió `list-tables`:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb describe-table --table-name <NOMBRE_TABLA> --output table'
```

Para ver la definición completa en JSON:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb describe-table --table-name <NOMBRE_TABLA> --output json'
```

## 4. Ver todos los ítems de una tabla

El comando más directo para inspeccionar datos es `scan`:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb scan --table-name <NOMBRE_TABLA> --output table'
```

En JSON, si quieres más detalle:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb scan --table-name <NOMBRE_TABLA> --output json'
```

## 5. Ver un item específico con `get-item`

Si conoces la clave primaria exacta:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb get-item --table-name <NOMBRE_TABLA> --key "{\"PK\":{\"S\":\"USER#jgarcia\"},\"SK\":{\"S\":\"PROFILE\"}}" --output json'
```

Ejemplo para un detalle de orden:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb get-item --table-name <NOMBRE_TABLA> --key "{\"PK\":{\"S\":\"ORDER#200\"},\"SK\":{\"S\":\"DETAILS\"}}" --output json'
```

## 6. Consultar datos por partición con `query`

Esto es lo más útil en el modelo single-table del proyecto.

### Perfil de usuario

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb query --table-name <NOMBRE_TABLA> --key-condition-expression "PK = :pk AND SK = :sk" --expression-attribute-values ":pk={\"S\":\"USER#jgarcia\"},:sk={\"S\":\"PROFILE\"}" --output table'
```

### Pedidos de un usuario

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb query --table-name <NOMBRE_TABLA> --key-condition-expression "PK = :pk AND begins_with(SK, :prefix)" --expression-attribute-values ":pk={\"S\":\"USER#jgarcia\"},:prefix={\"S\":\"ORDER#\"}" --output table'
```

### Detalle de una orden

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb query --table-name <NOMBRE_TABLA> --key-condition-expression "PK = :pk" --expression-attribute-values ":pk={\"S\":\"ORDER#200\"}" --output table'
```

### Ítems de una orden

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb query --table-name <NOMBRE_TABLA> --key-condition-expression "PK = :pk AND begins_with(SK, :prefix)" --expression-attribute-values ":pk={\"S\":\"ORDER#200\"},:prefix={\"S\":\"ITEM#\"}" --output table'
```

## 7. Filtrar columnas con `--projection-expression`

Si el `scan` trae demasiado ruido, puedes pedir solo algunos campos:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb scan --table-name <NOMBRE_TABLA> --projection-expression "PK, SK, user_id, name, email" --output table'
```

## 8. Ver solo usuarios o solo órdenes

Como el proyecto usa una single-table, puedes usar `begins_with` sobre `PK` para ver grupos de datos.

Usuarios:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb scan --table-name <NOMBRE_TABLA> --filter-expression "begins_with(PK, :prefix)" --expression-attribute-values ":prefix={\"S\":\"USER#\"}" --output table'
```

Órdenes:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb scan --table-name <NOMBRE_TABLA> --filter-expression "begins_with(PK, :prefix)" --expression-attribute-values ":prefix={\"S\":\"ORDER#\"}" --output table'
```

## 9. Ver APIs y Lambdas relacionadas

Lambdas registradas:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 lambda list-functions --output table'
```

APIs HTTP:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 apigatewayv2 get-apis --output table'
```

Rutas de una API concreta:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 apigatewayv2 get-routes --api-id <API_ID> --output table'
```

## 10. Comandos rápidos de verificación

Estos son los más prácticos para el día a día:

```bash
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb list-tables --output table'
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 dynamodb scan --table-name <NOMBRE_TABLA> --output table'
sudo docker compose exec -T cdk-deployer sh -lc '.infra_venv/bin/python3 -m awscli --endpoint-url http://ministack:4566 lambda list-functions --output table'
```

## 11. Notas útiles

- Si estás usando AWS real, quita `--endpoint-url`.
- Si no sabes el nombre exacto de la tabla, empieza por `list-tables`.
- En este proyecto los datos importantes están modelados con `PK` y `SK`, así que `query` suele ser mejor que `scan`.
- Para el usuario demo del frontend, usa `USER#jgarcia` y `ORDER#200` como referencias rápidas.