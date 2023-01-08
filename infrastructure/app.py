import os

from pathlib import Path

from aws_cdk import App, Environment
from fastapi_iac.stack import ServerlessFastAPIStack


THIS_DIR = Path(__file__).parent
FAST_API_PACKAGE_DIR = THIS_DIR / "../rest-api"

# for development, use account/region from cdk cli
DEV_ENV = Environment(account=os.environ["AWS_ACCOUNT_ID"], region=os.getenv("AWS_REGION"))

APP = App()

ServerlessFastAPIStack(
    scope=APP,
    id="serverless-fastapi",
    # we don't have a frontend (yet)
    frontend_cors_url="ericriddoch.info",
    login_page_domain_prefix="serverless-fastapi-mlops-club",
    fastapi_code_dir=FAST_API_PACKAGE_DIR,
    env=DEV_ENV,
)

APP.synth()
