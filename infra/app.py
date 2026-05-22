from aws_cdk import App, Environment

from infra.stack.lambda_stack import LambdaStack
from infra.stack.persistence_stack import PersistenceStack

# Cuenta dummy para LocalStack/ministack — CDK la requiere para resolver el entorno
app = App()

persistence = PersistenceStack(app, "EcommercePersistence")
api = LambdaStack(app, "EcommerceLambda", dynamo_table=persistence.table, redis_host="redis", redis_port="6379")

app.synth() 