import boto3, os


def _table_name() -> str:
    return os.environ.get('ECOMMERCE_TABLE_NAME') or os.environ.get('TABLE_NAME', 'Ecommerce')

def get_table():
    resource = boto3.resource(
        'dynamodb',
        endpoint_url=os.environ.get('DYNAMODB_ENDPOINT_URL'),
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'local'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'local'),
    )
    return resource.Table(_table_name())