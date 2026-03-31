# hash:sha256:7017dfd789ae3f0fdb4f6ace10be9c5ce6e58b9fa8f5fb67db207a7b104c018c
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    boto3==1.42.77 \
    gitpython==3.1.46 \
    pytest==9.0.2 \
    tqdm==4.67.3

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
