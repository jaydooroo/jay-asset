import awsgi
from app import app
from urllib.parse import parse_qs


def _normalize_event(event: dict) -> dict:
    """
    awsgi expects an API Gateway REST API (payload v1.0) shaped event.

    - Some test events omit `queryStringParameters` entirely.
    - API Gateway HTTP API / Lambda Function URL (payload v2.0) uses different keys.

    This function normalizes common cases into a v1-like shape so awsgi can build
    a WSGI environ without KeyError.
    """
    if not isinstance(event, dict):
        return event

    # API Gateway REST API (v1.0) style
    if "httpMethod" in event and "path" in event:
        event.setdefault("queryStringParameters", None)
        event.setdefault("headers", None)
        return event

    # API Gateway HTTP API / Lambda Function URL (v2.0) style
    request_context = event.get("requestContext") or {}
    rc_http = request_context.get("http") or {}

    if event.get("version") == "2.0" or rc_http:
        method = rc_http.get("method") or "GET"
        path = event.get("rawPath") or rc_http.get("path") or "/"

        qsp = event.get("queryStringParameters")
        if qsp is None:
            raw_qs = event.get("rawQueryString") or ""
            parsed = parse_qs(raw_qs, keep_blank_values=True)
            qsp = {k: (v[-1] if v else "") for k, v in parsed.items()} or None

        return {
            "httpMethod": method,
            "path": path,
            "headers": event.get("headers") or {},
            "queryStringParameters": qsp,
            "body": event.get("body"),
            "isBase64Encoded": event.get("isBase64Encoded", False),
            "requestContext": request_context,
        }

    # Unknown shape: best-effort to avoid awsgi KeyErrors.
    event.setdefault("queryStringParameters", None)
    event.setdefault("headers", None)
    event.setdefault("httpMethod", "GET")
    event.setdefault("path", "/")
    return event


def handler(event, context):
    """AWS Lambda handler that translates API Gateway events to Flask"""
    return awsgi.response(app, _normalize_event(event), context)
