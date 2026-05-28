from aws_cdk import RemovalPolicy, Stack, CfnOutput, aws_dynamodb as dynamodb
from constructs import Construct


class PersistenceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.table = dynamodb.Table(
            self,
            "EcommerceTable",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK",      type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        self.table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(name="GSI1PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="GSI1SK", type=dynamodb.AttributeType.STRING),
        )
        CfnOutput(self, "TableName", value=self.table.table_name)
