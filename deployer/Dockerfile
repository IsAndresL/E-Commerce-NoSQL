FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3 python3-venv python3-pip \
       zip unzip curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv "$VIRTUAL_ENV" \
    && "$VIRTUAL_ENV/bin/pip" install --upgrade pip setuptools wheel

WORKDIR /app

COPY . /app

RUN pip install -r infra/requirements.txt \
    && pip install awscli \
    && npm install -g aws-cdk

ENTRYPOINT ["/bin/sh", "-lc"]

CMD ["/bin/sh", "-c", "tail -f /dev/null"]