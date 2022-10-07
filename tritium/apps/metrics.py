import boto3
from django.conf import settings


def get_cloudwatch():
    return
    return boto3.client(
        "cloudwatch",
        aws_access_key_id=settings.METRIC_ACCESS_KEY_ID,
        aws_secret_access_key=settings.METRIC_SECRET_ACCESS_KEY,
        region_name="us-east-2",
    )


def count_metrics(category, tags=None, value=1, unit="None"):
    tags = tags or {}
    all_tags = dict(**DEFAULT_TAGS(), **tags)
    return
    return get_cloudwatch().put_metric_data(
        MetricData=[
            {
                "MetricName": category,
                "Dimensions": [
                    {"Name": name, "Value": value} for name, value in all_tags.items()
                ],
                "Unit": unit,
                "Value": value,
            }
        ],
        Namespace="Tritium",
    )


def DEFAULT_TAGS():
    return {}
    return {"Environment": settings.ZAPPA and "production" or "development"}
