# serverless-fastapi

![](./docs/openapi.png)

References:

1. AWS-themed GitHub Pages marketing page: https://aws-otel.github.io/
2. AWS Lambda Python setup: https://aws-otel.github.io/docs/getting-started/lambda/lambda-python
3. OpenTelemetry Python autoinstrumentation [PyPI page](https://pypi.org/project/opentelemetry-instrumentation/)
4. [Sample AWS ADOT-instrumented Flask API app](https://github.com/aws-observability/aws-otel-python/tree/main/integration-test-apps/auto-instrumentation/flask)

## Notes

### License

Talk about the common licenses.

Risk: people could take your code without crediting you and profit from it. Or potentially claim that they authored it.

Desire: You may want to allow certain types of access, maybe requesting attribution.

When you are writing commercial software, licenses matter extra, you don't want to get your company in trouble for stealing code. Could talk about the controversy of GitHub Copilot.

### CI and Code Review

- Define Code Review, integration, continuous integration, Peer review, Pull reqeust
  - Human attention is extremely valuable! Don't waste it on anything a machine can review for you. This point should be extra clear because by this time, we should have discussed how the PR process slows teams down in the first place, and pair programming is the ideal.

- Maybe we should show the DevOps infinity visualization

- It'd be great to cover different badges as we go:
  - shields.io
  - build passing / failing (GitHub actions), azure, circle, etc. have this too
  - pre-commit has a service
  - test coverage; coverage umbrella vendor. Talk about how GitHub apps vend: usually make it free to use and charge for commercial/private software

- It could be good to talk about common "bots" like:
  - dependabot
  - all contributors

- We should have a section on security scanning. Discuss the types of vulerabilities: supply chain, sshgit, exploits, etc. 
  - Discuss how to pick dependencies: the snyk package index
  - Some companies only allow you to use a pre-approved list of packages, or even pre-approved versions, which they may enforce by vending to an internal PyPI server
  - Private PyPI server

### Poetry

Very complete [pyproject.toml](https://github.com/rstcheck/rstcheck/blob/main/pyproject.toml) file

Also the `rich` 

#### Python packaging history

The history of Python packaging is long and complicated. And python to an early python three, the python standard library had a Library called distutils. The point of this library wants to provide a standard way of sharing python code. Python packages generally need a few things. They need a way to specify dependencies, they need a way to specify versions, and it's nice if they can specify metadata like who the author is and what get out the repository is associated with the cove base. The library also provided a way to include assets such as binaries, images, Jason files, etc.

The problem with this details is that it was very hard to use. The distribution utilities library was part of the python standard library, but it was a pain to use. So the community responded with an abstraction over distribution utilities call to set up tools. Set up tools was never made part of the python standard library. However, set up tools was so easy to use became much more popular than a built in distribution utilities library. Python maintainer saw that set up tools provided a much better packaging experience for Python users than just details did. So, although set up tools was not part of the official python standard library, I Python maintainers declared that set up tools was the officially recommended way of packaging python code into a shareable form. Today, if you go to the official Python documentation,
 you will find packaging instructions using set up tools to create packages from Python code.

Despite set up tools being easier to use than distribution utilities, many still found it very difficult to use. Beginners and professionals alike found that difficult troubleshooting was almost always necessary whenever they were adding intermediate to advanced packaging features to the package. For example, the manner in which you add binaries to python package using set up tools is by writing a file calle manifest dot in. In addition to writing this file, you must also add some special configuration. This is an notoriously difficult process to get right. Mini project packaging templates are available online do you help beginners get set up tools working correctly. While these templates work, they are difficult to modify or fully understand, because of how complicated they are.

Python maintainers acknowledge that set up tools was not satisfying the needs of certain python users. There was also a interesting problem faced by package authors that had to do with running isolated builds to separate package dependencies from build time dependencies. In response to both of these issues, the Python maintainers authored a PEP proposal from which a tool called build was created. Since set up tools was a third-party packaging tool, in theory nothing should stop other groups from creating other third-party packaging tools that did the same job. The PEP proposal for build defined a standard for building build back ends which could be used to build python distributions such as source distributions and wheels. Command line tool called build emerged from this. The build command line tool is capable of building any python package using a valid build back end. Some popular build Backends include poetry, Hatch, and flit. Of those three options, poetry is by far the most popular.

`pipx` and `fastapi` use `hatch`. Never seen a project using `flit`.

[PEP 621](https://peps.python.org/pep-0621/#example) defines a standard
way of putting `setup.cfg` info directly into `pyproject.toml`. It doesn't look like
`poetry` uses this format... does the `hatchling` engine? [Setuptools has adopted
the format](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html), so we could use this at work.

The Python Packaging Authority (PyPA) is a working group that maintains a core set of software projects used in Python packaging.
The PyPA publishes the P[ython Packaging User Guide](https://packaging.python.org/en/latest/), which is the authoritative resource on how to package, publish, and install Python projects using current tools. 

#### `.ini` and `.toml`

`.ini` is awful! But the stdlib had `ConfigParser`. As of [PEP 680](https://peps.python.org/pep-0680/) in Jan 2022, `tomllib` is part of the standard library. This goes nicely with `PEP 621` which defined the standard packaging metadata format in `pyproject.toml`.


#### Building and installing poetry packages

Build a package:

1. fill out `pyproject.toml`; set the `build-backend`
2. `pipx --spec build --wheel --sdist ./path/to/package`

You can also just install the package as normal with:

1. `pip install ./path/to/package/[some,extras]`

So cool! The end users are completely unaffected by the fact that our build backend might be poetry.

### Canary deployments

AWS has a [canary deployment with CDK workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/5195ab7c-5ded-4ee2-a1c5-775300717f42/en-US). 

### Metrics

- We can log metrics to the console. We can also send metrics to the otel collector. The otel collector then
  logs the metrics to the console, but in EMF format (since that's what the awsemf exporter does).


Code emits metric -> otlp collector -> prometheus, console, cloudwatch log stream in EMF format
Code emits trace -> otlp collector -> x-ray, console
Code emits log -> otlp collector -> cloudwatch log group

The use should be walked through how the OTLP collector works. It uses

- receivers
- processors
- exporters
- services
- extensions

^^^ Great (official) [docs on all this](https://opentelemetry.io/docs/collector/configuration/)

- It can support multiple backends for each
  - metrics: prometheus
  - traces: x-ray, jaeger, zipkin, tempo
  - logs: cloudwatch, splunk, elastic, kafka, file, loki.
- Logs also use the docker log driver. Where does that fit in? Does a OTEL log driver
  have to batch logs at the service? Maybe logs don't need to be send to the OTLP collector.
  As long as the logs have the trace IDs, they can be correlated in the final destination.
- If EMF format is used for metrics, maybe we don't have to send metrics to the OTLP collecor...
  except, if we use the opentelemetry SDK, our metrics are probably in OTLP format (somehow), not EMF,
  so they would need to be sent to the OTLP collector to then be "exported" in the right format

Lambda extensions
- This [ADOT Lambda design spec](https://github.com/open-telemetry/opentelemetry-lambda/blob/main/docs/design_proposal.md) shows
  that the ADOT lambda extension is literally the OTLP collector running as a separate process inside of the lambda container.
  So your function executes alongside it and proactively sends metrics to it.
- This is [the blogpost announcing Lambda extensions](https://aws.amazon.com/blogs/aws/getting-started-with-using-your-favorite-operational-tools-on-aws-lambda-extensions-are-now-generally-available/). NewRelic, DataDog, and ADOT are all here.
- Lambda extensions make your functions more expensive. The [Lambda pricing page](https://aws.amazon.com/lambda/pricing/) has this callout:

  > Duration charges apply to code that runs in the handler of a function as well as initialization code that is declared outside of the handler. For Lambda functions with AWS Lambda Extensions, duration also includes the time it takes for code in the last running extension to finish executing during shutdown phase. For more details, see the Lambda Programming Model documentation.

  So it's not as though the extension is doubling the cost of the function. It may it some cases. You only pay for time
  it takes for the extension to shut down, since the lambda runtime can't stop until your code and all extensions have stopped. 
  Hopefully that's not too long.

### Not covered

If you want to learn more about:

- Docker
- FastAPI
- git/GitHub/GitHub Actions
- AWS
- CloudFormation
- Linux/bash

Take additional courses on them and/or *build something*. This course will explain the way we use these things
enough to give context. A beginner should be able to follow along line-by-line and understand the role each tool
plays, but this course won't be a deep dive on those topics.

Expect this course to deep dive on:

- Concepts of deploying and monitoring production software
- 

### Course Announcement

Potential name: "Foundations for MLOps on AWS: deploying and managing software in production"

Target audience: people who know Python and would like to learn how to "ship" production software using AWS.



We'll use the free-tier services here to



- write a production-ready REST API with FastAPI

- test the code with unit testing, and the scalability with load testing

- deploy it with infrastructure as code (AWS CDK) as we would in a production setting

- monitor it with logs, traces, metrics, dashboards, and alerts

- update it 

- cheaply start small (with AWS Lambda), cheaply scale up (with Docker containers) 

- continuous integration, continuous delivery, and continuous deployment using GitHub Actions



### AWS Free Tier

Table of these images with labels of AWS services. 2 images in each row.

|                                                       |                                                         |
| ----------------------------------------------------- | ------------------------------------------------------- |
| ![](./docs/free-tier/cloudtrail.png) <br/> CloudTrail | ![](./docs/free-tier/cloudwatch.png) <br/> CloudWatch   |
| ![](./docs/free-tier/cloudfront.png) <br/> CloudFront | ![](./docs/free-tier/lambda.png) <br/> Lambda           |
| ![](./docs/free-tier/x-ray.png) <br/> X-Ray           | ![](./docs/free-tier/s3.png) <br/> S3                   |
| ![](./docs/free-tier/cognito.png) <br/> Cognito       | ![](./docs/free-tier/api-gateway.png) <br/> API Gateway |




### IaC advantages

- Free tier: delete your account and redeploy your whole app in a new one
  - renewed 15-30 day free tier
  - renewed 12-month free tier
- Deploy apps in an identical way: hook up all your REST APIs with monitoring, alerts, cost saving architecture, security, etc.
- Easy consistent tagging strategy, great for tracking costs, which developer created something, which app each resource is part of, etc.
- Automated deploys: continuous deployment
- Complete teardown: save money by cleaning up every resource associated with an entire, complex app
- State management: 10 resources could have (10 choose 0) + (10 choose 1) + ... + (10 choose 10) possible created/not-created states
  not to mention the individual attributes
- Your account doesn't become a mess, especially if you are sharing it with other developers. Story of how BEN's
  `ben-ai-development` account became a production account. Story of Steve deleting his personal S3 bucket which
  turned out to have production data in it by the time he deleted it.
- Abstraction: deploy apps with constructs like `ApplicationLoadBalancedFargateService` and `s3.Bucket(auto_delete=True)`
  which creates a lambda function. Talk about those lambda functions. Quickly create complex infrastructures you would
  otherwise spend weeks designing. Learn cloud architecture years faster than it used to take senior engineers.

### API Gateway

I got these metrics when I set `metrics_enabled=True`.

![](./docs/api-gateway-metrics.png)

And this when I set `tracing_enabled=True`. Before setting this to `True`, we saw the same visualization, but
the API Gateway component was missing.

![](./docs/api-gateway-trace.png)

```python
self._api = apigw.RestApi(
    self,
    f"-RestApi",
    deploy_options=apigw.StageOptions(
        stage_name=DEFAULT_STAGE_NAME,
        metrics_enabled=True,
        tracing_enabled=True,
        description="Production stage",
        throttling_burst_limit=10,
        throttling_rate_limit=2,
    ),
    description="Serverless FastAPI",
)
```

### Instrumentation

Good resource:

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

### Custom choices

Any custom choices you make for your app are BAD!

- Logging format
- Generating request ID, what to call that header

You want as many apps in your group/company to use the same standards as possible.

### Course presentation

MLOps is a combination of Software Development, DevOps, ML Engineering, and Data Engineering.

This course will give lots of good exposure to Software Development and DevOps, and attempt
to include ML Engineering examples (like when you need to keep track of RAM, say ways
a ML service could crash due to the problems typical services run into).

Show a heirarchy of needs?

- Code
- Deployment
- Training, re-training, and special deployment steps for MLOps (not covered here)
- Monitoring afterward
- ML-specific Monitoring (not covered here)

Talk about logs, traces, metrics, dashboards, alerts.

### Badges

Could do a quick tangent on https://shields.io/ when we make the FastAPI docs description.

### API Gateway

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