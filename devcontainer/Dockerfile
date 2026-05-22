FROM node:22-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv curl git \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g aws-cdk serverless \
    && python3 -m pip install --break-system-packages --no-cache-dir awscli boto3 aws-cdk-lib constructs

WORKDIR /workspace

CMD ["sleep", "infinity"]