import json


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "products handler OK",
            "event": event,
        }),
    }
