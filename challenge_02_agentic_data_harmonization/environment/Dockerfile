# hash:sha256:201af48093e3f10e4abf187ef4faa65467de1c1e573e1ea54a97ec0a63639d27
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    boto3==1.42.78 \
    pandas==2.3.3 \
    pronto==2.7.3 \
    rapidfuzz==3.14.3 \
    requests==2.33.1 \
    strands-agents==1.33.0 \
    strands-agents-tools==0.3.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
