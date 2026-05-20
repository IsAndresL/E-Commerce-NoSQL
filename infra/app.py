from aws_cdk import App, Environment

from infra.api_stack import ApiStack
from infra.core_stack import CoreStack
from infra.persistence_stack import PersistenceStack

# Cuenta dummy para LocalStack/ministack — CDK la requiere para resolver el entorno
env = Environment(account="000000000000", region="us-east-1")

app = App()

core = CoreStack(app,        "EcommerceCore",        env=env)
persistence = PersistenceStack(app, "EcommercePersistence", env=env)
api = ApiStack(app,         "EcommerceApi",         env=env, persistence_table=persistence.table)

app.synth()