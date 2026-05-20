from aws_cdk import App

from infra.api_stack import ApiStack
from infra.core_stack import CoreStack
from infra.persistence_stack import PersistenceStack

app = App()

# Core infra (VPCs, roles, etc.)
core = CoreStack(app, "EcommerceCore")

# Persistence (DynamoDB, Redis emulation bindings)
persistence = PersistenceStack(app, "EcommercePersistence")

# API stack (Lambdas + API Gateway)
api = ApiStack(app, "EcommerceApi", persistence_table=persistence.table)

app.synth()
