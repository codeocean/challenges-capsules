# hash:sha256:449c9bec5cea95f7e9d447d57f7720decdc7cd0d88a0e669e814432c4cdb4ba3
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_USE_BEDROCK=1
ENV AWS_REGION=us-east-1

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
