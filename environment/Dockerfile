# hash:sha256:6c2d15d160ddc43876cf1c3cef11e043ac989fb996e82c891abfa8b165524dcf
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_USE_BEDROCK=1
ENV AWS_REGION=us-east-1
ENV DISABLE_PROMPT_CACHING=1
ENV ANTHROPIC_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0

RUN pip install -U --no-cache-dir \
    biopython==1.86 \
    boto3==1.42.77 \
    matplotlib==3.10.8 \
    numpy==2.4.3 \
    pandas==3.0.1

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
