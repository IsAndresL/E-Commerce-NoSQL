from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import Stack
from constructs import Construct


class PersistenceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Simple DynamoDB table for ecommerce
        self.table = dynamodb.Table(
            self,
            "EcommerceTable",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            removal_policy=dynamodb.RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
