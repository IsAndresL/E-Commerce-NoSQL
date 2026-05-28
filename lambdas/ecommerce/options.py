from lambdas.handler import HEADERS


def lambda_handler(event, context):
    return {"statusCode": 204, "headers": HEADERS, "body": ""}
