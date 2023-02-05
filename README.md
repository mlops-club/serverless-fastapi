# serverless-fastapi

![](./docs/openapi.png)

References:

1. AWS-themed GitHub Pages marketing page: https://aws-otel.github.io/
2. AWS Lambda Python setup: https://aws-otel.github.io/docs/getting-started/lambda/lambda-python

Example `event` passed from the API Gateway to the lambda:

```python
{
    "resource": "/{proxy+}",
    "path": "/openapi.json",
    "httpMethod": "GET",
    "headers": {
        "Accept": "application/json,*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.8",
        "CloudFront-Forwarded-Proto": "https",
        "CloudFront-Is-Desktop-Viewer": "true",
        "CloudFront-Is-Mobile-Viewer": "false",
        "CloudFront-Is-SmartTV-Viewer": "false",
        "CloudFront-Is-Tablet-Viewer": "false",
        "CloudFront-Viewer-ASN": "21928",
        "CloudFront-Viewer-Country": "US",
        "Host": "n8484inss8.execute-api.us-west-2.amazonaws.com",
        "Referer": "https://n8484inss8.execute-api.us-west-2.amazonaws.com/prod/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Via": "2.0 ec99de6a8df96b4e008b942ab98e6594.cloudfront.net (CloudFront)",
        "X-Amz-Cf-Id": "kQzO9p3DMD3ncxkO4iPqRzen6HhIk8Y-oAUMgnwL06XZ1MLQMkBMWA==",
        "X-Amzn-Trace-Id": "Root=1-63dd9630-1f7ec6c948e660f220ef3c92",
        "X-Forwarded-For": "172.59.153.63, 64.252.130.90",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https",
    },
    "multiValueHeaders": {
        "Accept": ["application/json,*/*"],
        "Accept-Encoding": ["gzip, deflate, br"],
        "Accept-Language": ["en-US,en;q=0.8"],
        "CloudFront-Forwarded-Proto": ["https"],
        "CloudFront-Is-Desktop-Viewer": ["true"],
        "CloudFront-Is-Mobile-Viewer": ["false"],
        "CloudFront-Is-SmartTV-Viewer": ["false"],
        "CloudFront-Is-Tablet-Viewer": ["false"],
        "CloudFront-Viewer-ASN": ["21928"],
        "CloudFront-Viewer-Country": ["US"],
        "Host": ["n8484inss8.execute-api.us-west-2.amazonaws.com"],
        "Referer": ["https://n8484inss8.execute-api.us-west-2.amazonaws.com/prod/"],
        "sec-fetch-dest": ["empty"],
        "sec-fetch-mode": ["cors"],
        "sec-fetch-site": ["same-origin"],
        "sec-gpc": ["1"],
        "User-Agent": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        ],
        "Via": ["2.0 ec99de6a8df96b4e008b942ab98e6594.cloudfront.net (CloudFront)"],
        "X-Amz-Cf-Id": ["kQzO9p3DMD3ncxkO4iPqRzen6HhIk8Y-oAUMgnwL06XZ1MLQMkBMWA=="],
        "X-Amzn-Trace-Id": ["Root=1-63dd9630-1f7ec6c948e660f220ef3c92"],
        "X-Forwarded-For": ["172.59.153.63, 64.252.130.90"],
        "X-Forwarded-Port": ["443"],
        "X-Forwarded-Proto": ["https"],
    },
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": {"proxy": "openapi.json"},
    "stageVariables": None,
    "requestContext": {
        "resourceId": "rpy2e8",
        "resourcePath": "/{proxy+}",
        "httpMethod": "GET",
        "extendedRequestId": "fyRnmEIvPHcFmIg=",
        "requestTime": "03/Feb/2023:23:18:08 +0000",
        "path": "/prod/openapi.json",
        "accountId": "643884464387",
        "protocol": "HTTP/1.1",
        "stage": "prod",
        "domainPrefix": "n8484inss8",
        "requestTimeEpoch": 1675466288419,
        "requestId": "2bfe1913-eea8-48de-b643-166b53428586",
        "identity": {
            "cognitoIdentityPoolId": None,
            "accountId": None,
            "cognitoIdentityId": None,
            "caller": None,
            "sourceIp": "172.59.153.63",
            "principalOrgId": None,
            "accessKey": None,
            "cognitoAuthenticationType": None,
            "cognitoAuthenticationProvider": None,
            "userArn": None,
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "user": None,
        },
        "domainName": "n8484inss8.execute-api.us-west-2.amazonaws.com",
        "apiId": "n8484inss8",
    },
    "body": None,
    "isBase64Encoded": False,
}

```

## Notes

### `uvicorn` problem

`opentelemetry-instrument -- uvicorn ...` fails to autoinstrument our app.

[This GitHub issue](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/385) says that it's an issue with how uvicorn starts workers. Uvicorn starts new processes. The uvicorn main
process gets instrumented, but the new child processes containing our FastAPI application code don't end up getting
instrumented.

I verified that I could make instrumenting work by adding the autoinstrumentation lines of code for
logging directly in our code files. So manual instrumentation works to an extent with `uvicorn`. To get around
this issue, I switched the `Dockerfile` to use `gunicorn` instead. That fixed the issue.

This should be fine, we use `gunicorn` in production. Also, `gunicorn` won't even be used for production in this case,
as we'll be using AWS Lambda. As long as autoinstrumentation works in AWS Lambda as well, we can be confident that
we can deploy our app in Docker with `gunicorn` or on AWS Lambda with the OTel AWS distro without having to modify
our code.

### Structured logging

AWS likes it when you use `json.dumps()` on python dicts when inserting them in log statements.

You might to a statement like

```python
import json
logger.info("This is a log statement with a jsonified dict %s", json.dumps({"key": "value"}))
```

The key-value pairs in the dict will become structured and searchable via CloudWatch logs.
The builtin AWS log fields are usually `@message` and the others you can see in this screenshot:

![xray](./docs/correlated-logs.png)
