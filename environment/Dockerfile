# hash:sha256:5ffe23824d9a5c185ddeac7fcf40934cec20277f0ffff52e4689d8cc5c3ca542
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    pandas==2.3.3 \
    pronto==2.7.3 \
    rapidfuzz==3.14.3 \
    requests==2.33.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
