# hash:sha256:c2cf541c562b248a9ac6c10072650e8f44d6798340bdbaafb3a2cd4d3c3f2c98
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
    biopython==1.86 \
    matplotlib==3.10.8 \
    numpy==2.2.6 \
    scipy==1.15.3 \
    torch==2.11.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
