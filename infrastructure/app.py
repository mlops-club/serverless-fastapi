import os
from pathlib import Path

from aws_cdk import App, Environment, Tags
from fastapi_iac.stack import ServerlessFastAPIStack

THIS_DIR = Path(__file__).parent
FAST_API_PACKAGE_DIR = THIS_DIR / "../rest-api"

# for development, use account/region from cdk cli
DEV_ENV = Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.getenv("AWS_REGION"))

APP = App()

ServerlessFastAPIStack(
    scope=APP,
    construct_id="serverless-fastapi",
    # we don't have a frontend (yet)
    frontend_cors_url="https://ericriddoch.info",
    login_page_domain_prefix="serverless-fastapi",
    fastapi_code_dir=FAST_API_PACKAGE_DIR,
    enable_auth=False,
    env=DEV_ENV,
)

Tags.of(APP).add("organization", "mlops-club")
Tags.of(APP).add("project", "serverless-fastapi")
Tags.of(APP).add("created-with", "awscdk-python")

APP.synth()
