#!/usr/bin/env bash
set -euo pipefail

# Example script to synthesize and deploy the CDK stacks to AWS.
# Edit AWS account/region or run `cdk bootstrap` separately as needed.

echo "Activating virtualenv and installing Python deps..."
python -m pip install -r requirements.txt

echo "You should have the CDK CLI installed (npm i -g aws-cdk)."

echo "Synthesizing CDK app..."
cdk synth -a "python -m infra.app"

echo "Bootstrapping (if required)..."
echo "Run: cdk bootstrap aws://<ACCOUNT_ID>/<REGION>"

echo "Deploying stacks..."
cdk deploy --all -a "python -m infra.app" --require-approval never

echo "Done."
