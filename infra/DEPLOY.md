Despliegue de la infraestructura

Opciones para desplegar la infraestructura y probar las Lambdas.

1) Despliegue en AWS usando CDK

Requisitos:
- Node + npm (para instalar la CLI de CDK si se desea)
- Credenciales AWS configuradas (profile o variables de entorno)

Comandos clave:

```bash
python -m pip install -r requirements.txt
cdk synth -a "python -m infra.app"
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>   # ejecutar si es la primera vez
cdk deploy --all -a "python -m infra.app"
```

2) Probar localmente con ministack / localstack

Requisitos:
- `docker compose up -d` (usa `docker-compose.yml` incluido; el servicio `ministack` está definido)
- `aws` CLI instalado

Ejemplo (desde la raíz):

```bash
docker compose up -d ministack
scripts/deploy_ministack.sh
AWS_ENDPOINT=http://localhost:4566 python -m scripts.create_table
```

Notas:
- Los scripts incluidos son ejemplos. Ajusta nombres de funciones/handlers y permisos según necesites.
- Para pruebas rápidas también puedes invocar funciones localmente con
  `aws --endpoint-url http://localhost:4566 lambda invoke ...`.
