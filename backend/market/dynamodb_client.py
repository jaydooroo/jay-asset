from __future__ import annotations

from .config import aws_region, dynamodb_endpoint_url


def dynamodb_resource():
    """
    Return a DynamoDB resource for either AWS or DynamoDB Local.

    If MARKET_DYNAMODB_ENDPOINT_URL is set, boto3 talks to that endpoint. This
    lets local development use DynamoDB Local while deployed Lambda uses the
    real AWS service with the same repository code.
    """
    try:
        import boto3
        from botocore.config import Config
    except Exception as exc:  # pragma: no cover - depends on local/AWS runtime
        raise RuntimeError("boto3 is required for DynamoDB price storage") from exc

    kwargs = {
        "region_name": aws_region(),
        "config": Config(
            connect_timeout=3,
            read_timeout=10,
            retries={"max_attempts": 2},
        ),
    }
    endpoint_url = dynamodb_endpoint_url()
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url

        # DynamoDB Local accepts dummy credentials, but boto3 still wants values
        # unless the developer already has AWS credentials configured.
        kwargs["aws_access_key_id"] = "local"
        kwargs["aws_secret_access_key"] = "local"

    return boto3.resource("dynamodb", **kwargs)
