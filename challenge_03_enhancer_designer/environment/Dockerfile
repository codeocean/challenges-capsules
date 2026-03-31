# hash:sha256:9eed08cf5a47a4f8dee5b4ed63322736a02a1a12d77928fb94af805f46a0f0d0
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000

RUN pip install -U --no-cache-dir \
    biopython==1.86 \
    matplotlib==3.10.8 \
    numpy==2.2.6 \
    scipy==1.15.3 \
    torch==2.11.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
