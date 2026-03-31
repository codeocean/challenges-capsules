# hash:sha256:378c43ff1089810031c1c34410a9b47eb87887b839788acd2474b1d7ddd5eb84
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
    pyarrow==23.0.1 \
    pydantic==2.12.5

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
