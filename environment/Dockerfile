# hash:sha256:bd469aa4f98557c8e0b80d595209e6274594ee79ac28e675035e4f6cbde1eb22
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    boto3==1.42.77 \
    numpy==2.2.6 \
    pandas==2.3.3 \
    pydantic==2.12.5 \
    requests==2.33.0 \
    tqdm==4.67.3

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
