# hash:sha256:af3314e50602f19c8ea7f0fca43461829d02a68a5931f0a4002d385db8ae1802
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    boto3==1.42.77 \
    pydantic==2.12.5 \
    streamlit==1.55.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
