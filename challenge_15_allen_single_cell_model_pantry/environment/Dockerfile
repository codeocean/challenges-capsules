# hash:sha256:602e878e2251e689669d58ac99f96d8a96329480bc01701d73eb8da1d51ca8aa
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
ENV MAX_THINKING_TOKENS=10000
ENV ANTHROPIC_DEFAULT_SONNET_MODEL=
ENV ANTHROPIC_MODEL=
ENV BEDROCK_MODEL_ID=

RUN pip install -U --no-cache-dir \
    anndata \
    matplotlib \
    numpy \
    pandas \
    scanpy \
    scikit-learn \
    scvi-tools \
    torch \
    torchvision \
    transformers

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
