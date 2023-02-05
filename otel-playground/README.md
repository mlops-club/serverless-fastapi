Install:

`pip install opentelemetry-distro opentelemetry-exporter-otlp`

Detect which libraries you might want to instrument:

```text
usage: opentelemetry-bootstrap [-h] [--version] [-a {install,requirements}]

opentelemetry-bootstrap detects installed libraries and automatically installs the relevant instrumentation packages for
them.

optional arguments:
  -h, --help            show this help message and exit
  --version             print version information
  -a {install,requirements}, --action {install,requirements}
                        install - uses pip to install the new requirements using to the currently active site-package.
                        requirements - prints out the new requirements to stdout. Action can be piped and appended to a
                        requirements.txt file.
```

```bash
$ opentelemetry-bootstrap -a requirements

opentelemetry-instrumentation-aws-lambda==0.36b0
opentelemetry-instrumentation-dbapi==0.36b0
opentelemetry-instrumentation-logging==0.36b0
opentelemetry-instrumentation-sqlite3==0.36b0
opentelemetry-instrumentation-urllib==0.36b0
opentelemetry-instrumentation-wsgi==0.36b0
opentelemetry-instrumentation-boto3sqs==0.36b0
opentelemetry-instrumentation-botocore==0.36b0
opentelemetry-instrumentation-fastapi==0.36b0
opentelemetry-instrumentation-grpc==0.36b0
opentelemetry-instrumentation-jinja2==0.36b0
opentelemetry-instrumentation-requests==0.36b0
opentelemetry-instrumentation-tortoiseorm==0.36b0
opentelemetry-instrumentation-urllib3==0.36b0
```

`opentelemetry-bootstrap -a install` would not only detect, but install these ^^^.
