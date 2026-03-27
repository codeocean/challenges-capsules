# hash:sha256:883e3fc1f23f509f665ab127e06502b765728efd353673b4d1a0b00f6d52ab9a
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_USE_BEDROCK=1
ENV AWS_REGION=us-east-1
ENV DISABLE_PROMPT_CACHING=1
ENV ANTHROPIC_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0

RUN pip install -U --no-cache-dir \
    boto3==1.42.77 \
    gitpython==3.1.46 \
    pytest==9.0.2 \
    tqdm==4.67.3

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
