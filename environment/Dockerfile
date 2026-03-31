# hash:sha256:b9877cbfe6b893987e73b2b5199ffc2639971f0d030fed51f6aae6d98f6615e3
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    anndata==0.11.4 \
    mlcroissant==1.0.22 \
    numpy==2.2.6 \
    pandas==2.3.3

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
